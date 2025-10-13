from google_images_download import google_images_download  

response = google_images_download.googleimagesdownload()  

arguments = {
    "keywords": "train crowd inside carriage",
    "limit": 300,
    "print_urls": True,
    "output_directory": "dataset/train_interior"
}  

paths = response.download(arguments)
print(paths)
