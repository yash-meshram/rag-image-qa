import os
from typing import Dict, Any
import json
from langchain.prompts import PromptTemplate

def save_json(data: Dict[str, Any], type: str = "default"):
    '''saving the json data in the json file'''
    
    if type == "default":
        with open("data/default/images_data.json", 'w') as f:
            json.dump(data, f, indent=4)
            
    elif type == "browse":
        with open("data/browse/images_data.json", 'w') as f:
            json.dump(data, f, indent=4)


def load_json(type: str = "default"):
    '''loading the json file'''
    
    if type == "default":
        with open("data/default/images_data.json", 'r') as f:
            return json.load(f)
        
    elif type == "browse":
        with open("data/browse/images_data.json", 'r') as f:
            return json.load(f)


def search_json(question: str, images_data: json, llm, type: str = "default"):
    '''for the given question search in the json file for the answer using llm'''
    
    # images_data = load_json(type = type)
    
    BILL_SCHEMA = {
        "image_name": {
            "invoice_number": 'invoice number of the bill. format=str',
            "order_id": 'order id of the bill. format=str',
            "order_date": 'order date of the bill. format=str',
            "invoice_date": 'invoice date of the bill. format=str',
            "seller": 'seller mentioned in the bill. format=str',
            "buyer": 'buyer mentioned in the bill. format=str',
            "billing_address": 'billing address mentioned in the bill, if billing address is not available but shipping address is available then billing address will be same as shipping address. format=str',
            "items": [
                {
                    "name": 'name of the item. format=str',
                    "quantity": 'quantity of the item. format=int',
                    "unit_price": 'item price (in USD) for one unit, tax not included. format=float',
                    "tax_percent": 'percentage of the tax mentioned for the item. if it is not mentioned but tax amount is mentioned then calculate tax_percent for the item. format=float',
                    "total_price": 'total price (in USD) of the item. format=float'
                }
            ],
            "subtotal": 'sub-total (in USD) from the bill. if not mentioned then calculate using the details mentioned in the items key, subtotal does not include tax amount so the formula will be subtotal = (quantity*unit_price for all the items). format=float',
            "tax_percent": 'ovarall tax percent from the bill. if not mentioned then calculate using the details mentioned in the items key. format=float',
            "total": 'total price (in USD) for all the items mentioned in the bill. if not mentioned then calculate using the details mentioned in the items key total = (sum of total_price for each item). format=float',
            "payment_method": 'payment method mentioned in the bill. format=str'
        }
    }
    
    promt = PromptTemplate(
        input_variables = [],
        template = 
        '''
        ## Question:
        {question}
        
        ## Images Data:
        {images_data}
        
        ## Images Data Schema:
        {bill_schema}
        
        ## Instruction:
        In the 'Image Data' session I had provided the dictionary.
        The keys are the image name and values are image_data.
        All the explaination of the images_data had been mentioned in 'Images Data Schema' session
        Your job is to analyze the data provided in 'Images Data' session and provide the answer to the question mentioned in the 'Question' session.
        **Your answer should be based on the information provided in 'Images Data' session ONLY.**
        Remember all the price units are in USD, if in the response you have to tell anything related to price you have to disply unit as USD.
        If you are not able to get the answer based on data provided in 'Images Data' session then return answer as 'No information in the provided Images.'
        **Use only the information provided to you in 'Images Data' and 'Images Data Schema'. Dont use any other information even if it was asked to.**
        Do not provide preamble.
        
        ## ANSWER (No preamble):
        '''
    )
    
    chain = promt | llm
    
    answer = chain.invoke(
        input = {
            'question': question,
            'images_data': images_data,
            'bill_schema': BILL_SCHEMA
        }
    )
    return answer