# Sistema de Reservas de Salas

## Descrição da API

Este serviço RESTful é responsável por gerenciar o agendamento e controle de reservas de salas. Ele garante a disponibilidade das salas, prevenindo conflitos de horário e validando as entidades envolvidas (turmas e professores) através da integração com o microserviço de **Sistema de Gerenciamento Escolar**.

### Funcionalidades Principais:

* **Criação de Reservas:** Permite agendar uma sala para uma turma e professor específicos em uma data e período determinados.
* **Consulta de Reservas:** Possui endpoints para listar todas as reservas ou buscar uma reserva por seu identificador único.
* **Atualização de Reservas:** Possibilita modificar os detalhes de uma reserva existente.
* **Exclusão de Reservas:** Permite remover agendamentos de salas.

## Descrição do Ecossistema de Microsserviços

Este serviço opera como um componente especializado dentro de um ecossistema, colaborando com a **API-SchoolSystem** para gerenciar reservas de salas.

* **API-SchoolSystem (`https://github.com/brunaferreir/API-SchoolSystem`):** É a fonte autoritária para dados de entidades core como **turmas** e **professores**.
* **Serviço de Reservas de Salas (Este Serviço):** Foca exclusivamente na lógica de agendamento e disponibilidade de salas. Ele **não armazena** informações completas de turmas ou professores, apenas seus IDs e, no caso do professor, seu nome (que é obtido da `API-SchoolSystem` no momento da criação/atualização da reserva).

### Como este serviço se integra com a API-SchoolSystem:

1.  **Validação de Entidades:**
    * Quando uma reserva é criada ou atualizada, o Serviço de Reservas faz chamadas HTTP `GET` para a `API-SchoolSystem` (por exemplo, para `/api/turmas/{id}` e `/api/professores/{id}`) para verificar se o `turma_id` e o `id_professor` fornecidos são válidos e existem na base de dados da `API-SchoolSystem`.
    * O nome do professor é obtido da `API-SchoolSystem` e armazenado localmente na reserva para facilitar a consulta futura da reserva sem depender de uma nova chamada à API externa para o nome.
2.  **Acoplamento:**
    * Este serviço tem um acoplamento **fraco** em tempo de execução com a `API-SchoolSystem`. Ele depende da disponibilidade e do contrato da API externa para suas validações.
    * Em caso de indisponibilidade da `API-SchoolSystem` ou de validação falha (turma/professor não encontrados), o Serviço de Reservas retorna um erro `400 Bad Request`, indicando que a entidade referenciada não pôde ser validada.


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

---
