# UAZAPI WhatsApp API Documentation

## Base URL
```
https://chatsheros.uazapi.com
```

## Authentication

The API uses two types of tokens:
- **Admin Token**: Used for creating instances
- **Instance Token**: Returned when creating an instance, used for all instance operations

## API Endpoints

### 1. Create Instance

Creates a new WhatsApp instance.

**Endpoint:** `POST /instance/create`

**Headers:**
```json
{
  "Content-Type": "application/json",
  "admintoken": "YOUR_ADMIN_TOKEN"
}
```

**Request Body:**
```json
{
  "name": "instance_name"
}
```

**Response:**
```json
{
  "connected": false,
  "instance": {
    "id": "r48e075136cf887",
    "token": "e4ab9e0e-0781-4627-aa88-647d06e8ab03",
    "status": "disconnected",
    "qrcode": "",
    "name": "instance_name",
    "profileName": "",
    "profilePicUrl": "",
    "isBusiness": false,
    "plataform": "",
    "systemName": "uazapiGO",
    "created": "2025-11-07T01:48:53.905Z",
    "updated": "2025-11-07T01:48:53.905Z"
  },
  "loggedIn": false,
  "response": "Instance created successfully",
  "token": "e4ab9e0e-0781-4627-aa88-647d06e8ab03"
}
```

**Important Fields:**
- `instance.id`: Instance ID
- `token`: Instance token (save this for subsequent requests)

---

### 2. Connect Instance / Get QR Code

Starts the connection process and retrieves the QR code.

**Endpoint:** `POST /instance/connect`

**Headers:**
```json
{
  "Content-Type": "application/json",
  "token": "INSTANCE_TOKEN"
}
```

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "connected": true,
  "instance": {
    "id": "r2a7e2cc35375c9",
    "token": "ea130f46-79a9-4846-97f8-37666ca8869e",
    "status": "connecting",
    "qrcode": "data:image/png;base64,iVBORw0KGgoAAAANS...",
    "name": "instance_name",
    "status": "connecting"
  },
  "loggedIn": false
}
```

**Important Fields:**
- `instance.qrcode`: Base64-encoded PNG image of the QR code
- `instance.status`: Connection status (connecting, connected, disconnected)
- `connected`: Boolean indicating connection state

**QR Code Format:**
The QR code is returned as a data URL: `data:image/png;base64,<base64_data>`

---

### 3. Get Instance Status

Retrieves the current status of an instance (also includes QR code if available).

**Endpoint:** `GET /instance/status`

**Headers:**
```json
{
  "Content-Type": "application/json",
  "token": "INSTANCE_TOKEN"
}
```

**Response:**
```json
{
  "instance": {
    "id": "r2a7e2cc35375c9",
    "token": "ea130f46-79a9-4846-97f8-37666ca8869e",
    "status": "connecting",
    "qrcode": "data:image/png;base64,iVBORw0KGgoAAAANS...",
    "name": "instance_name",
    "profileName": "",
    "profilePicUrl": ""
  }
}
```

---

## Usage Flow

1. **Create Instance**
   ```bash
   POST /instance/create
   Headers: admintoken
   Body: {"name": "my_instance"}
   ```
   Save the `token` from the response.

2. **Connect & Get QR Code**
   ```bash
   POST /instance/connect
   Headers: token (instance token from step 1)
   Body: {}
   ```
   Extract `instance.qrcode` from response.

3. **Scan QR Code**
   - Open WhatsApp on your mobile device
   - Go to Settings > Linked Devices
   - Tap "Link a Device"
   - Scan the QR code

4. **Check Status**
   ```bash
   GET /instance/status
   Headers: token (instance token)
   ```
   Monitor the `instance.status` field.

---

## Python Example

```python
import requests
import base64

BASE_URL = "https://chatsheros.uazapi.com"
ADMIN_TOKEN = "your_admin_token_here"

# 1. Create instance
response = requests.post(
    f"{BASE_URL}/instance/create",
    headers={'Content-Type': 'application/json', 'admintoken': ADMIN_TOKEN},
    json={'name': 'my_whatsapp'}
)
data = response.json()
instance_token = data['token']

# 2. Connect and get QR
response = requests.post(
    f"{BASE_URL}/instance/connect",
    headers={'Content-Type': 'application/json', 'token': instance_token},
    json={}
)
qr_data = response.json()['instance']['qrcode']

# 3. Save QR code as image
qr_base64 = qr_data.split(',')[1]  # Remove data:image/png;base64, prefix
with open('qr.png', 'wb') as f:
    f.write(base64.b64decode(qr_base64))

print("QR code saved to qr.png")
```

---

## Status Values

- `disconnected`: Instance created but not connected
- `connecting`: Connection in progress, QR code available
- `connected`: Successfully connected to WhatsApp

---

## Error Responses

### Missing Admin Token
```json
{
  "code": 401,
  "message": "Missing token.",
  "data": {}
}
```

### Invalid Payload
```json
{
  "error": "Missing Name or instanceName in payload"
}
```

### Already Connecting
```json
{
  "response": "Connection attempt in progress, please wait 2 minutes before trying again"
}
```

---

## Messaging Endpoints

### 4. Send Text Message

Send a text message via WhatsApp (requires connected instance).

**Endpoint:** `POST /send/text`

**Headers:**
```json
{
  "Content-Type": "application/json",
  "token": "INSTANCE_TOKEN"
}
```

**Request Body:**
```json
{
  "number": "5511999999999",
  "message": "Hello from UAZAPI!"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Message sent"
}
```

---

### 5. Send Media/Image

Send an image or media file via WhatsApp (can be used to send QR codes).

**Endpoint:** `POST /send/media`

**Headers:**
```json
{
  "Content-Type": "application/json",
  "token": "INSTANCE_TOKEN"
}
```

**Request Body:**
```json
{
  "number": "5511999999999",
  "image": "data:image/png;base64,iVBORw0KGgo...",
  "caption": "Scan this QR code"
}
```

**Note:** You can send the QR code from `POST /instance/connect` response directly using this endpoint.

---

## Sending QR Code via WhatsApp

To send a QR code to someone via WhatsApp:

```python
# 1. Create new instance and get QR
response = requests.post(
    f"{BASE_URL}/instance/create",
    headers={'admintoken': ADMIN_TOKEN},
    json={'name': 'new_instance'}
)
new_token = response.json()['token']

# 2. Get QR code
response = requests.post(
    f"{BASE_URL}/instance/connect",
    headers={'token': new_token},
    json={}
)
qr_base64 = response.json()['instance']['qrcode']

# 3. Send QR via another CONNECTED instance
response = requests.post(
    f"{BASE_URL}/send/media",
    headers={'token': CONNECTED_INSTANCE_TOKEN},
    json={
        'number': '5511999999999',
        'image': qr_base64,
        'caption': 'Scan this to connect WhatsApp'
    }
)
```

**Important:** You cannot send messages from a disconnected instance. You need an already-connected instance to send the QR code.

---

## Notes

- The instance token is required for all instance-specific operations
- Store the instance token securely
- QR codes expire and need to be regenerated if not scanned quickly
- You can check the status periodically to monitor connection progress
- **To send messages, the instance must be connected** (status: "connected")
- Phone numbers must include country code (e.g., "5511999999999" for Brazil)
