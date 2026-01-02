#!/usr/bin/env python3
"""Quick test to verify 503 fix works"""
import asyncio
import httpx

async def test():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Login
        login_r = await client.post(
            'http://35.215.64.103/api/auth/login',
            json={'email': 'test_user@symphainy.com', 'password': 'test_password'}
        )
        print(f'Login: {login_r.status_code}')
        
        if login_r.status_code != 200:
            print(f'Login failed: {login_r.text}')
            return
        
        token = login_r.json().get('access_token')
        if not token:
            print('No token in response')
            return
        
        # Test file listing (was returning 503)
        list_r = await client.get(
            'http://35.215.64.103/api/v1/content-pillar/list-uploaded-files',
            headers={'Authorization': f'Bearer {token}'},
            timeout=10.0
        )
        print(f'List files: {list_r.status_code}')
        if list_r.status_code != 200:
            print(f'Error: {list_r.text[:200]}')

if __name__ == '__main__':
    asyncio.run(test())





