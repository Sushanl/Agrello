# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

## Backend API (Contract Analyzer)

This project now includes a Python FastAPI backend for contract analysis.

### Features

-   Accepts PDF contract uploads.
-   Extracts text from the PDF.
-   Uses an AI model (via OpenAI API) to:
    -   Summarize the contract in plain English.
    -   Highlight potential cons or unfavorable clauses.
-   Returns the analysis as a JSON response.

### Setup and Running the Backend

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set the OpenAI API Key:**
    The backend requires an OpenAI API key to function. Set it as an environment variable:
    ```bash
    export OPENAI_API_KEY='your_actual_openai_api_key_here'
    ```
    Replace `your_actual_openai_api_key_here` with your real key.

5.  **Run the FastAPI server:**
    From the project's root directory (not the `backend` directory):
    ```bash
    uvicorn backend.main:app --reload --app-dir .
    ```
    Or, if you are inside the `backend` directory:
    ```bash
    uvicorn main:app --reload
    ```
    The API will typically be available at `http://127.0.0.1:8000`. You can access the API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

### API Endpoint

-   **`POST /analyze-contract/`**:
    -   Upload a PDF file for analysis.
    -   **Request:** `multipart/form-data` with a `file` field containing the PDF.
    -   **Response (Success - 200 OK):**
        ```json
        {
          "original_filename": "contract.pdf",
          "simplified_contract": "Plain English summary of the contract...",
          "cons": [
            "Clause X: Potential issue description...",
            "Clause Y: Another potential issue..."
          ]
        }
        ```
    -   **Response (Error):** Appropriate HTTP status codes (400, 422, 500) with JSON error details.

### Running Tests

1.  Ensure you are in the `backend` directory and your virtual environment is activated.
2.  Make sure test dependencies are installed (they are included in `requirements.txt`).
3.  A dummy `OPENAI_API_KEY` is usually sufficient for most tests as API calls are mocked. However, ensure it's set:
    ```bash
    export OPENAI_API_KEY='test_key_for_unit_tests'
    ```
4.  Run tests using unittest:
    ```bash
    python -m unittest discover -s tests
    ```
    Or, to run a specific test file (e.g., `test_main_api.py`):
    ```bash
    python -m unittest tests.test_main_api
    ```
