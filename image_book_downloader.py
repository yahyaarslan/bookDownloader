import re
import requests
from PIL import Image, UnidentifiedImageError
from fpdf import FPDF
from io import BytesIO
import os
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory

def download_image(url):
    try:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        image_bytes = BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)  # Move the cursor to the beginning of the BytesIO object
        return image_bytes
    except (requests.exceptions.RequestException, IOError, UnidentifiedImageError) as e:
        print(f"Error occurred: {e}")
        return None

# Read and format the URLs
print("Formatting URLs...")
with open("links.txt", "r") as file:
    urls = [url.rstrip("',") for url in re.findall(r"https?://[^\s]+", file.read())]

# Create a PDF object
pdf = FPDF()

# Temporary directory to store images
with TemporaryDirectory() as temp_dir:
    # Download each image concurrently, process it, and add it to the PDF
    print("Downloading images...")
    with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust max_workers as needed
        futures = [executor.submit(download_image, url) for url in urls]

        for i, future in enumerate(futures):
            image_bytes = future.result()
            if image_bytes:
                # Save the image to a temporary file
                temp_path = os.path.join(temp_dir, f'image_{i}.jpg')
                with open(temp_path, 'wb') as f:
                    f.write(image_bytes.getbuffer())
                
                # Add the image to the PDF
                pdf.add_page()
                pdf.image(temp_path, x=0, y=0, w=pdf.w, h=pdf.h)

# Write the PDF to a file
print("Writing PDF...")
pdf.output("output.pdf", "F")
