from fastapi import status

from ..routers.users import get_current_user, get_db
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get('/users')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'matheusrocha'
    assert response.json()['email'] == 'matheusrocha@gmail.com'
    assert response.json()['first_name'] == 'Matheus'
    assert response.json()['last_name'] == 'Rocha'
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '(11) 95604-2056'
    
def test_change_password_sucess(test_user):
    response = client.put('/users/password', json={
        'password': 'teste1234',
        'new_password': 'test5678'
    })
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
def test_change_password_invalid_current_password(test_user):
    response = client.put('/users/password', json={
        'password': 'senha_errada',
        'new_password': 'test5678'
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        'detail': 'Error on password change'
    }
    
def test_change_phone_number_sucess(test_user):
    response = client.put('/users/phonenumber/22222222')
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
