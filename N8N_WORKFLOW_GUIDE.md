# n8n Workflow Guide: Auto QR Code Sender

## Overview

This workflow automatically:
1. Creates a new WhatsApp instance
2. Generates QR code
3. Sends QR code via your connected WhatsApp instance
4. Checks connection status every minute
5. Sends up to 10 QR codes (refreshing each minute)
6. Stops when device is connected or max attempts reached

---

## Setup Instructions

### Method 1: Import JSON (Easiest)

1. Open n8n
2. Click **"+"** to create new workflow
3. Click **"..." menu** → **"Import from File"**
4. Upload `n8n_workflow_qr_sender.json`
5. Done! Skip to "Configuration" section

### Method 2: Manual Creation

Follow the workflow structure below.

---

## Workflow Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  [Webhook] → [Create Instance] → [Connect & Get QR]            │
│       ↓                                                         │
│  [Set Variables] → [Check Status] → [Is Connected?]            │
│                                         ↓              ↓        │
│                                   YES: [Respond]  NO: Continue  │
│                                                         ↓        │
│                                            [Max Attempts?]      │
│                                              ↓           ↓       │
│                                        YES: [Respond] NO: Send  │
│                                                         ↓        │
│                          [Send QR] → [Wait 1min] → [Increment]  │
│                                ↑                        ↓        │
│                                └────── [Refresh QR] ← Loop      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Node Configuration

### 1. Webhook Trigger

**Type:** Webhook
**Method:** POST
**Path:** `create-whatsapp-instance`
**Response Mode:** "Using 'Respond to Webhook' Node"

**Test URL:** `http://your-n8n-url/webhook/create-whatsapp-instance`

---

### 2. Create Instance

**Type:** HTTP Request
**Method:** POST
**URL:** `https://chatsheros.uazapi.com/instance/create`

**Headers:**
```
admintoken: TPWVDMxqpcsBpKahh0B3ec1f4V8OVy1GvRCDunxHzilvmZxAv8
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "name": "={{ 'instance_' + $now.toUnixInteger() }}"
}
```

---

### 3. Connect & Get QR

**Type:** HTTP Request
**Method:** POST
**URL:** `https://chatsheros.uazapi.com/instance/connect`

**Headers:**
```
token: ={{ $json.token }}
Content-Type: application/json
```

**Body:** `{}` (empty JSON object)

---

### 4. Set Variables

**Type:** Set
**Mode:** Manual Mapping

**Fields:**
```javascript
new_instance_token: {{ $('Create Instance').item.json.token }}
new_instance_id: {{ $('Create Instance').item.json.instance.id }}
recipient_phone: {{ $('Webhook').item.json.body.phone }}
qr_code: {{ $json.instance.qrcode }}
attempt_count: 1
connected_instance_token: f5b12fac-c0ce-4c10-92eb-e24dc138230c
```

---

### 5. Check Instance Status

**Type:** HTTP Request
**Method:** GET
**URL:** `https://chatsheros.uazapi.com/instance/status`

**Headers:**
```
token: {{ $('Set Variables').item.json.new_instance_token }}
Content-Type: application/json
```

---

### 6. Is Connected?

**Type:** IF
**Condition:**
```
{{ $json.instance.status }} equals "connected"
```

**Outputs:**
- **True:** → Respond: Connected
- **False:** → Max Attempts Reached?

---

### 7. Respond: Connected

**Type:** Respond to Webhook
**Response Mode:** JSON

**Response Body:**
```json
{
  "success": true,
  "message": "Your device has been connected!",
  "instance_id": "={{ $('Set Variables').item.json.new_instance_id }}",
  "status": "connected"
}
```

---

### 8. Max Attempts Reached?

**Type:** IF
**Condition:**
```
{{ $('Set Variables').item.json.attempt_count }} >= 10
```

**Outputs:**
- **True:** → Respond: Max Attempts
- **False:** → Send QR via WhatsApp

---

### 9. Respond: Max Attempts

**Type:** Respond to Webhook
**Response Mode:** JSON

**Response Body:**
```json
{
  "success": false,
  "message": "Maximum attempts reached. QR code expired.",
  "attempts": "={{ $('Set Variables').item.json.attempt_count }}",
  "last_status": "={{ $('Check Instance Status').item.json.instance.status }}"
}
```

---

### 10. Send QR via WhatsApp

**Type:** HTTP Request
**Method:** POST
**URL:** `https://chatsheros.uazapi.com/send/media`

**Headers:**
```
token: {{ $('Set Variables').item.json.connected_instance_token }}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "number": "={{ $('Set Variables').item.json.recipient_phone }}",
  "image": "={{ $('Check Instance Status').item.json.instance.qrcode }}",
  "caption": "={{ '🔐 WhatsApp QR Code - Attempt ' + $('Set Variables').item.json.attempt_count + '/10\\n\\nScan this code with your WhatsApp to connect.\\n\\nThis code will refresh in 1 minute.' }}"
}
```

---

### 11. Wait 1 Minute

**Type:** Wait
**Time:** 60 seconds

---

### 12. Increment Counter

**Type:** Set
**Mode:** Manual Mapping

**Fields:**
```javascript
attempt_count: {{ $('Set Variables').item.json.attempt_count + 1 }}
new_instance_token: {{ $('Set Variables').item.json.new_instance_token }}
new_instance_id: {{ $('Set Variables').item.json.new_instance_id }}
recipient_phone: {{ $('Set Variables').item.json.recipient_phone }}
connected_instance_token: {{ $('Set Variables').item.json.connected_instance_token }}
```

