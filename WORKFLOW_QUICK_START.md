# n8n Workflow - Quick Start Guide

## 🚀 Import in 3 Steps

### Step 1: Import Workflow
1. Open n8n
2. Click **"+" (New Workflow)**
3. Click **"..." menu** → **"Import from File"**
4. Select `n8n_workflow_qr_sender.json`

### Step 2: Activate
Click **"Active"** toggle (top-right)

### Step 3: Test
Send POST request to webhook:
```bash
curl -X POST http://your-n8n-url/webhook/create-whatsapp-instance \
  -H "Content-Type: application/json" \
  -d '{"phone": "5511999999999"}'
```

**Done! ✅** QR codes will be sent to that WhatsApp number every minute.

---

## 📊 Workflow Flow

```
User Request (phone: 5511999999999)
         ↓
    Create Instance
         ↓
    Get QR Code
         ↓
    ┌─→ Check Status ←─────┐
    │        ↓              │
    │   Connected?          │
    │    ↓       ↓          │
    │  YES      NO          │
    │   ↓        ↓          │
    │ STOP  Max Attempts?   │
    │         ↓      ↓      │
    │       YES     NO      │
    │        ↓      ↓       │
    │      STOP  Send QR    │
    │             ↓         │
    │        Wait 1min      │
    │             ↓         │
    │        Refresh QR     │
    │             ↓         │
    └─────────────┘
```

---

## 🎯 What It Does

1. **Creates** new WhatsApp instance
2. **Sends** QR code to your specified phone number
3. **Checks** every minute if device connected
4. **Refreshes** QR code each time
5. **Stops** when:
   - Device connects → Returns success ✅
   - 10 attempts reached → Returns failure ❌

---

## 📝 Request Format

**Endpoint:** `POST /webhook/create-whatsapp-instance`

**Body:**
```json
{
  "phone": "5511999999999"
}
```

**Phone Format:**
- ✅ `5511999999999` (Brazil)
- ✅ `14155551234` (USA)
- ❌ `+5511999999999` (no + sign)
- ❌ `11999999999` (needs country code)

---

## 📱 Response Examples

### Success (Connected)
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

## 🔧 Configuration (Already Set)

Your connected instance is already configured:

```
Server: https://chatsheros.uazapi.com
Token: f5b12fac-c0ce-4c10-92eb-e24dc138230c
Number: 601130842973
Status: connected ✅
```

This sends the QR codes. The workflow creates NEW instances for users to connect.

---

## 🎨 Customization

### Change wait time (default: 1 minute)
**Node:** "Wait 1 Minute"
```
amount: 60  → Change to 30 (30 seconds) or 120 (2 minutes)
```

### Change max attempts (default: 10)
**Node:** "Max Attempts Reached?"
```
>= 10  → Change to >= 5 or >= 20
```

### Change QR caption
**Node:** "Send QR via WhatsApp"
```javascript
caption: "Your custom message here"
```

---

## 🧪 Test Individual Steps

### Test 1: Create Instance
```bash
curl -X POST https://chatsheros.uazapi.com/instance/create \
  -H "admintoken: TPWVDMxqpcsBpKahh0B3ec1f4V8OVy1GvRCDunxHzilvmZxAv8" \
  -H "Content-Type: application/json" \
  -d '{"name": "test_instance"}'
```

### Test 2: Get QR
```bash
curl -X POST https://chatsheros.uazapi.com/instance/connect \
  -H "token: INSTANCE_TOKEN_FROM_STEP_1" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Test 3: Send QR
```bash
curl -X POST https://chatsheros.uazapi.com/send/media \
  -H "token: f5b12fac-c0ce-4c10-92eb-e24dc138230c" \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999",
    "image": "data:image/png;base64,...",
    "caption": "Test QR"
  }'
```

---

## ⚡ Production Enhancements

Add these nodes for production:

1. **Input Validation**
   - Add IF node after Webhook
   - Validate phone number format
   - Return error if invalid

2. **Database Logging**
   - Add MySQL/PostgreSQL node
   - Log all attempts with timestamps
   - Track success/failure rates

3. **Error Notifications**
   - Add Telegram/Email node
   - Get notified on failures
   - Monitor workflow health

4. **Rate Limiting**
   - Add Rate Limit node
   - Prevent spam/abuse
   - Set max requests per hour

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "WhatsApp disconnected" | Verify connected instance is active |
| QR not sending | Check phone format (no +, with country code) |
| Loop doesn't work | Ensure "Loop Back" connects to "Check Status" |
| "Missing token" | Check node expressions use correct syntax |
| Workflow stops early | Check IF conditions use correct operators |

---

## 📚 Files Included

- `n8n_workflow_qr_sender.json` - Import this into n8n
- `N8N_WORKFLOW_GUIDE.md` - Detailed setup guide
- `WORKFLOW_QUICK_START.md` - This file
- `uazapi_whatsapp.py` - Python client (alternative to n8n)
- `UAZAPI_README.md` - Complete API documentation

---

## 🎯 Use Cases

1. **Customer Onboarding**
   - User signs up on your website
   - Webhook triggered with their phone
   - QR sent automatically via WhatsApp

2. **Support Portal**
   - Customer requests WhatsApp integration
   - Support agent triggers webhook
   - Customer receives QR instantly

3. **Automation Platform**
   - Integrate with Zapier/Make
   - Trigger from form submissions
   - Auto-connect users to WhatsApp

4. **SaaS Application**
   - User clicks "Connect WhatsApp"
   - API call to n8n webhook
   - Seamless onboarding flow

---

## 💡 Pro Tips

1. **Test with your own number first** before sending to customers
2. **Monitor the first 10 executions** to ensure everything works
3. **Set up error alerts** to catch issues early
4. **Use environment variables** for tokens (don't hardcode)
5. **Add retry logic** for API failures
6. **Log all requests** for debugging and analytics

---

## 🔐 Security Best Practices

1. **Use n8n authentication** on webhook endpoint
2. **Validate phone numbers** before processing
3. **Rate limit** webhook calls
4. **Don't expose** admin token in logs
5. **Store tokens** in n8n credentials
6. **Monitor** for unusual activity

---

## 📞 Support

**Already configured for your instance:**
- Server: https://chatsheros.uazapi.com
- Connected Number: 601130842973
- Instance Token: Ready to use ✅

Just import and activate! The workflow will use your connected WhatsApp to send QR codes to new users.
