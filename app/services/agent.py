from app.db.connection import query
from app.db.queries import simple_query
import json
from mistralai.client import Mistral

import os
from dotenv import load_dotenv
load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def run_agent(message: str):
    #1. Retrieve DB data
    sample_data = simple_query()

    #2. System prompt for day 2
    SYSTEM_PROMPT = f"""
    You are a professional assistant that outputs customer data exactly as provided.
    You do not have direct access to the database.
    You will be provided with customer data by the backend.
    Never invent data. Never add or remove fields.

    Your job is to output the customer data under the heading:

    Customer Data:
    """
    #3. Hard coded user prompt for day 2
    USER_PROMPT = f"""
    Please output the customer data exactly as provided.

    Here is the data:
    {sample_data}
    """
    #4. Call Mistral API
    client = Mistral(api_key=MISTRAL_API_KEY)
    response = client.chat.complete(
        model="mistral-medium-latest",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT}
        ]
    )

    #5. Extract answer
    answer = response.choices[0].message.content if response.choices and response.choices[0].message else "No response generated"
    print("Agent response from Mistral API:", answer)

    #6. Return structured response
    return {
        "user_question": message,
        "agent_response": answer,
        "data_used": sample_data
    }


# def run_agent(message: str):
#     print(f"Agent received message: {message}")
#     rows = query("SELECT first_name, last_name FROM customers LIMIT 3;")
#     return {
#         "echo": message,
#         "agent_response": f"Hello! You said: '{message}'. Below are some sample customers from the database:",
#         "sample_customers": {"rows": [dict(row._mapping) for row in rows]}
#     }