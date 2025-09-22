import aiohttp
import asyncio
import json
from typing import Dict, List, Optional, Any

class StraicoClient:
    def __init__(self, api_key: str, base_url: str = "https://api.straico.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make an HTTP request to the Straico API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async with statement.")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            async with self.session.request(method, url, json=data) as response:
                # Handle different response types
                content_type = response.headers.get('content-type', '')

                if 'application/json' in content_type:
                    response_data = await response.json()
                else:
                    # Handle non-JSON responses
                    text_response = await response.text()
                    try:
                        response_data = json.loads(text_response)
                    except json.JSONDecodeError:
                        response_data = {"response": text_response}

                if response.status >= 400:
                    raise Exception(f"API Error {response.status}: {response_data}")

                return response_data

        except aiohttp.ClientError as e:
            raise Exception(f"Network error: {str(e)}")

    async def get_models(self) -> List[Dict]:
        """Get list of available models"""
        return await self._make_request("GET", "/v1/models")

    async def get_user_info(self) -> Dict:
        """Get user account information"""
        return await self._make_request("GET", "/v1/user")

    async def chat_completion(self, model: str, messages: List[Dict], **kwargs) -> Dict:
        """Send a chat completion request with retry logic"""
        # Use quality mode to avoid GPT-5 reasoning token issues
        data = {
            "smart_llm_selector": {
                "quantity": 1,
                "pricing_method": "quality"
            },
            "message": messages[-1]["content"] if messages else "Hello",
            **kwargs
        }

        # Retry logic for API 500 errors
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                return await self._make_request("POST", "/v1/prompt/completion", data)
            except Exception as e:
                if "500" in str(e) and attempt < max_retries:
                    print(f"DEBUG - API 500 error, retrying attempt {attempt + 1}/{max_retries}")
                    await asyncio.sleep(1)  # Wait 1 second before retry
                    continue
                else:
                    raise e

    async def generate_image(self, model: str, description: str, size: str, variations: int, **kwargs) -> Dict:
        """Generate an image"""
        data = {
            "model": model,
            "description": description,
            "size": size,
            "variations": variations,
            **kwargs
        }
        return await self._make_request("POST", "/v1/image/generation", data)

    async def generate_video(self, prompt: str, model: str = "runway-gen3", **kwargs) -> Dict:
        """Generate a video"""
        data = {
            "prompt": prompt,
            "model": model,
            **kwargs
        }
        return await self._make_request("POST", "/videos/generations", data)

    async def get_generation_status(self, generation_id: str) -> Dict:
        """Check the status of a generation request"""
        return await self._make_request("GET", f"/generations/{generation_id}")