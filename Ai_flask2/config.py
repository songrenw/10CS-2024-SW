import os

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'default-api-key')
    RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY', 'default-api-key')