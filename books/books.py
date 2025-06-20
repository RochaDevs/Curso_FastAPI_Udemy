from fastapi import Body, FastAPI  # Importa a classe FastAPI do framework

app = FastAPI()  # Cria uma instância da aplicação FastAPI. Essa instância será usada para definir as rotas e configurações.

BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Tree', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author One', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Six', 'category': 'math'},
]

@app.get("/books")  # Esse é o decorator que "decora" a função abaixo.
async def read_all_books():  
    return BOOKS


@app.get("/books/title/{book_title}") # {books_title} é o chamado parametro dinamico, o que você escreve na URL você consegue acessar dentro da função
async def read_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            return book


@app.get("/books/") # Na URL, após / deve ser adicionado um ? e então o parametro da função (query param)
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    
    return books_to_return

@app.get("/books/{book_author}/")
async def read_author_category_by_query(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and \
            book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    
    return books_to_return

@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)

@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
            BOOKS[i] = updated_book
            

@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
            BOOKS.pop(i)
            break
        
#EXERCÍCIO 1:
@app.get("/books/all_books_one_author")
async def all_books_one_author(author: str): 
    books_to_return = []
    for i in range(len(BOOKS)):
        if BOOKS[i].get('author').casefold() == author.casefold():
            books_to_return.append(BOOKS[i])
    
    return books_to_return

#EXERCÍCIO 2:
@app.get("/books/all_books_one_author_query/{author}")
async def all_books_one_author_query(author: str):
    books_to_return = []
    for i in range(len(BOOKS)):
        if BOOKS[i].get('author').casefold() == author.casefold():
            books_to_return.append(BOOKS[i])
            
    

# Conceito de parametro dinamico
#@app.get("/books/{dynamic_param}")
#async def read_all_books(dynamic_param: str):
#    return {'dynamic_param': dynamic_param}