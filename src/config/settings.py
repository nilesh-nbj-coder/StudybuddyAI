import os
from dotenv import load_dotenv

load_dotenv()

class Settings():
    GROQ_API_KEY=os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME="llama-3.3-70b-versatile"
    TEMPRATURE=0.9
    MAX_RETRIES=3
    
settings=Settings()