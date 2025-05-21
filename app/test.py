from dotenv import load_dotenv
import os

load_dotenv("../.env")

# bill parsing schema
BILL_SCHEMA = {
    "invoice_number": str,
    "order_id": str,
    "order_date": str,
    "invoice_date": str,
    "seller": str,
    "buyer": str,
    "billing_address": str,
    "items": [
        {
            "description": str,
            "quantity": int,
            "unit_price": float,
            "tax_percent": float,
            "total_price": float
        }
    ],
    "subtotal": float,
    "tax": float,
    "total": float,
    "payment_method": str
}


# extracting text from image

# using pytesseract
import pytesseract
from PIL import Image

extracted_text = pytesseract.image_to_string(Image.open("../data/bill1.png"))
print(extracted_text)
type(extracted_text)


# LLM
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model = "gemini-2.0-flash"
)


# prompt
import json
from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_template(
    """
    ## BILL SCHEMA
    {bill_schema}

    ## BILL TEXT:
    {text}
    
    ## INSTRUCTION:
    Extract structured information from the 'BILL TEXT' session and return it as valid JSON as a schema given in 'BILL SCHEMA' session.
    only return the valid JSON. Dont even mention that it is a json
    
    ### VALID JSON (NO PREAMBLE):
    """
)
    
# chain
chain = prompt | llm

response = chain.invoke(
    input = {
        "bill_schema": BILL_SCHEMA,
        "text": extracted_text
    }
)

print(response.content)


# output should be json formate
from langchain_core.output_parsers import JsonOutputParser

json_parser = JsonOutputParser()
json_response = json_parser.parse(response.content)
print(json_response)
json_response


# extracting file name
import imghdr
import os

file_path = "../data/bill1.png"

# Check if file is an image
if imghdr.what(file_path):
    image_name = os.path.basename(file_path)
    print(image_name)
else:
    print("This is NOT an image.")
    
   
