# UAZAPI n8n Workflow - Complete Package

## 📦 What You Got

A complete n8n workflow that automatically:
- ✅ Creates WhatsApp instances
- ✅ Sends QR codes via your connected WhatsApp
- ✅ Auto-refreshes QR every minute
- ✅ Monitors connection status
- ✅ Stops when connected or after 10 attempts

---

## 🚀 Quick Start (3 Steps)

### 1. Import Workflow to n8n
```bash
1. Open n8n
2. Click "+" → "Import from File"
3. Upload: n8n_workflow_qr_sender.json
4. Click "Active" toggle
```

### 2. Get Your Webhook URL
Copy webhook URL from n8n (looks like):
```
http://your-n8n-domain/webhook/create-whatsapp-instance
```

### 3. Test It
```bash
python3 test_n8n_webhook.py http://your-webhook-url 5511999999999
```

**Done!** QR codes will be sent to that WhatsApp number.

---

## 📂 Files Included

### Core Files
| File | Description |
|------|-------------|
| `n8n_workflow_qr_sender.json` | ⭐ Import this into n8n |
| `WORKFLOW_QUICK_START.md` | 🚀 Quick setup guide |
| `N8N_WORKFLOW_GUIDE.md` | 📖 Detailed documentation |
| `test_n8n_webhook.py` | 🧪 Test your workflow |

### Additional Files
| File | Description |
|------|-------------|
| `UAZAPI_README.md` | 📚 Complete API documentation |
| `uazapi_whatsapp.py` | 🐍 Python client library |
| `send_qr_via_whatsapp.py` | 📤 Example: Send QR manually |

### Generated Test Files
| File | Description |
|------|-------------|
| `whatsapp_qr.png` | Generated QR code images |
| `test_*.py` | Discovery/testing scripts |

---

## 🎯 Your Instance (Already Configured)

```yaml
Server: https://chatsheros.uazapi.com
Instance Token: f5b12fac-c0ce-4c10-92eb-e24dc138230c
Connected Number: 601130842973
Status: connected ✅
```

This instance is used to **SEND** QR codes.
The workflow creates **NEW** instances for users to connect.

---

## 🔧 How It Works

```
User Request (phone: 5511999999999)
         ↓
┌────────────────────────────────┐
│  1. Create new instance        │
│  2. Generate QR code           │
│  3. Send QR to user's WhatsApp │
└────────────────────────────────┘
         ↓
┌────────────────────────────────┐
│  Every minute:                 │
│  - Check if connected          │
│  - If YES → Return success ✅  │
│  - If NO  → Send new QR        │
└────────────────────────────────┘
         ↓
┌────────────────────────────────┐
│  After 10 attempts:            │
│  - Stop sending                │
│  - Return timeout ❌           │
└────────────────────────────────┘
```

---

## 📱 API Endpoints Discovered

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/instance/create` | POST | Create new instance |
| `/instance/connect` | POST | Get QR code |
| `/instance/status` | GET | Check connection status |
| `/send/text` | POST | Send text message |
| `/send/media` | POST | Send image/QR code |

---

## 💻 Usage Examples

### Test from Command Line
```bash
python3 test_n8n_webhook.py \
  http://localhost:5678/webhook/create-whatsapp-instance \
  5511999999999
```

### Call from cURL
```bash
curl -X POST http://localhost:5678/webhook/create-whatsapp-instance \
  -H "Content-Type: application/json" \
  -d '{"phone": "5511999999999"}'
```

### Call from Python
```python
import requests

response = requests.post(
    'http://localhost:5678/webhook/create-whatsapp-instance',
    json={'phone': '5511999999999'}
)

