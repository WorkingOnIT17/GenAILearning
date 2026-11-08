from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()  # Load environment variables from .env file

model = ChatGoogleGenerativeAI(
    model = "gemini-3.5-flash-lite",
    max_tokens = 1024,
)

response = model.invoke("Who is the prime minister of India?")
print(response.content)