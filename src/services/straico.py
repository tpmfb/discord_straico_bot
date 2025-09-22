import aiohttp
import asyncio
import json
import time
import hashlib
from typing import Dict, List, Optional, Any
import logging
from core.errors import APIError

class StraicoService:
    def __init__(self, api_key: str, base_url: str = "https://api.straico.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = None
        self.logger = logging.getLogger(__name__)

        # Performance optimizations
        self._response_cache = {}
        self._cache_ttl = 300  # 5 minutes cache
        self._connection_pool_size = 10
        self._timeout = aiohttp.ClientTimeout(total=30, connect=10)

    async def __aenter__(self):
        # Optimized session with connection pooling
        connector = aiohttp.TCPConnector(
            limit=self._connection_pool_size,
            limit_per_host=5,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self._timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Connection": "keep-alive"
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _get_cache_key(self, method: str, endpoint: str, data: Optional[Dict] = None) -> str:
        """Generate cache key for request"""
        key_data = f"{method}:{endpoint}:{json.dumps(data, sort_keys=True) if data else ''}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        return time.time() - cache_entry['timestamp'] < self._cache_ttl

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, use_cache: bool = True) -> Dict:
        if not self.session:
            raise RuntimeError("Service not initialized. Use async with statement.")

        # Check cache for GET requests and specific endpoints
        cache_key = None
        if use_cache and method == "GET" or endpoint in ["/v1/models", "/v1/user"]:
            cache_key = self._get_cache_key(method, endpoint, data)
            if cache_key in self._response_cache and self._is_cache_valid(self._response_cache[cache_key]):
                self.logger.debug(f"Cache hit for {endpoint}")
                return self._response_cache[cache_key]['data']

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        self.logger.debug(f"Making {method} request to {url}")

        try:
            # Use optimized request parameters
            async with self.session.request(
                method,
                url,
                json=data,
                compress=True  # Enable compression
            ) as response:
                content_type = response.headers.get('content-type', '')

                if 'application/json' in content_type:
                    response_data = await response.json()
                else:
                    text_response = await response.text()
                    try:
                        response_data = json.loads(text_response)
                    except json.JSONDecodeError:
                        response_data = {"response": text_response}

                if response.status >= 400:
                    self.logger.error(f"API Error {response.status}: {response_data}")
                    raise APIError(f"API Error {response.status}: {response_data}", response.status)

                # Cache successful responses
                if use_cache and cache_key and response.status == 200:
                    self._response_cache[cache_key] = {
                        'data': response_data,
                        'timestamp': time.time()
                    }
                    # Clean old cache entries periodically
                    if len(self._response_cache) > 100:
                        self._clean_cache()

                return response_data

        except asyncio.TimeoutError:
            self.logger.error(f"Request timeout for {endpoint}")
            raise APIError(f"Request timeout for {endpoint}")
        except aiohttp.ClientError as e:
            self.logger.error(f"Network error: {str(e)}")
            raise APIError(f"Network error: {str(e)}")

    def _clean_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._response_cache.items()
            if current_time - entry['timestamp'] > self._cache_ttl
        ]
        for key in expired_keys:
            del self._response_cache[key]

    async def _make_request_with_timeout(self, method: str, endpoint: str, data: Optional[Dict] = None, timeout_seconds: int = 30) -> Dict:
        """Make request with custom timeout for specific operations"""
        if not self.session:
            raise RuntimeError("Service not initialized. Use async with statement.")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        self.logger.debug(f"Making {method} request to {url} with {timeout_seconds}s timeout")

        # Create custom timeout for this request
        custom_timeout = aiohttp.ClientTimeout(total=timeout_seconds, connect=10)

        try:
            async with self.session.request(
                method,
                url,
                json=data,
                timeout=custom_timeout,
                compress=True
            ) as response:
                content_type = response.headers.get('content-type', '')

                if 'application/json' in content_type:
                    response_data = await response.json()
                else:
                    text_response = await response.text()
                    try:
                        response_data = json.loads(text_response)
                    except json.JSONDecodeError:
                        response_data = {"response": text_response}

                if response.status >= 400:
                    self.logger.error(f"API Error {response.status}: {response_data}")
                    raise APIError(f"API Error {response.status}: {response_data}", response.status)

                return response_data

        except asyncio.TimeoutError:
            self.logger.error(f"Request timeout ({timeout_seconds}s) for {endpoint}")
            raise APIError(f"Request timeout ({timeout_seconds}s) for {endpoint}")
        except aiohttp.ClientError as e:
            self.logger.error(f"Network error: {str(e)}")
            raise APIError(f"Network error: {str(e)}")

    async def get_models(self) -> List[Dict]:
        return await self._make_request("GET", "/v1/models")

    async def get_user_info(self) -> Dict:
        return await self._make_request("GET", "/v1/user")

    async def chat_completion(self, model: str, messages: List[Dict], **kwargs) -> Dict:
        # Optimize the request payload
        data = {
            "smart_llm_selector": {
                "quantity": 1,
                "pricing_method": "quality"
            },
            "message": messages[-1]["content"] if messages else "Hello",
            **kwargs
        }

        # Reduce retry delay and optimize retry logic
        max_retries = 2
        base_delay = 0.5  # Reduced from 1 second

        for attempt in range(max_retries + 1):
            try:
                # Disable caching for chat completions (real-time responses)
                return await self._make_request("POST", "/v1/prompt/completion", data, use_cache=False)
            except APIError as e:
                if e.status_code == 500 and attempt < max_retries:
                    # Exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + (asyncio.get_event_loop().time() % 0.1)
                    self.logger.warning(f"API 500 error, retrying attempt {attempt + 1}/{max_retries} after {delay:.2f}s")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise e

    async def generate_image(self, model: str, description: str, size: str, variations: int, **kwargs) -> Dict:
        data = {
            "model": model,
            "description": description,
            "size": size,
            "variations": variations,
            **kwargs
        }

        # Use longer timeout for image generation (varies by model complexity)
        # Multiple variations can take significantly longer
        timeout_multiplier = max(variations, 1)
        extended_timeout = min(120, 60 + (timeout_multiplier * 20))  # 60s base + 20s per variation, max 120s

        return await self._make_request_with_timeout("POST", "/v1/image/generation", data, extended_timeout)

    async def generate_video(self, prompt: str, model: str = "runway-gen3", **kwargs) -> Dict:
        data = {
            "prompt": prompt,
            "model": model,
            **kwargs
        }
        # Video generation typically takes longer
        return await self._make_request_with_timeout("POST", "/videos/generations", data, 90)

    async def get_generation_status(self, generation_id: str) -> Dict:
        return await self._make_request("GET", f"/generations/{generation_id}")