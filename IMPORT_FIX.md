# n8n Import Fix Guide

## Issue: "Could not find property option"

This error occurs when n8n workflow JSON contains node configurations incompatible with your n8n version.

## ✅ Solution: Use the Fixed Workflow

**Import this file instead:**
```
n8n_workflow_qr_sender_v2.json
```

This version uses:
- HTTP Request v3 (more compatible)
- Set v2 (older, stable format)
- IF v1 (simpler conditions)

---

## 📥 How to Import v2

1. Open n8n
2. Click **"+"** → **"Import from File"**
3. Select **`n8n_workflow_qr_sender_v2.json`**
4. Click **Import**

If import works, skip to "After Import" section below.

---

## 🛠️ Alternative: Manual Creation

If import still fails, create the workflow manually:

### Step 1: Create Webhook Node

1. Add **Webhook** node
2. Configure:
   - **HTTP Method:** POST
   - **Path:** `create-whatsapp-instance`
   - **Response Mode:** "Using 'Respond to Webhook' Node"

### Step 2: Create Instance Node

1. Add **HTTP Request** node
2. Configure:
   - **Method:** POST
   - **URL:** `https://chatsheros.uazapi.com/instance/create`
   - **Headers:**
     - `admintoken`: `TPWVDMxqpcsBpKahh0B3ec1f4V8OVy1GvRCDunxHzilvmZxAv8`
     - `Content-Type`: `application/json`
   - **Body:** JSON
   ```json
   {
     "name": "={{ 'instance_' + $now.toUnixInteger() }}"
   }
   ```

### Step 3: Connect & Get QR Node

1. Add **HTTP Request** node
2. Configure:
   - **Method:** POST
   - **URL:** `https://chatsheros.uazapi.com/instance/connect`
   - **Headers:**
     - `token`: `={{ $json.token }}`
     - `Content-Type`: `application/json`
   - **Body:** JSON
   ```json
   {}
   ```

### Step 4: Set Variables Node

1. Add **Set** node
2. Add these values:

**String values:**
```
new_instance_token: {{ $('HTTP Request').item.json.token }}
new_instance_id: {{ $('HTTP Request').item.json.instance.id }}
recipient_phone: {{ $('Webhook').item.json.body.phone }}
connected_instance_token: f5b12fac-c0ce-4c10-92eb-e24dc138230c
```

**Number values:**
```
attempt_count: 1
```

### Step 5: Check Status Node

1. Add **HTTP Request** node
2. Configure:
   - **Method:** GET
   - **URL:** `https://chatsheros.uazapi.com/instance/status`
   - **Headers:**
     - `token`: `={{ $('Set').item.json.new_instance_token }}`

### Step 6: Is Connected? Node

1. Add **IF** node
2. Configure:
   - **Conditions:** String
   - **Value 1:** `={{ $json.instance.status }}`
   - **Operation:** Equals
   - **Value 2:** `connected`

### Step 7: Respond Connected Node

1. Add **Respond to Webhook** node (connect to TRUE output)
2. Configure:
   - **Response:** JSON
   ```json
   {
     "success": true,
     "message": "Your device has been connected!",
     "instance_id": "={{ $('Set').item.json.new_instance_id }}",
     "status": "connected"
   }
   ```

### Step 8: Max Attempts? Node

1. Add **IF** node (connect to FALSE output from step 6)
2. Configure:
   - **Conditions:** Number
   - **Value 1:** `={{ $('Set').item.json.attempt_count }}`
   - **Operation:** Larger or Equal
   - **Value 2:** `10`

### Step 9: Respond Max Attempts Node

1. Add **Respond to Webhook** node (connect to TRUE output)
2. Configure:
   - **Response:** JSON
   ```json
   {
     "success": false,
     "message": "Maximum attempts reached",
     "attempts": "={{ $('Set').item.json.attempt_count }}"
   }
   ```

### Step 10: Send QR Node

1. Add **HTTP Request** node (connect to FALSE output)
2. Configure:
   - **Method:** POST
   - **URL:** `https://chatsheros.uazapi.com/send/media`
   - **Headers:**
     - `token`: `={{ $('Set').item.json.connected_instance_token }}`
   - **Body:** JSON
   ```json
   {
     "number": "={{ $('Set').item.json.recipient_phone }}",
     "image": "={{ $('HTTP Request 2').item.json.instance.qrcode }}",
     "caption": "🔐 Scan this QR code - Attempt {{ $('Set').item.json.attempt_count }}/10"
   }
   ```

