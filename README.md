# ImageBookDownloader

This tool downloads books that are listed as images, typically hosted on an ebook reader website. It should only be used for legally purchased books.

## Installation

Install the required Python packages with pip:

```bash
pip install requests Pillow fpdf
```

## Usage

1. Open the online book in your browser. Open the browser's inspect tool. Search for "images", and select the occurrence that contains all image links.

2. Copy these links into a text file named "unformatted_links.txt" in the same directory as this script. Remove any unnecessary links. The script will strip out the URLs, so there's no need to format them.

3. Run the script with Python:

```bash
python image_book_downloader.py
```

This will create an "output.pdf" file in the same directory.

4. (Optional) If you want to compress the PDF, you can upload it to a service like [iLovePDF](https://www.ilovepdf.com/compress_pdf).

## Limitations
+ Large PDF files consume large memory, mainly a bootleneck caused by when fpdf has to output the actual PDF file (from RAM). Likely to be solved by handling large PDFs in batches.
+ No verbose option to see more logging of where the program is.
