from models import google_generative_ai_llm
from billParser import AnalyzeImage
from jsonStore import save_json, search_json
import streamlit as st
import os

llm = google_generative_ai_llm()

st.title("RAG-IMAGE-QA")

on = st.toggle("Use your own images")

type = "default"
submit = ""

if on:
    type = "browse"
    
    uploaded_file = st.file_uploader("Upload a bill image", type=["png", "jpg", "jpeg"])
    
    def load_uploded_images():   
        temp_path = f"data/browse/Images/temp_{uploaded_file.name}"
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        with st.spinner("Parsing bill..."):
            json_response = AnalyzeImage().parse_bill([temp_path], llm)
            save_json(json_response, type = type)
            
        os.remove(temp_path)
        st.success("Bill parsed!")

    if uploaded_file:
        load_uploded_images()
        
        question = st.text_input(
            "Ask question related to the bill images uploaded",
            value = "what is the total bill amount"
        )

        submit = st.button("Submit")

elif not on:
    question = st.text_input(
        "Ask question related to the bill images uploaded",
        value = "what is the total bill amount"
    )

    submit = st.button("Submit")

def get_response(question): 
    answer = search_json(question, llm, type = type)
    
    return answer.content

if submit:
    answer = get_response(question)
    st.markdown(answer)