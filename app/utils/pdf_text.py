from io import BytesIO

import aiohttp
from PyPDF2 import PdfReader


async def fetch_pdf(pdf_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as response:
                response.raise_for_status()
                pdf_content = await response.read()

        return pdf_content
    except aiohttp.ClientError as e:
        return f"Error downloading the PDF: {e}"


async def fetch_pdf_text(pdf_url):
    try:
        pdf_content = await fetch_pdf(pdf_url)
        if isinstance(pdf_content, str):
            return pdf_content

        pdf_file = BytesIO(pdf_content)
        reader = PdfReader(pdf_file)

        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()

        return text
    except Exception as e:
        return f"Error processing the PDF: {e}"
