from datetime import datetime, timedelta, timezone
from typing import Annotated

from database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from models import Users
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# SECRET_KEY: usada para assinar e verificar o JWT. Nunca coloque isso no código-fonte em produção!
SECRET_KEY = 'ea4927993a91ad9b415ed3b64f5f6c0d50e62d39d7a1a69d210a961af9949a78'

# HS256: algoritmo HMAC SHA256 para assinatura do token.
ALGORITHM = 'HS256'


# Define que usaremos bcrypt para hash de senha.
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
"""
    bcrypt_context.hash(...) cria um hash.
    bcrypt_context.verify(...) compara senha crua com o hash armazenado.
"""

# Indica que a autenticação será feita via Bearer token (JWT).
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
"""
    tokenUrl='auth/token': URL que o frontend usa para obter o token JWT.
"""

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number = str

# Define o formato de resposta da rota de login: token JWT + tipo ("bearer").
class Token(BaseModel):
    access_token:str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(
        Users.username == username
    ).first()
    
    if not user:
        return False
    
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    
    return user

def create_acess_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    
    #Claims
    encode = {
        'sub': username, # recomendado
        'id': user_id,  # customizado
        'role': role #
    }
    
    """
        Cria um dicionário chamado encode com os dados que serão codificados no token:

        'sub': significa "subject", é o campo padrão para representar quem é o dono do token (aqui, o username).

        'id': o ID do usuário (pode ser usado para buscar dados no banco no futuro).

        Esse dicionário representa o payload do JWT, ou seja, os dados que serão armazenados dentro do token.
    """
    
    expires = datetime.now(timezone.utc) + expires_delta
    
    """
        Calcula a data/hora de expiração do token:

        datetime.now(timezone.utc): pega o horário atual em UTC.

        + expires_delta: soma o tempo de expiração (ex: 20 minutos).

        O resultado é o timestamp no qual o token deixa de ser válido.
    """
    
    encode.update({'exp': expires})
    
    """
        Adiciona a chave 'exp' ao dicionário encode:

        'exp' é um campo padrão do JWT e representa a data de expiração.

        JWTs que passam do tempo de expiração não são mais aceitos quando verificados.
    """
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    """
        Gera o token JWT final:

        encode: o dicionário de dados do payload (sub, id, exp).

        SECRET_KEY: a chave secreta usada para assinar o token.

        algorithm=ALGORITHM: define o algoritmo de assinatura (como HS256).
    """

# Define uma função assíncrona que recupera o usuário atual com base no token JWT enviado pelo cliente
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user 1')
        
        return {'username': username, 'id': user_id, 'user_role': user_role}
    
    except JWTError as e:
        print(f'Erro no JWT: {str(e)}')  # ou use logging
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user 2')
     
        
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest, db: db_dependency):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True,
        phone_number=create_user_model.phone_number
    )
    
    db.add(create_user_model)
    db.commit()
    
    
    return create_user_model

"""
Se você tentar passar isso diretamente para Users(**...), o Python tentaria encontrar um parâmetro chamado password na classe Users, mas ela espera hashed_password. Além disso, o campo is_active em Users não seria preenchido pelo dicionário, o que causaria um erro se ele não tiver um valor padrão ou for obrigatório.
"""

#response_model=Token: define o formato da resposta usando o Pydantic model Token:
@router.post("/token", response_model=Token)
async def login_for_acess_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user 3')
    
    token = create_acess_token(user.username, user.id, user.role, timedelta(minutes=20))
    
    return {'access_token': token, 'token_type': 'bearer'}