---

### 13. Refresh QR Code

**Type:** HTTP Request
**Method:** POST
**URL:** `https://chatsheros.uazapi.com/instance/connect`

**Headers:**
```
token: {{ $json.new_instance_token }}
Content-Type: application/json
```

**Body:** `{}` (empty)

---

### 14. Loop Back

**Type:** Merge
**Mode:** Choose Branch
**Output:** Input 1

**Connect output to:** Check Instance Status node

---

## Configuration

After importing, update these values:

### 1. Connected Instance Token
In **"Set Variables"** node, change:
```
connected_instance_token: f5b12fac-c0ce-4c10-92eb-e24dc138230c
```
(This is already your connected instance, so it's ready!)

### 2. Admin Token
In **"Create Instance"** node headers:
```
admintoken: TPWVDMxqpcsBpKahh0B3ec1f4V8OVy1GvRCDunxHzilvmZxAv8
```
(Already set, no change needed)

---

## How to Use

### 1. Activate Workflow
Click **"Active"** toggle in top-right corner

### 2. Get Webhook URL
Copy the webhook URL from the Webhook node

### 3. Make Request

**Using cURL:**
```bash
curl -X POST http://your-n8n-url/webhook/create-whatsapp-instance \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5511999999999"
  }'
```

**Using Postman:**
```
POST http://your-n8n-url/webhook/create-whatsapp-instance

Body (JSON):
{
  "phone": "5511999999999"
}
```

**Using Python:**
```python
import requests

response = requests.post(
    'http://your-n8n-url/webhook/create-whatsapp-instance',
    json={'phone': '5511999999999'}
)

print(response.json())
```

### 4. What Happens Next

1. **Instance Created:** New WhatsApp instance is created
2. **QR Sent:** QR code sent to the phone number you provided
3. **Loop Starts:** Every minute:
   - Checks if WhatsApp was connected
   - If connected → Responds with success message
   - If not connected → Sends new QR code
4. **Max 10 Attempts:** After 10 QR codes, workflow stops

---

## Example Responses

### Success (Device Connected)
```json
{
  "success": true,
  "message": "Your device has been connected!",
  "instance_id": "r48e075136cf887",
  "status": "connected"
}
```

### Failure (Max Attempts)
```json
{
  "success": false,
  "message": "Maximum attempts reached. QR code expired.",
  "attempts": 10,
  "last_status": "connecting"
}
```

---

## Phone Number Format

**Important:** Phone number must include country code, NO "+" sign:

✅ Correct:
- `5511999999999` (Brazil)
- `14155551234` (USA)
- `447911123456` (UK)

❌ Incorrect:
- `+5511999999999` (has +)
- `11999999999` (missing country code)
- `(11) 99999-9999` (has formatting)

---

## Customization Options

### Change Wait Time
In **"Wait 1 Minute"** node:
```
amount: 60  // Change to 30 for 30 seconds, 120 for 2 minutes, etc.
unit: seconds
```

### Change Max Attempts
In **"Max Attempts Reached?"** node:
```
{{ $('Set Variables').item.json.attempt_count }} >= 10
```
Change `10` to your desired max attempts

### Customize Caption
In **"Send QR via WhatsApp"** node, edit the caption field:
```javascript
{{ '🔐 Your custom message - Attempt ' + $('Set Variables').item.json.attempt_count + '/10' }}
```

---

## Troubleshooting

### Issue: "WhatsApp disconnected" error
**Solution:** Make sure your connected instance (f5b12fac-c0ce-4c10-92eb-e24dc138230c) is still connected. Check status:
```bash
curl https://chatsheros.uazapi.com/instance/status \
  -H "token: f5b12fac-c0ce-4c10-92eb-e24dc138230c"
```

### Issue: Workflow doesn't loop
**Solution:** Make sure the "Loop Back" Merge node connects back to "Check Instance Status"

### Issue: QR code not sending
**Solution:**
1. Verify recipient phone number format (no + sign, with country code)
2. Check that connected instance token is correct
3. Test sending manually first

### Issue: "Missing token" error
**Solution:** Check that expressions are correctly referencing previous nodes using `$('Node Name').item.json.field`

---

## Testing Individual Nodes

You can test each node separately:

1. **Test Instance Creation:**
   - Use Execute Node on "Create Instance"
   - Should return instance ID and token

2. **Test QR Generation:**
   - Execute "Connect & Get QR"
   - Should return base64 QR code

3. **Test Sending:**
   - Execute "Send QR via WhatsApp"
   - Check recipient phone for QR code image

---

## Production Tips

1. **Error Handling:** Add an "On Error" workflow to catch failures
2. **Logging:** Add a "Spreadsheet" or "Database" node to log all attempts
3. **Notifications:** Add a "Telegram" or "Email" node to notify when device connects
4. **Rate Limiting:** Add a "Rate Limit" node before webhook to prevent abuse
5. **Validation:** Add an "IF" node after webhook to validate phone number format

---

## Your Instance Details (Already Configured)

```
Server URL: https://chatsheros.uazapi.com
Instance Token: f5b12fac-c0ce-4c10-92eb-e24dc138230c
Connected Number: 601130842973
Status: connected ✅
```

This instance is used to **SEND** the QR codes. The workflow creates **NEW** instances whose QR codes are sent via this connected instance.

---

## Support

If you encounter issues:
1. Check n8n execution logs (click on workflow execution)
2. Verify all tokens and phone numbers
3. Test API endpoints manually using curl/Postman
4. Check that connected instance is still active
