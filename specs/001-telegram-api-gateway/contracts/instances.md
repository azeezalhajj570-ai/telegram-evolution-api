# Contract: Instances API

Base path: `/instances`
All endpoints require `X-API-Key` header.

---

## Create Instance

`POST /instances`

**Request**:
```json
{
  "name": "My Work Account"
}
```

**Response** `201`:
```json
{
  "id": "uuid",
  "name": "My Work Account",
  "phone_number": null,
  "status": "pending",
  "created_at": "2026-05-16T00:00:00Z",
  "updated_at": "2026-05-16T00:00:00Z"
}
```

**Errors**: `422` validation error

---

## List Instances

`GET /instances`

**Response** `200`:
```json
{
  "instances": [
    {
      "id": "uuid",
      "name": "My Work Account",
      "phone_number": "+5511999999999",
      "status": "connected",
      "created_at": "2026-05-16T00:00:00Z",
      "updated_at": "2026-05-16T00:00:00Z"
    }
  ]
}
```

---

## Get Instance

`GET /instances/{id}`

**Response** `200`: Single instance object (same shape as list item)

**Errors**: `404` instance not found

---

## Delete Instance

`DELETE /instances/{id}`

**Response** `204`: No content

**Errors**: `404` instance not found
