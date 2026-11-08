from dotenv import load_dotenv
import os 
from langchain.chat_models import init_chat_model

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API key not found in environment variables")

models = [
    "gemini-3.5-flash-lite"
] 

for model_name in models: 
    try: 
        print(f"Initializing model: {model_name}")
        model = init_chat_model(f"google_genai:{model_name}",api_key=api_key)
        prompt = input("Enter prompt:")
        response = model.invoke(prompt,temperature=0.7)
        content = response.content
        if isinstance(content, list):
            text="".join(block["text"] for block in content if isinstance(block, dict) and block.get("type") == "text")
        else:
            text= content
        print(f"Response: {text}")
        break
    except Exception as e:
        print(f"Failed to initialize model {model_name}: {e}")
else: 
    print("All models failed to initialize")    