from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",   #1GB model
)

sentences = [
    "Machine learning is a subset of AI.",
    "Deep learning uses neural networks.",
    "I like playing football."
]

embeddings = model.embed_documents(sentences)

print(len(embeddings))  # Should print 3, as there are 3 sentences