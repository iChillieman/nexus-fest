from pydantic import BaseModel
from typing import List, Optional

# --- Status Schemas ---
class ForgeStatusBase(BaseModel):
    name: str

class ForgeStatusRead(ForgeStatusBase):
    id: int

    class Config:
        from_attributes = True

# --- User & Auth Schemas ---
class ForgeUserBase(BaseModel):
    username: str

class ForgeUserCreate(ForgeUserBase):
    email: str
    password: str

class ForgeUserRead(ForgeUserBase):
    id: int
    email: str
    created_at: int

    class Config:
        from_attributes = True

class ForgeLoginRequest(BaseModel):
    username: str
    password: str

class ForgeRegisterResponse(ForgeUserRead):
    api_key: str

# --- API Key Schemas ---
class ForgeAPIKeyBase(BaseModel):
    name: str

class ForgeAPIKeyCreate(ForgeAPIKeyBase):
    pass 

class ForgeAPIKeyUpdate(ForgeAPIKeyBase):
    name: str

class ForgeAPIKeyRead(ForgeAPIKeyBase):
    id: int
    created_at: int
    expires_at: Optional[int] = None
    
    class Config:
        from_attributes = True

class ForgeAPIKeyResponse(ForgeAPIKeyRead):
    api_key: str # Returned only on creation

# --- Task Schemas ---
class ForgeTaskBase(BaseModel):
    title: str
    description: Optional[str] = None

class ForgeTaskCreate(ForgeTaskBase):
    project_id: int

class ForgeTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status_id: Optional[int] = None

class ForgeTaskRead(ForgeTaskBase):
    id: int
    project_id: int
    status_id: int
    created_at: int
    updated_at: int
    deleted_at: Optional[int] = None
    status: ForgeStatusRead 

    class Config:
        from_attributes = True

# --- Project Schemas ---
class ForgeProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ForgeProjectCreate(ForgeProjectBase):
    pass

class ForgeProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ForgeProjectRead(ForgeProjectBase):
    id: int
    created_at: int
    updated_at: int
    deleted_at: Optional[int] = None
    tasks: List[ForgeTaskRead] = []

    class Config:
        from_attributes = True
