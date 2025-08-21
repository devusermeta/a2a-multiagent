#!/usr/bin/env python3

import asyncio
import httpx
import json


async def test_endpoints():
    """Test different endpoints to find the correct one"""
    endpoints = ["/", "/agent_card", "/card", "/health", "/info"]
    
    print("🔍 Testing TimeAgent endpoints...")
    
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            try:
                response = await client.get(f"http://localhost:10003{endpoint}")
                print(f"   {endpoint}: {response.status_code} - {response.text[:100]}...")
            except Exception as e:
                print(f"   {endpoint}: Error - {e}")


if __name__ == "__main__":
    asyncio.run(test_endpoints())
