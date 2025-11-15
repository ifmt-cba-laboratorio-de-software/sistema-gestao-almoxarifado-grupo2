# TEMPLATE DOCUMENTAÇÃO 

# Sumário
* [1. Introdução](#1-introdução)
    * [1.1. Tecnologias](#11-tecnologias)
* [2. Inicializar a Aplicação ](#2-inicializar-a-aplicação)
* [3. Arquitetura da Aplicação](#3-arquitetura-da-aplicação)
* [Estrutura do Projeto](#estrutura-do-projeto)


## 1. Introdução 

### Projeto API PRODUTOS 
Este projeto foi desenvolvido com Python e com o framework Django RestFramework. Ele permite cadastrar produtos, buscar, atualizar e deletar.

## 1.1. Tecnologias

A API foi desenvolvida utilizando as seguintes tecnologias:

- [xxx](link)
- [IDE VSCODE](https://code.visualstudio.com/download)

---
# 2. Inicializar a Aplicação 
### Testando a API 

Os passos necessários para testar localmente são:

- Instalar as ferramentas necessárias
- Clonar o projeto 
  ```plaintext
        git clone xxxx
    ```
- Entrar no diretório
    ```
    cd xxx
    ```
- Executar o seguintes comandos na raiz do diretório


  - Instalar xxx
    ````
    xxxxx
    ````
  - Instalar xxx
    ````
    xxxxx
    ````
 


-----------------------------------------------
## 3. Arquitetura da aplicação

imagem x

## Funcionalidades

### Rotas

## Endpoints da API de Produtos

| Operação     | Método HTTP | Endpoint                    | Função                 |
|---------------|--------------|------------------------------|------------------------|
| Create        | POST         | `/api/produtos/`             | Criar produto          |
| Read All      | GET          | `/api/produtos/`             | Listar todos           |
| Read One      | GET          | `/api/produtos/{id}`         | Buscar por ID          |
| Read Filter   | GET          | `/api/produtos/?nome=X`      | Buscar por filtro      |
| Update        | PUT          | `/api/produtos/{id}`         | Atualizar produto      |
| Delete        | DELETE       | `/api/produtos/{id}`         | Deletar produto        |


1. **Criar Produto**  
- **Endpoint:** `POST /api/produtos/`  
- **Descrição:** Cria um novo produto no sistema.  
- **Request Body:**  
  ```json
  {
    "nome": "copo ",
    "descricao": "copo descartável de 180ml",
    "estoque": 50
  }
  ```
- **Resposta:**  
  ```json
  {
    "id": 1,
    "nome": "copo",
    "descricao": "copo descartável de 180ml",
    "estoque": 50,
    "createdAt": "2025-10-02"
  }
  ```

---

2. **Listar Todos os Produtos**  
- **Endpoint:** `GET /api/produtos/`  
- **Descrição:** Retorna a lista completa de produtos cadastrados.  
- **Resposta:**  
  ```json
  [
    {
      "id": 1,
      "nome": "copo",
      "descricao": "copo descartável de 180ml",
      "estoque": 50
    },
    {
      "id": 2,
      "nome": "papel A4",
      "descricao": "resma de papel A4",
      "estoque": 80
    }
  ]
  ```

---

3. **Buscar Produto por ID**  
- **Endpoint:** `GET /api/produtos/{id}`  
- **Descrição:** Retorna os detalhes de um produto específico pelo seu ID.  
- **Exemplo:**  
  `GET /api/produtos/1`  
- **Resposta:**  
  ```json
  {
    "id": 1,
    "nome": "copo",
    "descricao": "copo descartável de 180ml",
    "estoque": 50
  }
  ```

---

4. **Buscar Produto por Filtro (nome)**  
- **Endpoint:** `GET /api/produtos/?nome=copo`  
- **Descrição:** Filtra produtos pelo nome informado.  
- **Exemplo:**  
  `GET /api/produtos/?nome=copo`  
- **Resposta:**  
  ```json
  [
    {
      "id": 1,
      "nome": "copo",
      "descricao": "copo descartável de 180ml",
      "estoque": 50
    }
  ]
  ```

---

5. **Atualizar Produto**  
- **Endpoint:** `PUT /api/produtos/{id}`  
- **Descrição:** Atualiza as informações de um produto existente.  
- **Request Body:**  
  ```json
  {
    "nome": "copo",
    "descricao": "copo descartável de 300ml",
    "estoque": 30
  }
  ```
- **Resposta:**  
  ```json
  {
    "id": 1,
    "nome": "copo",
    "descricao": "copo descartável de 300ml",
    "estoque": 30,
    "updatedAt": "2025-10-02"
  }
  ```

---

6. **Deletar Produto**  
- **Endpoint:** `DELETE /api/produtos/{id}`  
- **Descrição:** Remove um produto do sistema com base no ID informado.  
- **Exemplo:**  
  `DELETE /api/produtos/1`  
- **Resposta:**  
  ```json
  {
    "mensagem": "Produto com ID 1 foi deletado com sucesso."
  }
  ```

---

## Configuração

### Dependências

As principais dependências do projeto incluem:

- **Express**: Framework para APIs.  
- **TypeScript**: Superconjunto de JavaScript com tipagem estática.  
- **Mongoose**: ORM para MongoDB.  
- **dotenv**: Gerenciamento de variáveis de ambiente.  
- **@genkit-ai/googleai**: Integração com a API do Google GenAI.  
- **cors**: Middleware para lidar com CORS.


## Design de código e organização das pastas

### Clean Architecture no Projeto

xxxxx

1. **xxxx**: Responsável por interagir com o usuário, como os controladores de API (`xxx`, `xxx`).
2. xxx
3. xxx

### xxxxx

A **xxx** é uma prática xxxxxxxx xxxxxxxxxx (`xxx`, `xxx`).

-------------
## Estrutura do Projeto
````
📂api-produtos
├── apiprodutosvenv/     (ambiente virtual)
├── configprojeto/       (configurações do projeto)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── api/                 (app)
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
└── manage.py

````