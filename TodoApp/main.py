from typing import Annotated

import models
from database import SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, Path
from models import Todos
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

"""
O Annotated é uma forma nova do Python (a partir do 3.9/3.10) de adicionar anotações extras de metadados aos tipos.
"""

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
"""
models.Base → Aqui você está acessando a variável Base que você criou no seu database.py com:

.metadata.create_all() → Isso é o que diz ao SQLAlchemy para criar as tabelas no banco de dados, com base nas classes que herdam de Base (ou seja, suas models).

bind=engine → Aqui você está dizendo "Use o banco de dados ao qual esse engine está conectado", que no seu caso é o todos.db (SQLite).
"""

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()
        
"""
É um gerador Python que o FastAPI vai usar para fazer injeção de dependência de banco de dados nos endpoints.

def get_db():   →   Definindo a função
db = SessionLocal() →   Abre uma nova sessão de banco (uma conexão temporária)
try:	→   Começo de um bloco de segurança
yield db	→   "Entregue essa sessão para quem chamou essa função (normalmente o FastAPI num endpoint)"
finally: db.close()	→   Após o uso da sessão, feche a conexão, para evitar vazamentos de recursos

Diferença rápida entre return e yield:
return	
    Encerra a função e devolve um valor
    Não tem como continuar a execução
    
yield
    Pausa a função e devolve um valor temporário
    A função pode continuar de onde parou, depois
"""
        
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
        
        
db_dependency = Annotated[Session, Depends(get_db)]
"""
O Annotated faz parte da tipagem moderna do Python (vem do módulo typing).

Ele permite combinar um tipo + metadados extras.

No FastAPI, o uso mais comum de Annotated é quando você quer dizer o tipo de um parâmetro (ex: Session) e adicionar dependências (ex: Depends(get_db)) ao mesmo tempo.

db_dependency	→   Nome da variável (só um apelido, poderia ser qualquer nome)
Annotated[...]	→   Define um tipo + metadados
Session	→   Tipo de dado que o FastAPI vai injetar (no caso, uma sessão SQLAlchemy)
Depends(get_db)	→ Diz ao FastAPI: "Para preencher isso, use a dependência get_db()
"""

@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()

@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found')

@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    
    todo_model = Todos(**todo_request.model_dump())
    
    db.add(todo_model)
    db.commit()
    
@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    
    db.add(todo_model)
    db.commit()
    
@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delte_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).delete()
    
    db.commit()
    