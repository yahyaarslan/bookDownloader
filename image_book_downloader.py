import re
import requests
from PIL import Image, UnidentifiedImageError
from fpdf import FPDF
from io import BytesIO
import os
import shutil
from concurrent.futures import ThreadPoolExecutor


# Context manager for handling temporary directory
class TempDirectory:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        os.makedirs(self.path, exist_ok=True)
        return self.path

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.path)


def download_image(url, image_path):
    try:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        image.save(image_path)
        return image_path
    except (requests.exceptions.RequestException, IOError, UnidentifiedImageError) as e:
        print(f"Error occurred: {e}")


# Read and format the URLs in a single step
print("Formatting URLs...")
with open("unformatted_links.txt", "r") as file:
    urls = [url.rstrip("',") for url in re.findall(r"https?://[^\s]+", file.read())]

images = []

# Use context manager for images directory
with TempDirectory("images") as dirpath:
    # Create a PDF object
    pdf = FPDF()

    # Download each image concurrently, process it, and add it to the PDF
    print("Downloading images...")
    with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust max_workers as needed
        futures = []
        for i, url in enumerate(urls):
            image_path = f"{dirpath}/image{i}.jpg"
            futures.append(executor.submit(download_image, url, image_path))

        for future in futures:
            image_path = future.result()
            if image_path:
                # Add the image to the PDF
                pdf.add_page()
                pdf.image(image_path, x=0, y=0, w=pdf.w, h=pdf.h)

    # Write the PDF to a file
    print("Writing PDF...")
    pdf.output("output.pdf", "F")

# Upload to iLovePDF or similar compression service
# ...
