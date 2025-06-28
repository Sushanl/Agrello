import PyPDF2
from io import BytesIO

def extract_text_from_pdf(pdf_file_bytes: bytes) -> str:
    """
    Extracts text content from a PDF file.

    Args:
        pdf_file_bytes: Bytes of the PDF file.

    Returns:
        The extracted text content as a string.
        Returns an empty string if text extraction fails or PDF is invalid.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file_bytes))
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() or ""
        return text
    except PyPDF2.errors.PdfReadError:
        # Handle cases where the PDF is encrypted or malformed
        return ""
    except Exception:
        # Catch any other unexpected errors during PDF processing
        return ""

if __name__ == '__main__':
    # Example usage:
    # This part is for testing the function directly.
    # You would need a sample PDF file named 'sample.pdf' in the same directory.
    try:
        with open("sample.pdf", "rb") as f:
            pdf_bytes = f.read()
            if pdf_bytes:
                extracted_text = extract_text_from_pdf(pdf_bytes)
                if extracted_text:
                    print("Successfully extracted text:")
                    print(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
                else:
                    print("Could not extract text from PDF or PDF is empty/invalid.")
            else:
                print("Sample PDF is empty.")
    except FileNotFoundError:
        print("Error: sample.pdf not found. Please place a sample PDF in the backend directory for testing.")
    except Exception as e:
        print(f"An error occurred: {e}")
