from langchain_openai import ChatOpenAI
from dotenv import load_dotenv 
import os 

load_dotenv() 

llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"), temperature=0.5) 