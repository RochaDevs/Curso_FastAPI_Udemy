from fastapi import FastAPI

from .database import engine
from .models import Base
from .routers import admin, auth, todos, users

app = FastAPI()

Base.metadata.create_all(bind=engine)

"""
models.Base → Aqui você está acessando a variável Base que você criou no seu database.py com:

.metadata.create_all() → Isso é o que diz ao SQLAlchemy para criar as tabelas no banco de dados, com base nas classes que herdam de Base (ou seja, suas models).

bind=engine → Aqui você está dizendo "Use o banco de dados ao qual esse engine está conectado", que no seu caso é o todos.db (SQLite).
"""

@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

