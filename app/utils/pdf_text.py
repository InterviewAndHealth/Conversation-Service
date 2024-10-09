import aiohttp
from PyPDF2 import PdfReader
from io import BytesIO


async def fetch_pdf(pdf_url):
    try:
        # Step 1: Asynchronously download the PDF file
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as response:
                response.raise_for_status()  # Check for request errors
                pdf_content = await response.read()

        return pdf_content
    except aiohttp.ClientError as e:
        return f"Error downloading the PDF: {e}"


async def fetch_pdf_text(pdf_url):
    try:
        # Step 2: Fetch PDF content asynchronously
        pdf_content = await fetch_pdf(pdf_url)
        if isinstance(pdf_content, str):
            return pdf_content  # Return error message if fetching failed

        # Step 3: Load PDF into memory
        pdf_file = BytesIO(pdf_content)
        reader = PdfReader(pdf_file)

        # Step 4: Extract text from each page
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()

        return text
    except Exception as e:
        return f"Error processing the PDF: {e}"
