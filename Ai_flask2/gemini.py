import google.generativeai as genai
import os
from config import Config

genai.configure(api_key=Config.GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Write a story about a magic backpack.")
print(response.text)