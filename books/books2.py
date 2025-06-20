from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from typing import Optional


#FastAPI usa o BaseModel do Pydantic para se comunicar com o corpo (body) da requisição HTTP automaticamente!

app = FastAPI()

class Book: 
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int
    
    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date
    

class BookRequest(BaseModel): #Body
    id: Optional[int] = Field(description = 'ID is not needed on create', default = None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=6)
    published_date: int = Field(mt=1999, lt=2025)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                'title': 'A new book',
                'author': 'Sara',
                'description': 'A new description of a book',
                'rating': 5,
                'published_date': 2016
            }
        }
    }
    
        
BOOKS = [
    Book(id = 1, title = 'Computer Science Pro', author = 'codingwithruby', description = 'A very nice book!', rating = 5, published_date=2018),
    Book(id = 2, title = 'Be fast with FastAPI', author = 'codingwithruby', description = 'A great book!', rating = 5, published_date=2018),
    Book(id = 3, title = 'Master Endpoints', author = 'codingwithruby', description = 'A awesome book!', rating = 5, published_date=2020),
    Book(id = 4, title = 'HP1', author = 'Author 1', description = 'Book description', rating = 2, published_date=2010),
    Book(id = 5, title = 'HP2', author = 'Author 2', description = 'Book description', rating = 3, published_date=2010),
    Book(id = 6, title = 'HP3', author = 'Author 3', description = 'Book description', rating = 1, published_date=2025)
]
    
    
@app.get("/books", status_code=status.HTTP_200_OK)
async def real_all_books():
    return BOOKS



@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=(0))):
    for book in BOOKS: 
        if book.id == book_id:
            return book
        
    raise HTTPException(status_code=404, detail='Item not found')
        
        
        
        
@app.get('/books/', status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(gt=0, lt=6)): 
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

@app.get('/books/published/', status_code=status.HTTP_200_OK)
async def read_book_by_published_date(book_published_date: int = Query(gt=1999, lt=2025)): 
    books_to_return = []
    for book in BOOKS:
        if book.published_date == book_published_date:
            books_to_return.append(book)
    
    return books_to_return
            

@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))
    
def find_book_id(book: Book):
    if len(BOOKS) > 0:
        book.id = BOOKS[-1].id + 1
    else:
        book.id = 1
    
    return book



@app.put('/books/update_book', status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')  
            
            
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')  