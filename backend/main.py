import shutil
import tempfile
import os # Added os import
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# PyPDF2 is used by pdf_processor, not directly here.
# No need to import PyPDF2 directly in main.py if it's only used by a submodule.

from .pdf_processor import extract_text_from_pdf
from .gpt_analyzer import analyze_contract_text

app = FastAPI(title="Contract Analyzer API", version="0.1.0")

# Configure CORS
# This allows requests from your frontend development server (e.g., http://localhost:5173)
# For production, you might want to restrict origins more specifically.
origins = [
    "http://localhost:5173", # Default Vite dev server
    "http://localhost:3000", # Common React dev server
    # Add other origins if your frontend is served from a different port/domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Contract Analyzer API!"}

@app.post("/analyze-contract/")
async def analyze_contract_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are accepted.")

    if not file.content_type == "application/pdf":
         raise HTTPException(status_code=400, detail="Invalid file content type. Expected application/pdf.")

    # Create a temporary file to store the uploaded PDF
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            shutil.copyfileobj(file.file, tmp_pdf)
            tmp_pdf_path = tmp_pdf.name

        # Read the bytes from the temporary file for PDF processing
        with open(tmp_pdf_path, "rb") as f:
            pdf_bytes = f.read()

    except Exception as e:
        # Clean up tmp file if it was created before an error during copy
        if 'tmp_pdf_path' in locals() and os.path.exists(tmp_pdf_path):
            os.unlink(tmp_pdf_path)
        raise HTTPException(status_code=500, detail=f"Failed to save or read uploaded PDF: {str(e)}")
    finally:
        # Ensure the file stream from UploadFile is closed
        await file.close()

    # 1. Extract text from PDF
    extracted_text = extract_text_from_pdf(pdf_bytes)
    if not extracted_text.strip():
        if os.path.exists(tmp_pdf_path): # Clean up temp file
            os.unlink(tmp_pdf_path)
        raise HTTPException(status_code=422, detail="Could not extract text from the PDF. It might be empty, image-based, or corrupted.")

    # 2. Analyze text with GPT
    # Make sure OPENAI_API_KEY is set in the environment where this FastAPI app runs
    try:
        simplified_contract, cons = await analyze_contract_text(extracted_text)
    except EnvironmentError as e: # Specifically catch if OPENAI_API_KEY is not set
        if os.path.exists(tmp_pdf_path):
            os.unlink(tmp_pdf_path)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e: # Catch other errors from GPT analysis
        if os.path.exists(tmp_pdf_path):
            os.unlink(tmp_pdf_path)
        raise HTTPException(status_code=500, detail=f"Error during GPT analysis: {str(e)}")

    # 3. Clean up the temporary PDF file
    # Ensure tmp_pdf_path exists before trying to delete
    if 'tmp_pdf_path' in locals() and os.path.exists(tmp_pdf_path):
        os.unlink(tmp_pdf_path)

    if simplified_contract is None and cons is None: # Indicates a failure in analysis
        raise HTTPException(status_code=500, detail="Contract analysis failed to produce a result.")

    return {
        "original_filename": file.filename,
        "simplified_contract": simplified_contract,
        "cons": cons,
    }

# To run this app (from the project root directory):
# 1. Ensure OPENAI_API_KEY is set: export OPENAI_API_KEY='your_key_here'
# 2. Install dependencies: cd backend && pip install -r requirements.txt && cd ..
# 3. Run Uvicorn: uvicorn backend.main:app --reload --app-dir .
# Note: --app-dir . is used so that Python can find the 'backend' module.
# Alternatively, navigate to the 'backend' folder and run 'uvicorn main:app --reload'
# but then imports might need to be adjusted (e.g. from .pdf_processor to pdf_processor)
# The current setup (running from root with --app-dir .) is generally more robust for module resolution.
