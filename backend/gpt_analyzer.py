import os
import openai

# Ensure the OpenAI API key is set as an environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set.")
openai.api_key = api_key

async def analyze_contract_text(contract_text: str, model: str = "gpt-3.5-turbo") -> tuple[str, list[str]]:
    """
    Analyzes contract text using GPT to get a plain English summary and highlight cons.

    Args:
        contract_text: The text of the contract.
        model: The GPT model to use (e.g., "gpt-3.5-turbo", "gpt-4").

    Returns:
        A tuple containing:
            - simplified_contract (str): Plain English summary.
            - cons (list[str]): List of highlighted cons or unfavorable clauses.
    Returns (None, None) if analysis fails.
    """
    if not contract_text.strip():
        return "The provided contract text is empty.", []

    system_prompt = """\
You are a helpful assistant specialized in contract law and analysis.
Your task is to review a contract text, simplify it into plain English, and identify any clauses that might be unfavorable to one party or potential cons.
Present the output clearly, with a summary section and a list of cons.
Respond in JSON format with two keys: "simplified_contract" and "cons".
The "simplified_contract" should be a string.
The "cons" should be a list of strings, where each string is a specific con or unfavorable clause found.
If no specific cons are found, the "cons" list should be empty.
Example JSON output:
{
  "simplified_contract": "This is a plain English summary of the contract...",
  "cons": [
    "Clause 3.1: The termination conditions are heavily skewed in favor of Party A.",
    "Section 5: The liability cap for Party B is unusually low."
  ]
}
"""
    user_prompt = f"Please analyze the following contract text:\n\n```\n{contract_text}\n```"

    try:
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3, # Lower temperature for more factual and less creative responses
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        # Attempt to parse the JSON response from GPT
        import json
        try:
            analysis_result = json.loads(content)
            simplified_contract = analysis_result.get("simplified_contract", "Could not extract simplified contract.")
            cons = analysis_result.get("cons", [])

            # Ensure cons is a list of strings
            if not isinstance(cons, list) or not all(isinstance(item, str) for item in cons):
                cons = ["GPT response for cons was not in the expected format (list of strings)."]

            return simplified_contract, cons

        except json.JSONDecodeError:
            # Fallback if GPT doesn't return perfect JSON, try to give a reasonable message
            return "Failed to parse GPT response as JSON. The raw response was: " + content, []
        except AttributeError: # Handle cases where response structure is unexpected
             return "Unexpected response structure from GPT.", []


    except openai.APIError as e:
        # Handle API errors (e.g., rate limits, server errors)
        print(f"OpenAI API Error: {e}")
        return f"OpenAI API Error: {str(e)}", []
    except Exception as e:
        # Handle other potential errors (e.g., network issues)
        print(f"Error during GPT analysis: {e}")
        return f"An unexpected error occurred during analysis: {str(e)}", []

if __name__ == '__main__':
    import asyncio
    # This part is for testing the function directly.
    # You need to have OPENAI_API_KEY set in your environment.

    sample_contract = """\
    This AGREEMENT is made and entered into as of the 1st day of January, 2024, by and between Party A ("The Company"),
    and Party B ("The Consultant").
    WHEREAS, The Company desires to retain the services of The Consultant, and The Consultant is willing to perform such services.
    NOW, THEREFORE, in consideration of the mutual covenants contained herein, the parties agree as follows:
    1. SERVICES. The Consultant shall perform web development services.
    2. TERM. This Agreement shall commence on the date hereof and shall continue for a period of 12 months, unless terminated earlier.
    3. PAYMENT. The Company shall pay The Consultant a fee of $5000 per month. The Consultant shall bear all of its own expenses.
    4. TERMINATION. The Company may terminate this Agreement with 7 days notice for any reason. The Consultant may terminate with 30 days notice.
    5. CONFIDENTIALITY. The Consultant shall not disclose any confidential information of The Company.
    6. GOVERNING LAW. This Agreement shall be governed by the laws of the State of Confusion.
    7. ENTIRE AGREEMENT. This Agreement constitutes the entire agreement between the parties.
    """

    async def test_analysis():
        print("Testing GPT contract analysis...")
        if not api_key:
            print("OPENAI_API_KEY not set. Skipping direct test of gpt_analyzer.")
            return

        summary, cons = await analyze_contract_text(sample_contract)

        if summary or cons:
            print("\n--- Simplified Contract ---")
            print(summary)
            print("\n--- Potential Cons ---")
            if cons:
                for con in cons:
                    print(f"- {con}")
            else:
                print("No specific cons identified by GPT, or an issue occurred.")
        else:
            print("Analysis failed or returned no content.")

    if os.getenv("OPENAI_API_KEY"):
        asyncio.run(test_analysis())
    else:
        print("Skipping gpt_analyzer.py direct test because OPENAI_API_KEY is not set.")
