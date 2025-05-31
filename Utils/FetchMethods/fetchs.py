import aiohttp, asyncio, json
from aiohttp import ClientResponse
from typing import Optional, Union
from browserforge.headers import HeaderGenerator
from Utils.Exceptions import ScrapersError
from Utils.Tools import SingletonClass



class FetchsMethodsClass(metaclass = SingletonClass):
    def __init__(self):
        # --- Idea agregar un sistema independiente de Proxys ---
        pass
        

# ---------- Handler Fetch ----------
    # --- Main Func. ---
    async def __fetch_request(
        self,
        url:str = "https://httpbin.org/anything",
        method:str = "GET",
        timeout_seconds:Optional[int] = 15,
        return_json:bool = True,
        proxy:Optional[Union[str, dict[str, str]]] = None,
        session:Optional[aiohttp.ClientSession] = None,
        headers:Optional[dict] = None,
        **kwargs
    ) -> tuple[int, Union[dict, str]]:
        
        status_code = None
        owns_session = False

        try:
            if not session:
                session = aiohttp.ClientSession(
                    timeout = aiohttp.ClientTimeout(total = timeout_seconds),
                    cookie_jar = aiohttp.DummyCookieJar()
                )
                owns_session = True

            request_method = getattr(session, method.lower())

            async with request_method(url, proxy = self.proxy_formater(proxy), headers = headers, **kwargs) as response:
                status_code = response.status
                return await self.check_response(response, return_json)

        except Exception as err:
            return status_code, f"Error: {type(err).__name__} - {err}"

        finally:
            if owns_session:
                await self.close_session(session)


    # --- Func. GET ---
    async def fetch_GET(self, 
        url:str,
        timeout_seconds:Optional[int] = 15,
        return_json:bool = True, 
        proxy:Optional[Union[str, dict[str, str]]] = None, 
        headers:Optional[dict[str, str]] = None,
        cookies:Optional[dict] = None,
        session:Optional[aiohttp.ClientSession] = None,
        **kwargs:Optional[dict]
    ) -> tuple[int, Union[dict, str]]:
        
        return await self.__fetch_request(
            url = url,
            method = "GET",
            timeout_seconds = timeout_seconds,
            return_json = return_json,
            proxy = proxy,
            headers = headers,
            cookies = cookies,
            session = session,
            **kwargs
        )

    # --- Func. POST ---
    async def fetch_POST(self, 
        url:str,
        timeout_seconds:Optional[int] = 15,
        return_json:bool = True, 
        proxy:Optional[Union[str, dict[str, str]]] = None, 
        headers:Optional[dict[str, str]] = None,
        cookies:Optional[dict] = None,
        session:Optional[aiohttp.ClientSession] = None,
        **kwargs:Optional[dict]
    ) -> tuple[int, Union[dict, str]]:
        
        return await self.__fetch_request(
            url = url,
            method = "POST",
            timeout_seconds = timeout_seconds,
            return_json = return_json,
            proxy = proxy,
            headers = headers,
            cookies = cookies,
            session = session,
            **kwargs
        )



# ------------ Tools ------------
    # --- Create Session ---
    def create_session(self,
        headers:Optional[dict[str, str]] = None,
        update_headers:bool = True,
        cookies:Optional[dict[str, str]] = None,
        timeout_seconds:int = 15
    ) -> aiohttp.ClientSession:

        new_cookies = aiohttp.CookieJar()
        if cookies:
            for k, v in cookies.items():
                new_cookies.update_cookies({k: v})

        session = aiohttp.ClientSession(
            cookie_jar = new_cookies,
            headers = self.gen_new_headers(headers) if update_headers else headers,
            timeout = aiohttp.ClientTimeout(total = timeout_seconds)
        )
        return session

    # --- Close Session ---
    async def close_session(self,
        session:aiohttp.ClientSession
    ) -> bool:
        
        if session.closed:
            return True
        
        await session.close()
        return session.closed
    
    # --- Proxy Formater ---
    def proxy_formater(self, 
        proxy:Optional[Union[str, dict[str, str]]] = None
    ) -> str:
        if not proxy:
            return ""
        
        elif isinstance(proxy, str):
            proxy_parts = proxy.split(":")
            if "http" in proxy and (len(proxy_parts) > 1 or ":" in proxy.split("@")[1]):
                return proxy
            elif len(proxy_parts) == 2:
                return f"http://{proxy}"
            elif len(proxy_parts) == 4:
                return f"http://{proxy_parts[2]}:{proxy_parts[3]}@{proxy_parts[0]}:{proxy_parts[1]}"
            
        elif isinstance(proxy, dict) and "http" in proxy:
            return proxy["http"]
        
        raise ValueError(
            'Invalid Proxy, Check the Format, it Could Be:\n'
            '- str: "ip:port" (example., "xxx.xxx.x.x:xxxx")\n'
            '- str: "http://user:password@ip:port"\n'
            '- dict: {"http": "http://user:password@ip:port", "https": "http://user:password@ip:port"}'
        )

    # --- Gen. Headers ---
    def gen_new_headers(self,
        args:Optional[dict[str, str]] = None
    ) -> dict[str, str]:
        
        fake_headers = HeaderGenerator(
            browser = ('chrome', 'safari', 'edge'),
            os = ('windows', 'macos', 'android', 'ios'),
            device = ('desktop', 'mobile'),
            locale = ('en-US', 'en', 'de'),
            http_version = 2
        )
        headers = fake_headers.generate()
        if args:
            for key, value in args.items():
                headers[key] = value
        return headers

    # --- Check Response ---
    async def check_response(self, 
        response:ClientResponse, 
        return_json:bool
    ) -> tuple[int, Union[dict, str]]:

        try:
            content = await response.json() if return_json else await response.text()
            return response.status, content

        except (json.JSONDecodeError):
            raise ScrapersError(
                f"An error occurred while parsing the server response... | Code: {response.status} | Headers: {response.headers} | Content: {response.text}"
            )
