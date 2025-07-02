# schemas.py
from pydantic import BaseModel

class UsuarioCreate(BaseModel):
    usuario: str
    password: str
    rol: str

class UsuarioOut(BaseModel):
    id: int
    usuario: str
    rol: str

    class Config:
        orm_mode = True