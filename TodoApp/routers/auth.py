from warnings import deprecated

from fastapi import APIRouter
from models import Users
from passlib.context import CryptContext
from pydantic import BaseModel

router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

@router.post("/auth/")
async def create_user(create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True
    )
    
    
    return create_user_model

"""
Se você tentar passar isso diretamente para Users(**...), o Python tentaria encontrar um parâmetro chamado password na classe Users, mas ela espera hashed_password. Além disso, o campo is_active em Users não seria preenchido pelo dicionário, o que causaria um erro se ele não tiver um valor padrão ou for obrigatório.
"""
