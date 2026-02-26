# securrr.py
import os
import bcrypt
from dotenv import load_dotenv
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

def get_hashed_secret(plain_text_secret: str) -> str:
    return bcrypt.hashpw(plain_text_secret.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_secret(plain_text_secret: str, hashed_secret: str) -> bool:
    return bcrypt.checkpw(plain_text_secret.encode('utf-8'), hashed_secret.encode('utf-8'))

#### API Key Stuffs:

load_dotenv()
API_KEY_CHILLIEMAN = os.getenv("NEXUS_API_KEY_CHILLIEMAN", "Stub")
API_KEY_DAE = os.getenv("NEXUS_API_KEY_DAE", "Stub")
API_KEY_ZEPH = os.getenv("NEXUS_API_KEY_ZEPH", "Stub")

api_key_header = APIKeyHeader(name="X-Nexus-Key", auto_error=False)  # auto_error=False = nicer 403

# API Key for Chillieman
async def get_api_key_chillie(api_key: str = Security(api_key_header)):
    if api_key != API_KEY_CHILLIEMAN:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key


# API Key for Dae
async def get_api_key_dae(api_key: str = Security(api_key_header)):
    if api_key != API_KEY_DAE:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key

# API Key for the Zeph
async def get_api_key_zeph(api_key: str = Security(api_key_header)):
    if api_key != API_KEY_ZEPH:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key
