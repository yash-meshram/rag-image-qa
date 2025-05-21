from langchain_google_genai import ChatGoogleGenerativeAI

def google_generative_ai_llm(model: str = "gemini-2.0-flash", temperature: float = 0.0):
    '''define a google genrative ai model'''
    
    llm = ChatGoogleGenerativeAI(
        model = model,
        temperature = temperature
    )
    return llm