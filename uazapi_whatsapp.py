#!/usr/bin/env python3
"""
UAZAPI WhatsApp API Client
Simple client to create instance, start it, and retrieve QR code
"""

import requests
import json
import time


class UazapiWhatsApp:
    """
    Client for UAZAPI WhatsApp API

    Base URL: https://chatsheros.uazapi.com

    Required:
    - Admin Token for creating instances
    - Instance Token (returned from create) for connecting and getting QR
    """

    def __init__(self, base_url: str, admin_token: str):
        """
        Initialize UAZAPI client

        Args:
            base_url: Base URL of the API (e.g., https://chatsheros.uazapi.com)
            admin_token: Admin token for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.admin_token = admin_token

    def create_instance(self, name: str):
        """
        Create a new WhatsApp instance

        Endpoint: POST /instance/create
        Headers: admintoken
        Payload: {"name": "instance_name"}

        Args:
            name: Name for the new instance

        Returns:
            dict: Response containing instance details including:
                - instance.id: Instance ID
                - token: Instance token (needed for connect/status)
                - instance.status: Current status
        """
        url = f"{self.base_url}/instance/create"
        headers = {
            'Content-Type': 'application/json',
            'admintoken': self.admin_token
        }
        payload = {'name': name}

        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    def connect_instance(self, instance_token: str):
        """
        Connect instance and retrieve QR code

        Endpoint: POST /instance/connect
        Headers: token (instance token)
        Payload: {} (empty)

        Args:
            instance_token: Token from create_instance response

        Returns:
            dict: Response containing:
                - instance.qrcode: Base64 encoded QR code image (data:image/png;base64,...)
                - instance.status: Connection status
                - connected: Boolean connection state
        """
        url = f"{self.base_url}/instance/connect"
        headers = {
            'Content-Type': 'application/json',
            'token': instance_token
        }

        response = requests.post(url, headers=headers, json={})
        return response.json()

    def get_instance_status(self, instance_token: str):
        """
        Get instance status and QR code

        Endpoint: GET /instance/status
        Headers: token (instance token)

        Args:
            instance_token: Token from create_instance response

        Returns:
            dict: Response containing:
                - instance.qrcode: Base64 encoded QR code image
                - instance.status: Current status (connecting, connected, disconnected)
                - instance information
        """
        url = f"{self.base_url}/instance/status"
        headers = {
            'Content-Type': 'application/json',
            'token': instance_token
        }

        response = requests.get(url, headers=headers)
        return response.json()

    def save_qr_code(self, qrcode_data: str, filename: str = "whatsapp_qr.png"):
        """
        Save base64 QR code to file

        Args:
            qrcode_data: Base64 data URL (data:image/png;base64,...)
            filename: Output filename
        """
        import base64

        # Remove the data:image/png;base64, prefix
        if qrcode_data.startswith('data:image'):
            qrcode_data = qrcode_data.split(',')[1]

        # Decode and save
        img_data = base64.b64decode(qrcode_data)
        with open(filename, 'wb') as f:
            f.write(img_data)

        print(f"QR code saved to {filename}")


def main():
    """
    Example usage: Create instance, start it, and get QR code
    """

    # Configuration
    BASE_URL = "https://chatsheros.uazapi.com"
    ADMIN_TOKEN = "TPWVDMxqpcsBpKahh0B3ec1f4V8OVy1GvRCDunxHzilvmZxAv8"

    # Initialize client
    client = UazapiWhatsApp(BASE_URL, ADMIN_TOKEN)

    # Step 1: Create instance
    print("=" * 60)
    print("Step 1: Creating WhatsApp instance...")
    print("=" * 60)

    instance_name = f"whatsapp_{int(time.time())}"
    create_response = client.create_instance(instance_name)

    print(json.dumps(create_response, indent=2))

    # Extract instance details
    instance_id = create_response['instance']['id']
    instance_token = create_response['token']

    print(f"\n✓ Instance Created!")
    print(f"  - Instance ID: {instance_id}")
    print(f"  - Instance Token: {instance_token}")
    print(f"  - Status: {create_response['instance']['status']}")

    # Step 2: Connect instance and get QR code
    print("\n" + "=" * 60)
    print("Step 2: Connecting instance and getting QR code...")
    print("=" * 60)

    connect_response = client.connect_instance(instance_token)

    print(f"\n✓ Connection initiated!")
    print(f"  - Status: {connect_response['instance']['status']}")
    print(f"  - Connected: {connect_response['connected']}")

    qrcode = connect_response['instance']['qrcode']

    if qrcode:
        print(f"  - QR Code: Received ({len(qrcode)} characters)")

        # Save QR code to file
        client.save_qr_code(qrcode, "whatsapp_qr.png")

        print("\n" + "=" * 60)
        print("SUCCESS! Next steps:")
        print("=" * 60)
        print("1. Open WhatsApp on your mobile device")
        print("2. Go to Settings > Linked Devices")
        print("3. Tap 'Link a Device'")
        print("4. Scan the QR code from whatsapp_qr.png")
        print("\nOr view the QR in your terminal/browser using the base64 data")

        # Step 3: Check status
        print("\n" + "=" * 60)
        print("Step 3: Checking instance status...")
        print("=" * 60)

        status_response = client.get_instance_status(instance_token)
        print(f"  - Status: {status_response['instance']['status']}")
        print(f"  - Instance ID: {status_response['instance']['id']}")

        return {
            'instance_id': instance_id,
            'instance_token': instance_token,
            'qrcode': qrcode,
            'status': status_response['instance']['status']
        }
    else:
        print("  ⚠ No QR code received. Instance might already be connected.")
        return None


if __name__ == "__main__":
    result = main()

    if result:
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Instance ID: {result['instance_id']}")
        print(f"Instance Token: {result['instance_token']}")
        print(f"Status: {result['status']}")
        print(f"QR Code saved to: whatsapp_qr.png")
