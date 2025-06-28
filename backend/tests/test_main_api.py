import unittest
import os
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from io import BytesIO

# Important: The TestClient needs to be created *after* the OPENAI_API_KEY is patched for gpt_analyzer
# or we need to ensure the app instance uses a mocked gpt_analyzer.
# For simplicity in this setup, we'll patch globally.

# Set a dummy API key for tests before importing the FastAPI app
os.environ["OPENAI_API_KEY"] = "fake_test_key"

from backend.main import app # app instance from your main.py

# Now that app is imported, gpt_analyzer has also been imported and checked for the key.

class TestMainAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    @patch('backend.main.extract_text_from_pdf')
    @patch('backend.main.analyze_contract_text', new_callable=AsyncMock) # AsyncMock for async func
    def test_analyze_contract_success(self, mock_analyze_contract_text, mock_extract_text_from_pdf):
        # Mock return values
        mock_extract_text_from_pdf.return_value = "This is extracted PDF text."
        mock_analyze_contract_text.return_value = ("Simplified summary.", ["Con 1.", "Con 2."])

        # Create a dummy PDF file-like object
        pdf_bytes = b"%PDF-1.4\n%test\n%%EOF" # Minimal valid PDF bytes
        file_like_object = BytesIO(pdf_bytes)

        response = self.client.post(
            "/analyze-contract/",
            files={"file": ("test_contract.pdf", file_like_object, "application/pdf")}
        )

        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response["original_filename"], "test_contract.pdf")
        self.assertEqual(json_response["simplified_contract"], "Simplified summary.")
        self.assertEqual(json_response["cons"], ["Con 1.", "Con 2."])

        # Ensure mocks were called
        mock_extract_text_from_pdf.assert_called_once_with(pdf_bytes)
        mock_analyze_contract_text.assert_called_once_with("This is extracted PDF text.")

    def test_analyze_contract_invalid_file_type_not_pdf(self):
        file_like_object = BytesIO(b"some text data")
        response = self.client.post(
            "/analyze-contract/",
            files={"file": ("test_contract.txt", file_like_object, "text/plain")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid file type", response.json()["detail"])

    def test_analyze_contract_invalid_content_type(self):
        file_like_object = BytesIO(b"%PDF-1.4...") # Content might be PDF like
        response = self.client.post(
            "/analyze-contract/",
            files={"file": ("test_contract.pdf", file_like_object, "text/plain")} # Wrong content type
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid file content type", response.json()["detail"])


    @patch('backend.main.extract_text_from_pdf')
    def test_analyze_contract_pdf_extraction_fails(self, mock_extract_text_from_pdf):
        mock_extract_text_from_pdf.return_value = "" # Simulate extraction failure

        pdf_bytes = b"%PDF-1.4\n%test\n%%EOF"
        file_like_object = BytesIO(pdf_bytes)

        response = self.client.post(
            "/analyze-contract/",
            files={"file": ("test.pdf", file_like_object, "application/pdf")}
        )
        self.assertEqual(response.status_code, 422) # Unprocessable Entity
        self.assertIn("Could not extract text", response.json()["detail"])

    @patch('backend.main.extract_text_from_pdf')
    @patch('backend.main.analyze_contract_text', new_callable=AsyncMock)
    def test_analyze_contract_gpt_analysis_fails(self, mock_analyze_contract_text, mock_extract_text_from_pdf):
        mock_extract_text_from_pdf.return_value = "Some text."
        # Simulate GPT analysis returning None, None (indicating failure)
        mock_analyze_contract_text.return_value = (None, None)

        pdf_bytes = b"%PDF-1.4\n%test\n%%EOF"
        file_like_object = BytesIO(pdf_bytes)

        response = self.client.post(
            "/analyze-contract/",
            files={"file": ("test.pdf", file_like_object, "application/pdf")}
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Contract analysis failed", response.json()["detail"])

    @patch('backend.main.extract_text_from_pdf')
    @patch('backend.main.analyze_contract_text', new_callable=AsyncMock)
    def test_analyze_contract_gpt_analysis_raises_exception(self, mock_analyze_contract_text, mock_extract_text_from_pdf):
        mock_extract_text_from_pdf.return_value = "Some text."
        mock_analyze_contract_text.side_effect = Exception("GPT blew up")

        pdf_bytes = b"%PDF-1.4\n%test\n%%EOF"
        file_like_object = BytesIO(pdf_bytes)

        response = self.client.post(
            "/analyze-contract/",
            files={"file": ("test.pdf", file_like_object, "application/pdf")}
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Error during GPT analysis: GPT blew up", response.json()["detail"])

    # Test for OPENAI_API_KEY not set (this is a bit tricky due to import-time checks)
    # One way is to run the client in a subprocess with a modified environment.
    # Another is to try and force a reload of modules if possible.
    # For now, the gpt_analyzer test covers the direct raise of EnvironmentError.
    # The endpoint itself would rely on that propagated error.
    # If gpt_analyzer.py's import-time check for OPENAI_API_KEY fails, FastAPI app won't even start correctly.
    # This makes it hard to test with TestClient, which assumes a running app.
    # We'll rely on the unit test for gpt_analyzer for the API key check.

    def tearDown(self):
        # Clean up environment variables if necessary, though TestClient is preferred.
        # For OPENAI_API_KEY, it was set before app import.
        pass

if __name__ == '__main__':
    # To run these tests:
    # Ensure OPENAI_API_KEY is set in the environment, or they will fail if gpt_analyzer fails to load.
    # Example: OPENAI_API_KEY="testkey" python -m unittest backend.tests.test_main_api
    # The `os.environ["OPENAI_API_KEY"] = "fake_test_key"` line at the top helps for isolated test runs.
    unittest.main()
