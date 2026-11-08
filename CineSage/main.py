from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List,Optional
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()  # Load environment variables from .env file

model = ChatGoogleGenerativeAI(
    model = "gemini-3.5-flash-lite",
    max_output_tokens = 1024,
)


#Schema
class Movie(BaseModel):
    title: str
    release_year: Optional[int] = None
    director: Optional[str] = None
    genre: List[str] = []
    cast: List[str] = []
    summary: Optional[str] = None
    themes: List[str] = []
    rating: Optional[float] = None


parser = PydanticOutputParser(pydantic_object=Movie)


prompt = ChatPromptTemplate.from_messages(
    [('system',"""
    Extract movie information from the paragraph 
    {format_instructions}
    """),
    ('human',"{paragraph}")]
)

para = input("Enter movie paragraph description: ")

final_prompt = prompt.invoke({"paragraph":para,
"format_instructions":parser.get_format_instructions()})

# Invoke the response
response = model.invoke(final_prompt)
parsed_movie = parser.invoke(response)

json_output = parsed_movie.model_dump_json(indent = 2)
print(json_output)