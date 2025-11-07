#!/usr/bin/env python3
"""
Example: Send WhatsApp QR code to a phone number via UAZAPI

Note: This requires an already connected WhatsApp instance.
You can't use the new instance to send its own QR - you need
another already-connected instance to send the QR code to someone.
"""

import requests
import json
import time


class UazapiSender:
    def __init__(self, base_url: str, admin_token: str):
        self.base_url = base_url.rstrip('/')
        self.admin_token = admin_token

    def send_text(self, instance_token: str, phone_number: str, message: str):
        """
        Send text message via WhatsApp

        Endpoint: POST /send/text
        Headers: token (instance token)

        Args:
            instance_token: Token of a CONNECTED instance
            phone_number: Phone number with country code (e.g., "5511999999999")
            message: Text message to send

        Returns:
            API response
        """
        url = f"{self.base_url}/send/text"
        headers = {
            'Content-Type': 'application/json',
            'token': instance_token
        }
        payload = {
            'number': phone_number,
            'message': message
        }

        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    def send_media(self, instance_token: str, phone_number: str, media_base64: str, caption: str = ""):
        """
        Send image/media via WhatsApp (can be used to send QR code)

        Endpoint: POST /send/media
        Headers: token (instance token)

        Args:
            instance_token: Token of a CONNECTED instance
            phone_number: Phone number with country code
            media_base64: Base64 encoded image (data:image/png;base64,...)
            caption: Optional caption for the image

        Returns:
            API response
        """
        url = f"{self.base_url}/send/media"
        headers = {
            'Content-Type': 'application/json',
            'token': instance_token
        }
        payload = {
            'number': phone_number,
            'image': media_base64,  # or 'media': media_base64
            'caption': caption
        }

        response = requests.post(url, headers=headers, json=payload)
        return response.json()


def example_send_qr_code():
    """
    Example: Send QR code to a phone number

    IMPORTANT: You need TWO instances:
    1. Instance A (connected) - to SEND the QR code
    2. Instance B (new) - whose QR code you want to send
    """

    BASE_URL = "https://chatsheros.uazapi.com"
    ADMIN_TOKEN = "TPWVDMxqpcsBpKahh0B3ec1f4V8OVy1GvRCDunxHzilvmZxAv8"

    sender = UazapiSender(BASE_URL, ADMIN_TOKEN)

    # Step 1: Create NEW instance (Instance B) to get its QR code
    print("="*60)
    print("Creating new instance to get QR code...")
    print("="*60)

    response = requests.post(
        f"{BASE_URL}/instance/create",
        headers={'Content-Type': 'application/json', 'admintoken': ADMIN_TOKEN},
        json={'name': f'qr_instance_{int(time.time())}'}
    )
    new_instance_data = response.json()
    new_instance_token = new_instance_data['token']

    # Connect to get QR
    response = requests.post(
        f"{BASE_URL}/instance/connect",
        headers={'Content-Type': 'application/json', 'token': new_instance_token},
        json={}
    )
    qr_code_base64 = response.json()['instance']['qrcode']

    print(f"✓ QR code obtained for new instance")

    # Step 2: Send QR code using ANOTHER connected instance
    print("\n" + "="*60)
    print("Sending QR code via WhatsApp...")
    print("="*60)

    # You would use a CONNECTED instance token here
    CONNECTED_INSTANCE_TOKEN = "your_connected_instance_token"
    RECIPIENT_PHONE = "5511999999999"  # Phone number with country code

    try:
        result = sender.send_media(
            instance_token=CONNECTED_INSTANCE_TOKEN,
            phone_number=RECIPIENT_PHONE,
            media_base64=qr_code_base64,
            caption="Scan this QR code to connect WhatsApp"
        )
        print(f"✓ QR code sent successfully!")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"✗ Failed to send: {e}")
        print("\nNote: You need a CONNECTED instance to send messages.")
        print("The new instance can't send its own QR code.")


def example_payload_formats():
    """Show different payload formats for sending media"""

    print("="*60)
    print("Possible payload formats for /send/media:")
    print("="*60)

    formats = [
        {
            "description": "Format 1: Using 'image' key",
            "payload": {
                "number": "5511999999999",
                "image": "data:image/png;base64,iVBORw0KGgo...",
                "caption": "Scan this QR code"
            }
        },
        {
            "description": "Format 2: Using 'media' key",
            "payload": {
                "number": "5511999999999",
                "media": "data:image/png;base64,iVBORw0KGgo...",
                "caption": "Scan this QR code"
            }
        },
        {
            "description": "Format 3: Alternative phone key",
            "payload": {
                "phone": "5511999999999",
                "image": "data:image/png;base64,iVBORw0KGgo...",
                "message": "Scan this QR code"
            }
        }
    ]

    for fmt in formats:
        print(f"\n{fmt['description']}")
        print(json.dumps(fmt['payload'], indent=2))


if __name__ == "__main__":
    print("\n" + "="*60)
    print("UAZAPI - Send QR Code via WhatsApp")
    print("="*60)

    example_payload_formats()

    print("\n\n" + "="*60)
    print("IMPORTANT NOTES:")
    print("="*60)
    print("1. You CANNOT send messages from a disconnected instance")
    print("2. To send a QR code via WhatsApp, you need:")
    print("   - Instance A: Already connected (to SEND)")
    print("   - Instance B: New instance (whose QR you want to send)")
    print("3. Use Instance A's token to send Instance B's QR code")
    print("4. Phone number format: Country code + number (e.g., '5511999999999')")
    print("="*60)
