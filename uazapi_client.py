#!/usr/bin/env python3
"""
UAZAPI WhatsApp API Client
Helps interact with UAZAPI for instance management and QR code retrieval
"""

import requests
import json
import time
from typing import Optional, Dict, Any


class UazapiClient:
    def __init__(self, base_url: str, admin_token: str):
        """
        Initialize UAZAPI client

        Args:
            base_url: Base URL of the API (e.g., https://chatsheros.uazapi.com)
            admin_token: Admin token for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.admin_token = admin_token
        self.headers = {
            'Content-Type': 'application/json',
        }
        # Try multiple authentication header patterns
        self.auth_headers = [
            {'admintoken': admin_token},
            {'admin-token': admin_token},
            {'Authorization': f'Bearer {admin_token}'},
            {'token': admin_token},
            {'api-key': admin_token},
            {'x-api-key': admin_token}
        ]

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, auth_header: Optional[Dict] = None) -> Dict[Any, Any]:
        """
        Make HTTP request to API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request payload (for POST requests)
            auth_header: Specific auth header to use

        Returns:
            Response JSON
        """
        url = f"{self.base_url}{endpoint}"

        # Merge headers
        headers = self.headers.copy()
        if auth_header:
            headers.update(auth_header)
        else:
            headers.update(self.auth_headers[0])  # Default to first auth pattern

        try:
            print(f"\n🔹 {method} {url}")

            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                print(f"📤 Payload: {json.dumps(data, indent=2)}")
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            print(f"📥 Status Code: {response.status_code}")

            # Try to parse JSON response
            try:
                result = response.json()
                print(f"📦 Response: {json.dumps(result, indent=2)}")
                return result
            except json.JSONDecodeError:
                print(f"📦 Response (text): {response.text}")
                return {"status_code": response.status_code, "text": response.text}

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            return {"error": str(e)}

    # Common endpoint patterns - these may need adjustment based on actual API

    def create_instance(self, instance_name: Optional[str] = None) -> Dict:
        """
        Create a new WhatsApp instance

        Args:
            instance_name: Optional name for the instance

        Returns:
            Response with instance details
        """
        print("\n" + "="*50)
        print("Creating Instance...")
        print("="*50)

        instance_name = instance_name or f"instance_{int(time.time())}"

        # Try different payload formats
        payloads = [
            {'instanceName': instance_name},
            {'name': instance_name},
            {'Name': instance_name},
            {'instance': instance_name},
            {'instanceId': instance_name},
        ]

        endpoint = '/instance/create'

        for payload in payloads:
            print(f"\n📝 Trying payload format: {payload}")
            result = self._make_request('POST', endpoint, payload)
            if result.get('status_code') != 400 and 'Missing Name' not in result.get('error', ''):
                return result

        return {"error": "Could not find correct payload format"}

    def get_qr_code(self, instance_id: Optional[str] = None) -> Dict:
        """
        Get QR code for WhatsApp authentication

        Args:
            instance_id: Instance ID (if required)

        Returns:
            Response with QR code data
        """
        print("\n" + "="*50)
        print("Getting QR Code...")
        print("="*50)

        # Try common patterns for QR code retrieval
        endpoints = [
            '/instance/qr',
            '/api/instance/qr',
            '/v1/instance/qr',
            '/v2/instance/qr',
            '/qrcode',
            '/instance/qrcode',
            '/instance/connect'
        ]

        if instance_id:
            endpoints.extend([
                f'/instance/{instance_id}/qr',
                f'/instance/{instance_id}/qrcode',
                f'/api/instance/{instance_id}/qr',
                f'/v2/instance/{instance_id}/qr'
            ])

        for endpoint in endpoints:
            result = self._make_request('GET', endpoint)
            if result.get('status_code') != 404 and 'error' not in result:
                return result

        return {"error": "Could not find working QR code endpoint"}

    def get_instance_status(self, instance_id: Optional[str] = None) -> Dict:
        """
        Get instance connection status

        Args:
            instance_id: Instance ID (if required)

        Returns:
            Response with instance status
        """
        print("\n" + "="*50)
        print("Getting Instance Status...")
        print("="*50)

        endpoints = [
            '/instance/status',
            '/api/instance/status',
            '/v1/instance/status',
            '/v2/instance/status',
            '/instance/connectionState'
        ]

        if instance_id:
            endpoints.extend([
                f'/instance/{instance_id}/status',
                f'/api/instance/{instance_id}/status',
                f'/v2/instance/{instance_id}/status'
            ])

        for endpoint in endpoints:
            result = self._make_request('GET', endpoint)
            if result.get('status_code') != 404 and 'error' not in result:
                return result

        return {"error": "Could not find working status endpoint"}

    def list_instances(self) -> Dict:
        """
        List all instances

        Returns:
            Response with list of instances
        """
        print("\n" + "="*50)
        print("Listing Instances...")
        print("="*50)

        endpoints = [
            '/instance/list',
            '/instances',
            '/api/instances',
            '/v1/instances',
            '/v2/instances',
            '/instance/fetchInstances'
        ]

        for endpoint in endpoints:
            result = self._make_request('GET', endpoint)
            if result.get('status_code') != 404 and 'error' not in result:
                return result

        return {"error": "Could not find working list instances endpoint"}

    def start_instance(self, instance_id: str) -> Dict:
        """
        Start/connect an instance

        Args:
            instance_id: Instance ID to start

        Returns:
            Response with start result
        """
        print("\n" + "="*50)
        print(f"Starting Instance: {instance_id}")
        print("="*50)

        endpoints = [
            f'/instance/{instance_id}/start',
            f'/instance/{instance_id}/connect',
            f'/api/instance/{instance_id}/start',
            f'/v2/instance/{instance_id}/connect',
            '/instance/connect',
            '/instance/start'
        ]

        for endpoint in endpoints:
            payload = {'instanceId': instance_id} if not instance_id in endpoint else {}
            result = self._make_request('POST', endpoint, payload)
            if result.get('status_code') != 404 and 'error' not in result:
                return result

        return {"error": "Could not find working start instance endpoint"}


def main():
    """
    Main function to test the API
    """
    # Configuration
    BASE_URL = "https://chatsheros.uazapi.com"
    ADMIN_TOKEN = "TPWVDMxqpcsBpKahh0B3ec1f4V8OVy1GvRCDunxHzilvmZxAv8"

    # Initialize client
    client = UazapiClient(BASE_URL, ADMIN_TOKEN)

    print("="*50)
    print("UAZAPI WhatsApp API Client")
    print("="*50)

    # Test 1: List instances
    print("\n\n🔍 Step 1: Listing existing instances...")
    instances = client.list_instances()

    # Test 2: Create instance
    print("\n\n🔍 Step 2: Creating new instance...")
    instance_name = f"test_instance_{int(time.time())}"
    create_result = client.create_instance(instance_name)

    # Extract instance ID if available
    instance_id = None
    if isinstance(create_result, dict):
        instance_id = (create_result.get('instanceId') or
                      create_result.get('instance') or
                      create_result.get('id') or
                      create_result.get('data', {}).get('instanceId'))

    # Test 3: Get QR Code
    print("\n\n🔍 Step 3: Getting QR Code...")
    qr_result = client.get_qr_code(instance_id)

    # Test 4: Check instance status
    print("\n\n🔍 Step 4: Checking instance status...")
    status_result = client.get_instance_status(instance_id)

    print("\n\n" + "="*50)
    print("Summary")
    print("="*50)
    print(f"✅ Instance Creation: {'Success' if create_result.get('instanceId') else 'Check response'}")
    print(f"✅ QR Code Retrieval: {'Success' if qr_result.get('qrcode') or qr_result.get('base64') else 'Check response'}")
    print(f"✅ Instance Status: {'Success' if status_result.get('status') or status_result.get('state') else 'Check response'}")

    if instance_id:
        print(f"\n📱 Instance ID: {instance_id}")

    if qr_result.get('qrcode') or qr_result.get('base64'):
        print("\n📱 QR Code received! You can now scan it with WhatsApp mobile app.")


if __name__ == "__main__":
    main()
