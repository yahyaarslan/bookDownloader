import re
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from concurrent.futures import ThreadPoolExecutor

def download_image(url):
    try:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        image_bytes = BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)
        return image_bytes
    except (requests.exceptions.RequestException, IOError, UnidentifiedImageError) as e:
        print(f"Error occurred: {e}")
        return None

def add_image_to_pdf(image_bytes, pdf_canvas, page_width, page_height):
    image = Image.open(image_bytes)
    image_width, image_height = image.size
    aspect = image_height / float(image_width)
    
    # Calculate the dimensions of the image to fit the page
    if aspect > 1:
        # Image is taller than wide, fit to height
        new_height = page_height
        new_width = new_height / aspect
    else:
        # Image is wider than tall, fit to width
        new_width = page_width
        new_height = new_width * aspect
    
    # Center the image on the page
    x = (page_width - new_width) / 2
    y = (page_height - new_height) / 2
    
    # Use ImageReader to read the image from bytes and draw it on the canvas
    image_reader = ImageReader(BytesIO(image_bytes.getvalue()))
    pdf_canvas.drawImage(image_reader, x, y, new_width, new_height)

# Read and format the URLs
print("Formatting URLs...")
with open("links.txt", "r") as file:
    urls = [url.rstrip("',") for url in re.findall(r"https?://[^\s]+", file.read())]

# Create a PDF canvas
output_pdf = BytesIO()
pdf_canvas = canvas.Canvas(output_pdf, pagesize=letter)
page_width, page_height = letter

# Download each image concurrently, process it, and add it to the PDF
print("Downloading images...")
with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust max_workers as needed
    futures = [executor.submit(download_image, url) for url in urls]

    for future in futures:
        image_bytes = future.result()
        if image_bytes:
            # Add a new page and then add the image to the PDF
            pdf_canvas.showPage()
            add_image_to_pdf(image_bytes, pdf_canvas, page_width, page_height)

# Finalize the PDF
print("Writing PDF...")
pdf_canvas.save()

# Move to the beginning of the BytesIO buffer to write it out
output_pdf.seek(0)
with open("output.pdf", "wb") as f:
    f.write(output_pdf.getbuffer())
