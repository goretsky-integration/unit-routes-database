# Unit's routes Database

Сервис хранит информацию о всех подключенных юнитах,
а также информацию о маршрутах отчетов/уведомлений.

---

### Терминология:

- Unit - точка продаж/пиццерия.
- Chat ID - уникальный идентификатор чата в Telegram.
- Маршрут - связка chat ID, юнита и типа отчета.

---

## API Reference

- [Units](#units)
    - [Get units list](#get-all-units)
    - [Get unit by name](#get-unit-by-name)
    - [Get regions list](#get-all-regions)
- [Telegram chats](#telegram-chats)
    - [Get Telegram chats list](#get-all-telegram-chats)
    - [Create Telegram chat](#create-telegram-chat)
    - [Get chat types](#get-all-chat-types)
    - [Get Telegram chat detail](#get-telegram-chat)
    - [Update Telegram chat](#update-telegram-chat)
- [Report types](#report-types)
    - [Get report types](#get-all-report-types)
    - [Get statistics report types](#get-all-statistics-report-types)
- [Report routes](#report-routes)
    - [Get report routes units](#get-report-routes-units)
    - [Get report routes Telegram chats](#get-report-routes-telegram-chats)
    - [Create report route](#create-report-route)
    - [Delete report route](#delete-report-type)

### Units

#### Get all units

```http request
  GET /units/
```

| Query Parameter | Type  | Description                  |
|:----------------|:------|:-----------------------------|
| `limit`         | `int` | **Optional**. Default is 100 |
| `offset`        | `int` | **Optional**. Default is 0   |

#### Response

```json
{
  "units": [
    {
      "id": 1,
      "name": "Москва 1-1",
      "uuid": "b8e7c2a9-563f-4011-b531-3974efc36a48",
      "office_manager_account_name": "om_account_msk_1",
      "dodo_is_api_account_name": "api_account_msk_1",
      "region": "Москва 1"
    }
  ],
  "is_end_of_list_reached": true
}
```

---

#### Get unit by name

```http request
  GET /units/name/${unit_name}/
```

| Path Parameter | Type     | Description             |
|:---------------|:---------|:------------------------|
| `unit_name`    | `string` | **Required**. Unit name |

#### Response

```json
{
  "id": 1,
  "name": "Москва 1-1",
  "uuid": "b8e7c2a9-563f-4011-b531-3974efc36a48",
  "office_manager_account_name": "om_account_msk_1",
  "dodo_is_api_account_name": "api_account_msk_1",
  "region": "Москва 1"
}
```

---

#### Get all regions

```http request
  GET /units/regions/
```

| Query Parameter | Type  | Description                  |
|:----------------|:------|:-----------------------------|
| `limit`         | `int` | **Optional**. Default is 100 |
| `offset`        | `int` | **Optional**. Default is 0   |

#### Response

```json
{
  "regions": [
    {
      "id": 1,
      "name": "Москва 1"
    }
  ],
  "is_end_of_list_reached": true
}
```

---

### Telegram chats

#### Get all Telegram chats

```http request
GET /telegram-chats/
```

| Query Parameter | Type  | Description                  |
|:----------------|:------|:-----------------------------|
| `limit`         | `int` | **Optional**. Default is 100 |
| `offset`        | `int` | **Optional**. Default is 0   |

#### Response

```json
{
  "telegram_chats": [
    {
      "title": "Eldos",
      "chat_id": 123456
    }
  ],
  "is_end_of_list_reached": true
}
```

---

#### Create Telegram chat

```http request
POST /telegram-chats/
```

#### Body

```json
{
  "chat_id": 123456,
  "type": "PRIVATE",
  "title": "Eldos",
  "username": null
}
```

| Body       | Type     | Description                              |
|:-----------|:---------|:-----------------------------------------|
| `chat_id`  | `int`    | User/Group Telegram ID                   |
| `type`     | `enum`   | Choices: `PRIVATE`/`GROUP`               |
| `title`    | `string` | Chat title                               |
| `username` | `string` | **Optional**. This field may be omitted. |

#### Response status codes:

- 201 - Created.
- 400 - Invalid field in the body.
- 409 - Chat already exists.

---

#### Get all chat types

```http request
GET /telegram-chats/chat-types/
```

#### Response

```json
[
  "PRIVATE",
  "GROUP"
]
```

---

#### Get Telegram chat

```http request
GET /telegram-chats/${chat_id}/
```

| Path Parameter | Type  | Description      |
|:---------------|:------|:-----------------|
| `chat_id`      | `int` | Telegram chat ID |

#### Response

```json
{
  "chat_id": 12345,
  "username": "",
  "title": "hello",
  "type": "Private"
}
```

---

#### Update Telegram chat

```http request
PUT /telegram-chats/${chat_id}/
```

| Path Parameter | Type  | Description      |
|:---------------|:------|:-----------------|
| `chat_id`      | `int` | Telegram chat ID |

#### Response status codes:

- 204 - Updated.
- 400 - Invalid request.
- 404 - Chat not found.

---

### Report types

#### Get all report types

```http request
GET /report-types/
```

| Query Parameter | Type  | Description                  |
|:----------------|:------|:-----------------------------|
| `limit`         | `int` | **Optional**. Default is 100 |
| `offset`        | `int` | **Optional**. Default is 0   |

#### Response

```json
{
  "report_types": [
    {
      "id": 16,
      "name": "CANCELED_ORDERS",
      "verbose_name": "Отмены заказов"
    }
  ],
  "is_end_of_list_reached": false
}
```

---

#### Get all statistics report types

```http request
GET /report-types/statistics/
```

| Query Parameter | Type  | Description                  |
|:----------------|:------|:-----------------------------|
| `limit`         | `int` | **Optional**. Default is 100 |
| `offset`        | `int` | **Optional**. Default is 0   |

#### Response

```json
{
  "report_types": [
    {
      "id": 777,
      "name": "BONUS_SYSTEM",
      "verbose_name": "Бонусная система"
    }
  ],
  "is_end_of_list_reached": true
}
```

---

### Report routes

#### Get report routes units

```http request
GET /report-routes/units/
```

| Query Parameter  | Type  | Description                  |
|:-----------------|:------|:-----------------------------|
| `chat_id`        | `int` | Telegram chat ID             |
| `report_type_id` | `int` | Report type ID               |
| `limit`          | `int` | **Optional**. Default is 100 |
| `offset`         | `int` | **Optional**. Default is 0   |

#### Response

```json
{
  "unit_ids": [
    1,
    2,
    3
  ],
  "is_end_of_list_reached": true
}
```

---

#### Get report routes telegram chats

```http request
GET /report-routes/telegram-chats/
```

| Query Parameter  | Type  | Description                  |
|:-----------------|:------|:-----------------------------|
| `unit_id`        | `int` | Unit ID                      |
| `report_type_id` | `int` | Report type ID               |
| `limit`          | `int` | **Optional**. Default is 100 |
| `offset`         | `int` | **Optional**. Default is 0   |

#### Response

```json
{
  "chat_ids": [
    1,
    2,
    3
  ],
  "is_end_of_list_reached": true
}
```

---

#### Create report route

```http request
POST /report-routes/
```

#### Body

```json
{
  "report_type_id": 0,
  "chat_id": 0,
  "unit_ids": [
    1,
    2,
    3
  ]
}
```

#### Response status codes

- 201 - Created
- 400 - Bad request
- 403 - Permission to units/report type denied
- 404 - Chat/report type/units do not exist
- 409 - Report type already exists

---

#### Delete report type

```http request
DELETE /report-routes/
```

| Query Parameter  | Type        | Description      |
|:-----------------|:------------|:-----------------|
| `chat_id`        | `int`       | Chat ID          |
| `report_type_id` | `int`       | Report type ID   |
| `unit_ids`       | `list[int]` | List of unit IDs |

#### Response status codes

- 204 - Deleted
