"""
Este arquivo é o responsável por criar a conexão com o banco de dados e por configurar a base de onde as suas model classes (tabelas) vão herdar.

É um setup central que você vai importar em outras partes do seu código (por exemplo, nos arquivos de Models e Repositories).
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

"""
O que são?

create_engine → Cria a conexão com o banco de dados.

declarative_base → Cria uma classe base para os modelos (tabelas).

sessionmaker → Cria um gerador de sessões de banco (sessões que você usará para fazer queries, inserts, updates, deletes etc).
"""

SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
"""
Explicação:

Você está usando SQLite, que é um banco de dados local, baseado em arquivo.

'sqlite:///./todos.db' significa:

sqlite:// → Protocolo.

./todos.db → Banco salvo no diretório atual do projeto (na raiz).

Se fosse PostgreSQL, por exemplo, seria algo como:
postgresql://usuario:senha@localhost/nome_do_banco
"""

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={'check_same_thread': False}
) 
"""
Explicação:

engine → É o objeto que representa a conexão real com o banco. Toda comunicação SQL passa por ele.

connect_args={'check_same_thread': False} → Isso é uma exigência específica do SQLite.

Por padrão o SQLite só permite que a conexão seja usada na mesma thread em que ela foi criada.

Como o FastAPI pode usar múltiplas threads (por causa da natureza assíncrona dele), você precisa desabilitar essa checagem.
"""

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""
Explicação:

sessionmaker → Cria uma "fábrica de sessões" para interagir com o banco.

autocommit=False	Você controla quando o commit acontece (normalmente via db.commit())

autoflush=False	Evita que o SQLAlchemy envie dados para o banco automaticamente antes de cada query

bind=engine	Liga (conecta) essa sessão ao seu engine que aponta para o SQLite
"""

Base = declarative_base()

"""
Explicação:

Toda tabela que você for criar no SQLAlchemy vai herdar de Base.

Ou seja:
Base é o que conecta suas classes Python com o banco de dados real.
"""