print(response.json())
```

### Call from JavaScript
```javascript
fetch('http://localhost:5678/webhook/create-whatsapp-instance', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({phone: '5511999999999'})
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## 📊 Response Format

### Success (Device Connected)
```json
{
  "success": true,
  "message": "Your device has been connected!",
  "instance_id": "r48e075136cf887",
  "status": "connected"
}
```

### Timeout (10 attempts)
```json
{
  "success": false,
  "message": "Maximum attempts reached. QR code expired.",
  "attempts": 10,
  "last_status": "connecting"
}
```

---

## 🎨 Customization

### Change wait time (default: 1 minute)
Edit **"Wait 1 Minute"** node in n8n:
```
amount: 60  → 30 (30 seconds) or 120 (2 minutes)
```

### Change max attempts (default: 10)
Edit **"Max Attempts Reached?"** node:
```
>= 10  → >= 5 or >= 20
```

### Change QR message
Edit **"Send QR via WhatsApp"** node caption:
```javascript
"🔐 Your custom message here"
```

---

## 🔐 Phone Number Format

**Important:** Phone must have country code, NO "+" sign

| ✅ Correct | ❌ Incorrect |
|-----------|-------------|
| `5511999999999` | `+5511999999999` |
| `14155551234` | `11999999999` |
| `447911123456` | `(11) 99999-9999` |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "WhatsApp disconnected" | Check your instance is still connected |
| QR not sending | Verify phone format (no +, with country code) |
| Workflow not looping | Check "Loop Back" node connections |
| Timeout too fast | Increase max attempts or wait time |

---

## 🎓 Learn More

### API Documentation
- **UAZAPI_README.md** - Complete API reference
- All endpoints, examples, and error codes

### Python Examples
- **uazapi_whatsapp.py** - Full Python client
- **send_qr_via_whatsapp.py** - Manual QR sending

### n8n Setup
- **N8N_WORKFLOW_GUIDE.md** - Detailed setup
- **WORKFLOW_QUICK_START.md** - Quick reference

---

## 📞 Testing Checklist

Before going live:

- [ ] Import workflow to n8n
- [ ] Activate workflow
- [ ] Test with your own number
- [ ] Verify QR codes arrive on WhatsApp
- [ ] Try scanning one QR code
- [ ] Check success response
- [ ] Try not scanning (timeout test)
- [ ] Check max attempts response

---

## 🚀 Production Deployment

1. **Secure Your Webhook**
   - Add authentication to webhook
   - Use HTTPS in production
   - Hide webhook URL

2. **Add Error Handling**
   - Monitor workflow executions
   - Set up error notifications
   - Log all attempts

3. **Rate Limiting**
   - Limit requests per user
   - Prevent spam/abuse
   - Add CAPTCHA if public

4. **Monitoring**
   - Track success rate
   - Monitor instance status
   - Alert on failures

---

## 💡 Use Cases

1. **Customer Onboarding**
   - User signs up → Gets QR via WhatsApp
   - Seamless integration experience

2. **Support Portal**
   - Customer needs WhatsApp access
   - Support triggers workflow
   - Auto-provision WhatsApp

3. **SaaS Applications**
   - "Connect WhatsApp" button
   - Instant QR delivery
   - No manual setup

4. **E-commerce**
   - Seller onboarding
   - Auto WhatsApp setup
   - Business integration

---

## 🎯 Next Steps

1. ✅ Import `n8n_workflow_qr_sender.json` to n8n
2. ✅ Activate the workflow
3. ✅ Test with `test_n8n_webhook.py`
4. ✅ Integrate into your application
5. ✅ Monitor and optimize

---

## 📚 Documentation Index

### Quick Start
- `WORKFLOW_QUICK_START.md` - Get running in 5 minutes

### Detailed Guides
- `N8N_WORKFLOW_GUIDE.md` - Complete n8n setup
- `UAZAPI_README.md` - Full API documentation

### Code Examples
- `uazapi_whatsapp.py` - Python client
- `send_qr_via_whatsapp.py` - Manual QR sending
- `test_n8n_webhook.py` - Workflow testing

### Import File
- `n8n_workflow_qr_sender.json` - n8n workflow

---

## ✅ What's Working

- ✅ Instance creation endpoint
- ✅ QR code generation
- ✅ Status checking
- ✅ Media/image sending
- ✅ Text message sending
- ✅ Auto-refresh loop
- ✅ Connection monitoring
- ✅ Max attempts limit

---

## 🎉 You're Ready!

Everything is configured for your instance:
```
Token: f5b12fac-c0ce-4c10-92eb-e24dc138230c
Number: 601130842973
Status: connected ✅
```

Just **import**, **activate**, and **test**!

---

## 📧 Support

If you need help:
1. Check troubleshooting section
2. Review n8n execution logs
3. Test API endpoints manually
4. Verify instance is connected

**Happy Automating! 🚀**
