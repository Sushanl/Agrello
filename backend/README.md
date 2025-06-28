# Contract Analyzer Backend

This directory contains the FastAPI backend for the Contract Analyzer application.

## Functionality

The backend provides an API endpoint to:
1.  Accept a PDF file (presumably a contract).
2.  Extract text from the PDF.
3.  Send the extracted text to an OpenAI GPT model for analysis.
4.  The AI is prompted to return:
    *   A simplified, plain English summary of the contract.
    *   A list of potential cons or unfavorable clauses.
5.  Return this analysis as a JSON response.

## Setup and Running

For detailed instructions on setting up, running the server, and running tests, please refer to the "Backend API (Contract Analyzer)" section in the [main project README.md](../README.md).

### Quick Commands (from project root)

*   **Set API Key (do this first in your shell session):**
    ```bash
    export OPENAI_API_KEY='your_openai_api_key'
    ```
*   **Install Dependencies (run from `backend` directory after creating/activating venv):**
    ```bash
    # cd backend
    # python -m venv venv
    # source venv/bin/activate (or venv\Scripts\activate on Windows)
    pip install -r requirements.txt
    ```
*   **Run Server (from project root):**
    ```bash
    uvicorn backend.main:app --reload --app-dir .
    ```
    Access Swagger UI at `http://127.0.0.1:8000/docs`.

*   **Run Tests (from `backend` directory):**
    ```bash
    # Ensure OPENAI_API_KEY is set (can be a dummy value like 'test_key' as mocks are used)
    python -m unittest discover -s tests
    ```

## Modules

*   `main.py`: Contains the FastAPI application, API endpoint definition (`/analyze-contract/`), CORS setup, and orchestration of PDF processing and GPT analysis.
*   `pdf_processor.py`: Handles text extraction from PDF files using the `PyPDF2` library.
*   `gpt_analyzer.py`: Manages interaction with the OpenAI API using the `openai` library. It crafts the prompt for contract summarization and con identification and parses the response.
*   `requirements.txt`: Lists Python dependencies for the backend.
*   `tests/`: Contains unit and integration tests.
    *   `test_main_api.py`: Tests for the FastAPI endpoint.
    *   `test_pdf_processor.py`: Tests for PDF text extraction logic.
    *   `test_gpt_analyzer.py`: Tests for the GPT interaction logic.

## Environment Variables

*   `OPENAI_API_KEY`: **Required**. Your API key for accessing OpenAI services. The application will not start correctly (or GPT analysis will fail) if this is not set.

## API Endpoint Details

See the [main project README.md](../README.md) for details on the `/analyze-contract/` endpoint, request format, and response structure.
