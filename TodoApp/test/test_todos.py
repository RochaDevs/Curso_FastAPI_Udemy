import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base
from ..main import app
from ..models import Todos
from ..routers.todos import get_current_user, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass = StaticPool, #Garante que todas as conexões compartilhem o mesmo banco para testes
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def override_get_current_user():
    return {'username': 'matheusrocha', 'id': 1, 'user_role': 'admin'}
    
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

"""
    O que é app.dependency_overrides?
    
        O app.dependency_overrides é um dicionário interno do FastAPI.
        Ele permite substituir (ou sobrescrever) as dependências da sua aplicação apenas no contexto de testes (ou de forma controlada).
    
    Ele diz para o FastAPI:

        “use override_get_db sempre que alguém pedir get_db”

        “use override_get_current_user sempre que alguém pedir get_current_user”

        Isso deixa seu ambiente de teste 100% controlado.
        
    app.dependency_overrides = {
        get_db: override_get_db,
        get_current_user: override_get_current_user,
    }

"""

client = TestClient(app)

@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code",
        description="Need to learn everyday",
        priority=5,
        complete=False,
        owner_id=1
    )
    
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text('DELETE from todos;'))
        connection.commit()

def test_read_one_authenticated(test_todo):
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'complete': False,
        'title': 'Learn to code',
        'description': 'Need to learn everyday',
        'id': 1,
        'priority': 5,
        'owner_id': 1
    }
    
def test_read_one_authenticated_not_found(test_todo):
    response = client.get("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        'detail': 'Todo is not found'
    }

def test_create_todo(test_todo):
    request_data={
        'title': 'New Todo!',
        'description': 'New todo description',
        'priority': 5,
        'complete': False
    }
    
    response = client.post('/todo/', json=request_data)
    assert response.status_code == 201
    
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')
    
    