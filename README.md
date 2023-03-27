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
