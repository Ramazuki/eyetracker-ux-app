from pydantic import BaseModel

class AdminSchema(BaseModel):
    login: str
    password: str
