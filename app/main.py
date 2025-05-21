from models import google_generative_ai_llm
from billParser import AnalyzeImage
from jsonStore import save_json, search_json
import streamlit as st
import os

# defining the model
llm = google_generative_ai_llm(temperature = 0.7)

def update_images_data_json(data_directory: str, llm):
    '''building default images data - json file'''
    
    json_response = AnalyzeImage().parse_bills_from_data_directory(data_directory, llm)
    save_json(json_response, type = type)
    

st.title("RAG-IMAGE-QA")

on = st.toggle("Use default images")

type = "default"
submit = ""

if not on:
    type = "browse"
    
    uploaded_files = st.file_uploader("Upload bill images", type=["png", "jpg", "jpeg"], accept_multiple_files = True)
    
    def load_uploaded_images():
        '''extracting the data from the uploaded images in json format and storing them in data/browse/images_data.json file''' 
        
        temp_paths = []
        for file in uploaded_files:
            temp_path = f"data/{type}/Images/{file.name}"
            temp_paths.append(temp_path)
            
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())
            
        with st.spinner("Parsing bill..."):
            json_response = AnalyzeImage().parse_bills(temp_paths, llm)
            save_json(json_response, type = type)
            
        for temp_path in temp_paths:
            os.remove(temp_path)
        st.success("Bill parsed!")
        st.session_state["parsed_images"] = True
        st.session_state["uploaded_filenames"] = [file.name for file in uploaded_files]
        

    if uploaded_files:
        uploaded_filenames = [file.name for file in uploaded_files]
        if (
            "parsed_images" not in st.session_state or
            "uploaded_filenames" not in st.session_state or
            st.session_state["uploaded_filenames"] != uploaded_filenames
        ):
            load_uploaded_images()

        question = st.text_input(
            "Ask question related to the uploaded bill images",
            value = "what is the total bill amount?"
        )

        submit = st.button("Submit")

elif on:
    reload = st.button("Reload Default images!")
    
    if reload:
        st.session_state["reloading"] = True
        with st.spinner("Reloading default images..."):
            update_images_data_json("data/default/Images", llm)
        st.session_state["reloading"] = False
        st.success("Default images reloaded!")
    
    question = st.text_input(
        "Ask question related to the default bill images",
        value = "what is the total bill amount?"
    )

    submit = st.button("Submit", disabled=st.session_state.get("reloading", False))

def get_response(question):
    '''getting the answer for the given question'''
    
    with st.spinner("Generating answer..."):
        answer = search_json(question, llm, type = type)
    return answer.content


if submit:
    answer = get_response(question)
    st.markdown(answer)