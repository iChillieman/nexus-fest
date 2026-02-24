# ... (Previous schemas)

# --- Comment Schemas ---
class ForgeTaskCommentBase(BaseModel):
    content: str

class ForgeTaskCommentCreate(ForgeTaskCommentBase):
    pass

class ForgeTaskCommentRead(ForgeTaskCommentBase):
    id: int
    task_id: int
    author_type: str # USER, WORKER
    author_id: int
    created_at: int

    class Config:
        from_attributes = True

# --- Worker Schemas ---
class ForgeWorkerBase(BaseModel):
    name: str

class ForgeWorkerCreate(ForgeWorkerBase):
    pass

class ForgeWorkerRead(ForgeWorkerBase):
    id: int
    user_id: int
    created_at: int
    
    class Config:
        from_attributes = True

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
    detail: Optional[str] = None
    notes: Optional[str] = None
    assigned_worker_id: Optional[int] = None

class ForgeTaskCreate(ForgeTaskBase):
    project_id: int

class ForgeTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    detail: Optional[str] = None
    notes: Optional[str] = None
    status_id: Optional[int] = None
    assigned_worker_id: Optional[int] = None

class ForgeTaskRead(ForgeTaskBase):
    id: int
    project_id: int
    status_id: int
    created_at: int
    updated_at: int
    deleted_at: Optional[int] = None
    status: ForgeStatusRead 
    assigned_worker: Optional[ForgeWorkerRead] = None # Include assigned worker details
    comments: List[ForgeTaskCommentRead] = [] # Include comments

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
