import os, io, csv, aiofiles
import pandas as pd
from pathlib import Path
from typing import Union
from Utils.Tools import SingletonClass
from Utils.FilesManager.files_tools import create_route_folder



class CSVFilesManager(metaclass = SingletonClass):
    def __init__(self):
        pass


# ---------- Manage Files ----------
    # --- List Csv Files ---
    async def list_csv_files(self,
        folder_path:str
    ) -> list[str]:

        return [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    # --- Create New CSV ---
    async def create_new_csv(self,
        filename:str,
        folder_path:str,
        data: Union[list[dict[str, str]], pd.DataFrame]
    ) -> list[bool, Union[Path, str]]:

        if not filename.endswith(".csv"):
            filename += ".csv"
        
        root = create_route_folder(folder_path)
        file_path = root / filename

        if isinstance(data, pd.DataFrame):
            return await self.__save_pd(file_path, data)
            
        elif isinstance(data, list) and data:
            return await self.__save_list(file_path, data)

        raise ValueError

    # --- Save PD to CSV ---
    async def __save_pd(self,
        root:str,
        data: pd.DataFrame
    ) -> list[bool, Union[Path, str]]:
        
        csv_data = data.to_csv(index = False)
        async with aiofiles.open(root, mode = "w", encoding = "utf-8") as file:
            await file.write(csv_data)
        return True, root
    
    # --- Save List to CSV ---
    async def __save_list(self,
        root:str,
        data: list[dict[str, str]]
    ) -> list[bool, Union[Path, str]]:

        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames = data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        async with aiofiles.open(root, mode = 'w', encoding = 'utf-8') as file:
            await file.write(buffer.getvalue())
        return True, root
        
    # --- Delete CSV ---
    async def delete_csv(self,
        file_path:Path,
    ) -> bool:
        if not os.path.exists(file_path):
            return False

        os.remove(file_path)
        return True
        