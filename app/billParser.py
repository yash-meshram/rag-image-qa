import os
import pytesseract
from PIL import Image
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from concurrent.futures import ThreadPoolExecutor, as_completed
import boto3


class AnalyzeImage:
    def __init__(self):
        # bill parsing schema
        self.BILL_SCHEMA = {
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
    
    
    # Method 1: Pytesseract (currently using)
    def extract_text(self, image_paths: list):
        '''extracting the text from the bill images using pytesseract'''
        
        def is_valid_image(image_path):
            try:
                with Image.open(image_path) as img:
                    img.verify()
                return True
            except Exception:
                return False
        
        def process_image(image_path):
            if is_valid_image(image_path):
                image_name = os.path.basename(image_path)
                try:
                    text = pytesseract.image_to_string(Image.open(image_path))
                    return image_name, text
                except Exception as e:
                    return image_name, f"Error: {e}"
            return None

        extracted_text = {}

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_image, path) for path in image_paths]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    image_name, text = result
                    extracted_text[image_name] = text

        return extracted_text
    
    
    # Method 2: AWS Textract
    def extract_text_(self, image_paths: list):
        '''extracting the text from the bill images using AWS textract'''
        
        def is_valid_image(image_path):
            try:
                with Image.open(image_path) as img:
                    img.verify()
                return True
            except Exception:
                return False
        
        def process_image(image_path):
            if is_valid_image(image_path):
                image_name = os.path.basename(image_path)
                try:
                    textract_client = boto3.client('textract')
                    with open(image_path, "rb") as document_file:
                        document_bytes = document_file.read()               
                    response = textract_client.detect_document_text(Document={"Bytes": document_bytes})
                    text = ''
                    for item in response['Blocks']:
                        if item['BlockType'] == 'LINE':
                            text += item['Text'] + '\n'
                    return image_name, text
                except Exception as e:
                    return image_name, f"Error: {e}"
            return None

        extracted_text = {}

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_image, path) for path in image_paths]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    image_name, text = result
                    extracted_text[image_name] = text

        return extracted_text
        

    def extract_bill_info(self, extracted_text, llm):
        '''Use LLM to extract structured bill info from the extracted text'''
        
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
        chain = prompt | llm
        response = chain.invoke(
            input = {
                "bill_schema": self.BILL_SCHEMA,
                "text": extracted_text
            }
        )
        return response
            

    def parse_bills(self, image_paths, llm):
        '''extract the data from the images and return it in json format'''
        
        extracted_text = self.extract_text(image_paths)
        response = self.extract_bill_info(extracted_text, llm)
        # json parser
        json_parser = JsonOutputParser()
        json_response = json_parser.parse(response.content)
        return json_response
    

    def parse_bills_from_data_directory(self, data_directory: str, llm):
        '''extract the data from the all the images in the given data_directory and retun in json format'''
        
        image_paths = [
            os.path.join(data_directory, file_name)
            for file_name in os.listdir(data_directory)
            if file_name.endswith(("png", "jpg", "jpeg"))
        ]
        json_response = self.parse_bills(image_paths, llm)
        return json_response