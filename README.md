## Configurações

- Se a fonte de dados é o arquivo de dados `books.csv`, copiar o arquivo para este local. 
- Criar o arquivo .env na raiz do projeto

```
DATABASE_PATH=mockdata/books.csv
PAGE_SIZE=10
```

## Pre-requisitos

- poetry
- python >=3.12

## Instalar 

Para instalar a aplicação em modo produção: 

```
poetry install
```

Para instalar em modo desenvolvimento:

```
poetry install -G dev
```

## Iniciar em desenvolvimento

```
poe servedev
```


## para obter o token JWT

Efetuar uma request no seguinte formato

```
POST /v1/api/token

{"username": "n", "password": "p"}
```

