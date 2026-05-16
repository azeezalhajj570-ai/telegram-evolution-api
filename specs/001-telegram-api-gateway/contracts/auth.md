# Contract: Authentication API

Base path: `/instances/{id}/auth`
All endpoints require `X-API-Key` header.

---

## Send Login Code

`POST /instances/{id}/auth/send-code`

**Request**:
```json
{
  "phone_number": "+5511999999999"
}
```

**Response** `200`:
```json
{
  "status": "code_sent",
  "phone_number": "+5511999999999"
}
```

**Errors**:
- `400` instance already connected
- `404` instance not found
- `422` invalid phone number format

---

## Verify OTP

`POST /instances/{id}/auth/verify-code`

**Request**:
```json
{
  "code": "12345"
}
```

**Response** `200` (when 2FA not required):
```json
{
  "status": "authenticated",
  "twofa_required": false
}
```

**Response** `200` (when 2FA required):
```json
{
  "status": "awaiting_2fa",
  "twofa_required": true
}
```

**Errors**:
- `400` invalid code / no active auth flow / wrong flow state
- `404` instance not found

---

## Submit 2FA Password

`POST /instances/{id}/auth/2fa`

**Request**:
```json
{
  "password": "my_2fa_password"
}
```

**Response** `200`:
```json
{
  "status": "authenticated"
}
```

**Errors**:
- `400` wrong password / no 2fa flow active
- `404` instance not found

---

## Connect Instance

`POST /instances/{id}/auth/connect`

**Request**: (empty body)

**Response** `200`:
```json
{
  "status": "connected"
}
```

**Errors**:
- `400` no saved session / already connected
- `404` instance not found

---

## Disconnect Instance

`POST /instances/{id}/auth/disconnect`

**Request**: (empty body)

**Response** `200`:
```json
{
  "status": "disconnected"
}
```

**Errors**:
- `400` not currently connected
- `404` instance not found
