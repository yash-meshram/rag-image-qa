from langchain_google_genai import ChatGoogleGenerativeAI

def google_generative_ai_llm(model: str = "gemini-2.0-flash"):
    llm = ChatGoogleGenerativeAI(
        model = model
    )
    return llm