import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base
from ..main import app
from ..models import Todos, Users
from ..routers.auth import bcrypt_context

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
    return {'username': 'matheusrocha', 'id': 1, 'role': 'admin'}

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
        

@pytest.fixture
def test_user():
    user = Users(
        username='matheusrocha',
        email='matheusrocha@gmail.com',
        first_name='Matheus',
        last_name='Rocha',
        hashed_password=bcrypt_context.hash('teste1234'),
        role='admin',
        phone_number='(11) 95604-2056'
    )
    
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()