# API de acessibilidade em prateleiras

Backend em FastAPI para cadastrar produtos associados a tags, receber leituras do
sensor e devolver a áudio descrição correspondente. A API registra também tags
desconhecidas para que possam ser identificadas no histórico.

## Executar

Requer Python 3.10+ e MongoDB.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure a conexão por variáveis de ambiente (não coloque credenciais no código):

```bash
export MONGODB_URI="mongodb://localhost:27017"
export MONGODB_DATABASE="inclusive_catalog"
uvicorn app.main:app --reload
```

Para compatibilidade, `uvicorn main:app --reload` também funciona. A documentação
interativa fica em `http://127.0.0.1:8000/docs`; exemplos de requisição estão em
`test_main.http`.

## Regras de negócio

- Cada tag pode estar associada a no máximo um produto; o ID é removido de espaços
  nas pontas e convertido para maiúsculas.
- Uma leitura encontra o produto pela tag e devolve sua áudio descrição quando
  conhecida. Tags desconhecidas também são registradas, com estado `unknown`.
- O histórico guarda a identificação e o nome do produto no momento da leitura,
  mesmo que o produto seja alterado ou removido posteriormente.
- Listagens aceitam paginação (`skip`, `limit`); leituras podem ser filtradas por
  `tag_id`.
- A descrição em texto pode ser convertida em fala pelo dispositivo, ou usada para
  selecionar um áudio pré-gravado numa evolução do projeto. A API não reproduz áudio.

## Endpoints

| Método | Caminho | Uso |
|---|---|---|
| `POST` | `/api/v1/products` | Cadastrar produto e tag opcional |
| `GET` | `/api/v1/products` | Listar catálogo |
| `GET` | `/api/v1/products/{product_id}` | Consultar produto |
| `PATCH` | `/api/v1/products/{product_id}` | Atualizar campos do produto |
| `DELETE` | `/api/v1/products/{product_id}` | Remover produto |
| `POST` | `/api/v1/readings` | Registrar leitura e obter áudio descrição |
| `GET` | `/api/v1/readings` | Consultar histórico de leituras |
