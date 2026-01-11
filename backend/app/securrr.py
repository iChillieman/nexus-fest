# securrr.py
import bcrypt

def get_hashed_secret(plain_text_secret: str) -> str:
    return bcrypt.hashpw(plain_text_secret.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_secret(plain_text_secret: str, hashed_secret: str) -> bool:
    return bcrypt.checkpw(plain_text_secret.encode('utf-8'), hashed_secret.encode('utf-8'))