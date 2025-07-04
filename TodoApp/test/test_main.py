from fastapi import status
from fastapi.testclient import TestClient

from ..main import app

"""
    O TestClient é uma ferramenta do FastAPI (em cima do Starlette) que permite simular chamadas HTTP ao seu app FastAPI sem precisar subir um servidor de verdade.
    Ou seja, é um “cliente de testes” que manda requisições diretamente para a aplicação, simulando requisições reais.
"""

client = TestClient(app)
"""
    Cria uma instância do TestClient, passando sua aplicação app como parâmetro.
    Esse client é como se fosse o navegador do usuário, mas rodando dentro do pytest, simulando chamadas HTTP.
"""
    
def test_return_health_check():
    response = client.get('/healthy')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'Healthy'}
