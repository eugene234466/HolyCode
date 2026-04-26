from dotenv import load_dotenv
import os
load_dotenv()
class Config:
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')
    BIBLE_API_URL = os.getenv('BIBLE_API_URL')
    VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY')    
    VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY')
    VAPID_EMAIL = os.getenv('VAPID_EMAIL')
    
    
    
    
    