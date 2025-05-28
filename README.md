# Sistema de Reservas de Salas :green_book:

Este serviço RESTful é responsável por gerenciar o agendamento e controle de reservas de salas. Ele garante a disponibilidade das salas, prevenindo conflitos de horário e validando as entidades envolvidas (turmas e professores) através da integração com o microserviço de **Sistema de Gerenciamento Escolar**.

Esta API depende da **API de Gerenciamento Escolar (School System)**, que deve estar em execução e exposta localmente. A comunicação entre os serviços ocorre via requisições HTTP REST, para validar:
- Verifica se a **turma** existe via `GET /turmas/{id}`
- Verifica se o **professor** existe via `GET /professores/{id}`
- *Se a API-SchoolSystem estiver indisponível ou os dados não forem encontrados, a API retorna erro 400 Bad Request*


## 🔧 Tecnologias Utilizadas
* Python 3.11
* FastAPI
* SQLAlchemy
* Docker & Docker Compose

## 🚀 Como Executar o Projeto

### Pré-requisitos

* [Docker](https://www.docker.com/) instalado
* Python 3.x
* pip (gerenciador de pacotes do Python)

### Passo a Passo

1. Clone o repositório:
   ```bash
   git clone https://github.com/gilopesr/reserva-de-salas.git
   cd Reserva

2. Inicie os containers:
   ```bash
   docker-compose up --build


## Acesse a documentação:

    * A API estará disponível em `http://localhost:5000/reservas` (ou na porta e host configurados).
   
### Funcionalidades Principais:

* **Criação de Reservas:** Agendamento de salas para turmas e professores específicos, em data e horário definidos.
* **Consulta de Reservas:** listagem de todas as reservas ou buscar uma reserva por seu id.
* **Atualização de Reservas:** Possibilita modificar os detalhes de uma reserva existente.
* **Exclusão de Reservas:** Permite remover reservas de salas.

## 🧩 Integração com Microserviços
Este serviço opera como parte de um ecossistema de microserviços, interagindo com a API-SchoolSystem:

* **API-SchoolSystem:** Responsável por dados de turmas e professores.

* **Serviço de Reservas:** Gerencia unicamente a lógica de agendamento de salas.

## Estrutura do Projeto

A estrutura do projeto é a seguinte:  📂

    ```
    ├── Reserva/
    |   ├── controllers/
    |   │   ├── __init__.py
    |   │   └── reserva_route.py
    |   ├── models/
    |   │   ├── __init__.py
    |   │   └── reserva_model.py
    |   ├── config.py
    |   ├── app.py   
    |   ├── database.py  
    |   ├── dockerfile
    |   ├── requirements.txt
    |   └── docker-compose.yml
    ├── LICENCE
    └── README.md
    ```


## Endpoints da API (Rotas)

A API de Reservas de Salas expõe os seguintes endpoints:

### Reservas (`/reservas`)

#### `POST /reservas`

Cria uma nova reserva de sala.

* **Corpo da Requisição (JSON):**
    ```json
    {
        "turma_id": 101,          // ID da turma (inteiro, deve existir na API-SchoolSystem)
        "id_professor": 5,        // ID do professor (inteiro, deve existir na API-SchoolSystem)
        "sala": "Laboratório C",  // Nome da sala (string)
        "data": "2025-06-15",     // Data da reserva (string no formato "YYYY-MM-DD")
        "hora_inicio": "09:00",   // Hora de início (string no formato "HH:MM")
        "hora_fim": "10:30"       // Hora de fim (string no formato "HH:MM")
    }
    ```
* **Respostas:**
    * `201 OK`: Reserva criada com sucesso. Retorna os detalhes da reserva criada.
    * `400 Bad Request`: Dados inválidos (campos faltando, formato incorreto, ID inválido, hora de início >= hora de fim).
    * `400 Bad Request`: Turma ou professor não encontrados/API-SchoolSystem indisponível.
    * `409 Conflict`: Conflito de horário para a sala e período especificados.

#### `GET /reservas`

Lista todas as reservas existentes no sistema.

* **Respostas:**
    * `200 OK`: Retorna uma lista de objetos de reserva.
    ```json
    [
        {
            "id_reserva": 1,
            "turma_id": 101,
            "professor": "João Silva",
            "sala": "Laboratório C",
            "data": "2025-06-15",
            "hora_inicio": "09:00",
            "hora_fim": "10:30"
        }
    ]
    ```

#### `GET /reservas/<int:id_reserva>`

Obtém os detalhes de uma reserva específica pelo seu ID.

* **Parâmetros de URL:**
    * `id_reserva` (inteiro): O ID único da reserva.
* **Respostas:**
    * `200 OK`: Retorna o objeto da reserva.
    * `404 Not Found`: Reserva não encontrada.

#### `PUT /reservas/<int:id_reserva>`

Atualiza uma reserva existente pelo seu ID. Apenas os campos fornecidos no corpo da requisição serão atualizados.

* **Parâmetros de URL:**
    * `id_reserva` (inteiro): O ID único da reserva a ser atualizada.
* **Corpo da Requisição (JSON):**
    ```json
    {
        "sala": "Auditório Principal",
        "hora_fim": "12:00"
        // Outros campos como "turma_id", "id_professor", "data", "hora_inicio" podem ser incluídos
    }
    ```
* **Respostas:**
    * `200 OK`: Reserva atualizada com sucesso. Retorna os detalhes da reserva atualizada.
    * `400 Bad Request`: Dados inválidos (formato incorreto, ID inválido, hora de início >= hora de fim com os novos valores).
    * `400 Bad Request`: Turma ou professor não encontrados/API-SchoolSystem indisponível (se `turma_id` ou `id_professor` foram atualizados).
    * `404 Not Found`: Reserva não encontrada.
    * `409 Conflict`: Conflito de horário com outra reserva existente.

#### `DELETE /reservas/<int:id_reserva>`

Deleta uma reserva existente pelo seu ID.

* **Parâmetros de URL:**
    * `id_reserva` (inteiro): O ID único da reserva a ser deletada.
* **Respostas:**
    * `200 OK`: Reserva deletada com sucesso.
    * `404 Not Found`: Reserva não encontrada.

## Licença

[MIT License](https://opensource.org/licenses/MIT)
