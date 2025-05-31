import asyncio, json, os, aiofiles
from typing import Any, Optional
from Utils.Tools import SingletonClass


class AsyncConfigManager(metaclass = SingletonClass):
    def __init__(self, 
        config_path:Optional[str] = "general_settings.json"
    ):
        if hasattr(self, "initialized"):
            return
        
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_path)
        self.config_data = None
        self._lock = asyncio.Lock()
        self.initialized = True

    # --- Load Data From Json ---
    async def __load_config(self):
        async with self._lock:
            if not self.config_data:
                if not os.path.exists(self.config_path):
                    raise FileNotFoundError(f"File Not Found At {self.config_path}")
                async with aiofiles.open(self.config_path, mode="r", encoding="utf-8") as f:
                    content = await f.read()
                    self.config_data = json.loads(content)

    # --- Loaded Data ---
    async def get_configs(self, 
        *keys: str
    ) -> Optional[Any]:
        await self.__load_config()
        data = self.config_data
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None
        return data


    async def get_all_configs(self) -> dict:
        await self.__load_config()
        return self.config_data
