#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Optional

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
LABEL_EXT = ".txt"

@dataclass
class LabelIssue:
    kind: str
    message: str

@dataclass
class FileReport:
    image_path: Optional[Path] = None
    label_path: Optional[Path] = None
    has_label: bool = False
    issues: List[LabelIssue] = field(default_factory=list)
    objects: int = 0

def relative_stem(base: Path, p: Path) -> Path:
    """Return path of p relative to base, but without suffix (stem) preserving subfolders.
    Example: base=/a/images, p=/a/images/sub/x.jpg -> sub/x
    """
    rel = p.relative_to(base)
    return rel.with_suffix("")

def find_matching_label_path(images_dir: Path, labels_dir: Path, image_path: Path) -> Path:
    """Map an image path to its expected label path under labels_dir, preserving subfolders."""
    rel_stem = relative_stem(images_dir, image_path)
    return labels_dir.joinpath(rel_stem).with_suffix(LABEL_EXT)

def parse_label_line(line: str) -> Tuple[int, float, float, float, float]:
    parts = line.strip().split()
    if len(parts) != 5:
        raise ValueError(f"expected 5 values, got {len(parts)}")
    try:
        cls = int(float(parts[0]))  # robust to "0.0"
        x, y, w, h = map(float, parts[1:])
    except Exception as e:
        raise ValueError(f"failed to parse numbers: {e}")
    return cls, x, y, w, h

def validate_values(cls: int, x: float, y: float, w: float, h: float, nc: Optional[int]) -> List[LabelIssue]:
    issues: List[LabelIssue] = []
    # class range
    if nc is not None and not (0 <= cls < nc):
        issues.append(LabelIssue("class_range", f"class {cls} not in [0..{nc-1}]"))
    # normalized checks
    if x <= 0 or x >= 1 or y <= 0 or y >= 1:
        issues.append(LabelIssue("range_xy", f"x/y should be in (0,1): got x={x:.6f}, y={y:.6f}"))
    if w <= 0 or w > 1 or h <= 0 or h > 1:
        issues.append(LabelIssue("range_wh", f"w/h should be in (0,1]: got w={w:.6f}, h={h:.6f}"))
    # pixel-like detection
    if any(v > 2 for v in (x, y, w, h)):
        issues.append(LabelIssue("not_normalized", "values look like pixels, not normalized 0..1"))
    return issues

def scan(images_dir: Path, labels_dir: Path, nc: Optional[int]) -> Tuple[List[FileReport], Dict[str, int]]:
    reports: List[FileReport] = []
    # Map for found images
    image_files = [p for p in images_dir.rglob("*") if p.suffix.lower() in IMAGE_EXTS]
    image_stems = {relative_stem(images_dir, p): p for p in image_files}

    # Check each image for a label
    for stem, img_path in image_stems.items():
        rep = FileReport(image_path=img_path)
        lbl_path = labels_dir.joinpath(stem).with_suffix(LABEL_EXT)
        rep.label_path = lbl_path
        if lbl_path.exists():
            rep.has_label = True
            # Read label file
            try:
                text = lbl_path.read_text(encoding="utf-8").strip()
            except UnicodeDecodeError:
                text = lbl_path.read_text(encoding="latin-1").strip()
            if text == "":
                rep.issues.append(LabelIssue("empty_label", "label txt is empty"))
            else:
                lines = [ln for ln in text.splitlines() if ln.strip() != ""]
                rep.objects = 0
                for i, ln in enumerate(lines, 1):
                    try:
                        cls, x, y, w, h = parse_label_line(ln)
                        issues = validate_values(cls, x, y, w, h, nc)
                        rep.issues.extend(issues)
                        rep.objects += 1
                    except Exception as e:
                        rep.issues.append(LabelIssue("parse_error", f"line {i}: {e}"))
        else:
            rep.has_label = False
            rep.issues.append(LabelIssue("missing_label", "no matching label file"))
        reports.append(rep)

    # Orphan labels: txt without image
    orphan_count = 0
    for txt in labels_dir.rglob(f"*{LABEL_EXT}"):
        rel = relative_stem(labels_dir, txt)
        expected_img = None
        for ext in IMAGE_EXTS:
            candidate = images_dir.joinpath(rel).with_suffix(ext)
            if candidate.exists():
                expected_img = candidate
                break
        if expected_img is None:
            # Orphan
            orphan_rep = FileReport(image_path=None, label_path=txt, has_label=True)
            orphan_rep.issues.append(LabelIssue("orphan_label", "label has no matching image"))
            reports.append(orphan_rep)
            orphan_count += 1

    # Summary
    summary = {
        "total_images": len(image_files),
        "images_with_labels": sum(1 for r in reports if r.image_path and r.has_label),
        "images_missing_labels": sum(1 for r in reports if r.image_path and not r.has_label),
        "orphan_labels": orphan_count,
        "files_with_issues": sum(1 for r in reports if r.issues),
        "total_objects": sum(r.objects for r in reports),
    }
    return reports, summary

def write_csv(reports: List[FileReport], summary: Dict[str, int], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["image_path","label_path","has_label","objects","issue_kind","issue_message"])
        for r in reports:
            if r.issues:
                for iss in r.issues:
                    w.writerow([str(r.image_path or ""), str(r.label_path or ""), r.has_label, r.objects, iss.kind, iss.message])
            else:
                w.writerow([str(r.image_path or ""), str(r.label_path or ""), r.has_label, r.objects, "", ""])
        # Append summary
        w.writerow([])
        for k, v in summary.items():
            w.writerow([k, v])

def main(argv=None):
    p = argparse.ArgumentParser(description="Check YOLO labels against images (normalized format).")
    p.add_argument("--images", required=True, type=str, help="Root folder of images (recursively scanned).")
    p.add_argument("--labels", required=True, type=str, help="Root folder of labels (mirrored subfolders).")
    p.add_argument("--nc", type=int, default=None, help="Number of classes. If set, enforce class id in [0..nc-1].")
    p.add_argument("--report", type=str, default=None, help="Optional path to write CSV report.")
    args = p.parse_args(argv)

    images_dir = Path(args.images)
    labels_dir = Path(args.labels)
    if not images_dir.exists():
        print(f"[ERROR] Images folder not found: {images_dir}", file=sys.stderr)
        sys.exit(2)
    if not labels_dir.exists():
        print(f"[ERROR] Labels folder not found: {labels_dir}", file=sys.stderr)
        sys.exit(2)

    reports, summary = scan(images_dir, labels_dir, args.nc)

    # Console summary
    print("=== YOLO Label Check Summary ===")
    for k, v in summary.items():
        print(f"{k:>24}: {v}")

    # Top issues
    issues_count: Dict[str, int] = {}
    for r in reports:
        for iss in r.issues:
            issues_count[iss.kind] = issues_count.get(iss.kind, 0) + 1
    if issues_count:
        print("\nIssue breakdown:")
        for k, v in sorted(issues_count.items(), key=lambda kv: -kv[1]):
            print(f"  - {k}: {v}")

    # Save CSV
    if args.report:
        out_csv = Path(args.report)
        write_csv(reports, summary, out_csv)
        print(f"\n[OK] CSV report saved to: {out_csv.resolve()}")

if __name__ == "__main__":
    main()