### Step 11: Wait Node

1. Add **Wait** node
2. Configure:
   - **Time:** 60 seconds

### Step 12: Increment Counter Node

1. Add **Set** node
2. Add these values:

**String values:**
```
new_instance_token: {{ $('Set').item.json.new_instance_token }}
new_instance_id: {{ $('Set').item.json.new_instance_id }}
recipient_phone: {{ $('Set').item.json.recipient_phone }}
connected_instance_token: {{ $('Set').item.json.connected_instance_token }}
```

**Number values:**
```
attempt_count: {{ $('Set').item.json.attempt_count + 1 }}
```

### Step 13: Refresh QR Node

1. Add **HTTP Request** node
2. Configure:
   - **Method:** POST
   - **URL:** `https://chatsheros.uazapi.com/instance/connect`
   - **Headers:**
     - `token`: `={{ $json.new_instance_token }}`
   - **Body:** JSON `{}`

### Step 14: Loop Back Node

1. Add **Merge** node
2. Configure:
   - **Mode:** Choose Branch
   - **Output:** Input 1
3. **Connect output** to "Check Status" node (Step 5)

---

## 🔗 Node Connections

```
Webhook → Create Instance → Connect & Get QR → Set Variables → Check Status
                                                                    ↓
                                                              Is Connected?
                                                              ↙         ↘
                                                         TRUE          FALSE
                                                          ↓              ↓
                                                  Respond Connected  Max Attempts?
                                                                      ↙         ↘
                                                                   TRUE       FALSE
                                                                    ↓           ↓
                                                           Respond Max    Send QR
                                                                           ↓
                                                                      Wait 1min
                                                                           ↓
                                                                   Increment Counter
                                                                           ↓
                                                                      Refresh QR
                                                                           ↓
                                                                      Loop Back
                                                                           ↓
                                                        (back to Check Status)
```

---

## ✅ After Import (or Manual Creation)

### 1. Update Your Instance Token

In the **"Set Variables"** node, change:
```
connected_instance_token: YOUR_CONNECTED_INSTANCE_TOKEN
```

Replace with your actual connected instance token.

### 2. Activate Workflow

Click the **"Active"** toggle (top-right)

### 3. Test

Get your webhook URL and test:
```bash
curl -X POST http://your-n8n-url/webhook/create-whatsapp-instance \
  -H "Content-Type: application/json" \
  -d '{"phone": "5511999999999"}'
```

---

## 🐛 Troubleshooting

### Import Still Fails

**Try this:**
1. Update n8n to latest version
2. Clear browser cache
3. Try importing in incognito mode
4. Use manual creation method above

### Node Not Found Error

**Your n8n version might be missing nodes:**
- Make sure you have the latest n8n version
- Check if HTTP Request node is available
- Try using the n8n desktop app instead of cloud

### Expression Errors

**Fix node references:**
- Make sure node names match exactly
- Use the dropdown to select nodes instead of typing
- Check that all `$('Node Name')` references are correct

---

## 📚 What Changed from v1 to v2

| Feature | v1 | v2 |
|---------|----|----|
| HTTP Request | v4.1 | v3 ✅ |
| Set Node | v3.3 | v2 ✅ |
| IF Node | v2 (complex) | v1 (simple) ✅ |
| Parameters | New format | Old format ✅ |

v2 is more compatible with older n8n versions.

---

## 🎯 Quick Test Checklist

After import/creation:

- [ ] Webhook node shows URL
- [ ] All nodes are connected (no red warnings)
- [ ] "Set Variables" has your instance token
- [ ] Activate workflow (toggle on)
- [ ] Test with curl or Postman
- [ ] Check execution log for errors

---

## 📞 Still Having Issues?

1. **Check n8n version:**
   ```bash
   n8n --version
   ```

2. **Try n8n community:**
   - https://community.n8n.io

3. **Use Python alternative:**
   - See `uazapi_whatsapp.py` for direct API usage

---

## ✨ Success!

Once imported, you should see:
- ✅ 14 nodes connected
- ✅ No error warnings
- ✅ Webhook URL available
- ✅ Ready to activate

**Happy automating! 🚀**
