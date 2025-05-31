import asyncio, dotenv, json
import pandas as pd
from pathlib import Path
from alphacast import Alphacast
from typing import Optional, Union
from Configs import AsyncConfigManager
from Utils.Notify import NotifyDiscord
from Modules.Geopriskindex import TransformDataGeoPoliticalRiskIndex
from Utils.Exceptions import (
    # --- GeoPolitical ---
    ErrorUnexpected,
    # --- AlphaCast API Exceptions ---
    ErrorAuthenticationAccount,
    InvalidIDRepository,
    ErrorCreateNewDataset,
    ErrorUploadDataset
)



class MainManagerGeopoliticalRisk:
    def __init__(self,
        token_alphacast:Optional[str] = None
    ):
        # --- Configs ENV ---
        tokens = dotenv.dotenv_values()
        # --- Configs ---
        self.configs:dict[str, any] = None
        # --- Notify Center ---
        self.notify = NotifyDiscord()
        # --- AlphaCast ---
        self.alphacast = Alphacast(token_alphacast if token_alphacast else tokens["API_KEY_ALPHACAST"])
        # --- Geo Political Manager ---
        self.manager_data = TransformDataGeoPoliticalRiskIndex()
        # --- Logger ---


# ---------- Main Method ----------
    async def create_new_process(self) -> None:
        try:
            # --- Load Configs ---
            await self.load_configs()

            # --- Gen. Dataset --- 
            df_result, path_file = await self.prepair_dataset()

            # --- Prepair & Upload Results ---
            response_api = self.upload_results(df_result)

            # --- Send Notify ---
            if self.configs["notify_system"]["send_notify"]:
                await self.notify.webhook_control_success(
                    company = self.configs["notify_system"],
                    dataset_data = {
                        'dataset_link': f'https://www.alphacast.io/datasets/{response_api["datasetId"]}',
                        'dataset_id': response_api["datasetId"],
                        'api_response': response_api
                    }
                )
            
        except Exception as err:
            await self.notify.webhook_control_error(
                company = self.configs["notify_system"],
                problem_logs = f'An error occurred; the process could not be completed... | Message: {err}'
            )



# ---------- Prepaid Dataset ----------
    # --- Gen. New Dataset ---
    async def prepair_dataset(self) -> list[pd.DataFrame, Union[None, Path]]:
        try:
            # --- DownLoad Table ---
            await self.manager_data.download_risk_table()

            # --- Transform To df ---
            df_result = self.manager_data.transform_data_to_pd(
                #results = table,
                convert_to_datetime = {
                    "year": "%Y-%m-%d"
                },
                numeric_columns = {
                    "Final Index": float,
                    "Political Risk Index": float,
                    "Government Interference Index": float,
                    "Globalization Index": float,
                    "Conflict & Unrest Index": float,
                    "Geographical Risk Index": float,
                    "Geoeconomic Dependency Index": float
                },
                rename_columns = {
                    "Final Index": "Financial Index",
                    "Year": "Date"
                },
                order_columns = [
                    "Year", "Country", "Final Index", "Political Risk Index",
                    "Government Interference Index", "Globalization Index",
                    "Conflict & Unrest Index", "Geographical Risk Index", "Geoeconomic Dependency Index", "region"
                ]
            )

            if not self.configs["general"]["upload_csv_files"]:
                return df_result, None

            # --- Save Result in .csv File ---
            status, file_path = await self.manager_data.save_table_result(
                file_name = self.configs["general"]["file_csv_name"],
                folder = self.configs["general"]["folder_files_csv"],
                data = df_result
            )

            # --- DF & CSV File Path ---
            return df_result, file_path
    
        except Exception as err:
            raise ErrorUnexpected(
                message = f'An Unexpected Error Occurred While Generating Dataset From Geo Political...',
                context = {
                    "error_type": type(err).__name__,
                    "error_msg": str(err)
                }
            )



# ---------- AlphaCast SDK ----------
    # --- Main ---
    def upload_results(self,
        df_upload:pd.DataFrame
    ) -> dict[str, any]:
        
        # --- Check Login ---
        self.check_auth_api()

        # --- Check Repo´s ---
        self.check_repository_exists()

        # --- Create Dataset ---
        response_dataset = self.create_new_dataset()

        # --- Upload Dataset ---
        response_upload = self.upload_dataset(
            dataset_id = response_dataset["id"],
            df = df_upload
        )
    
        if isinstance(response_upload, bytes):
            response_upload = response_upload.decode("utf-8")
        if isinstance(response_upload, str):
            return json.loads(response_upload)
        
        return response_upload


    # --- Login ---
    def check_auth_api(self) -> list[dict[str, any]]:
        try:
            return self.alphacast.repository.read_all()

        except Exception as err:
            raise ErrorAuthenticationAccount(
                message = f'Error Failed To Authenticate AlphaCast API... ',
                context = {
                    "error_type": type(err).__name__,
                    "error_msg": str(err)
                }
            )

    # --- Check Repository ---
    def check_repository_exists(self) -> list[dict[str, any]]:
        repository_id = self.configs["general"]["repository_id_upload"]
        try:
            return self.alphacast.repository.read_by_id(repository_id)
        
        except Exception as err:
            raise InvalidIDRepository(
                message = f'Error, Not Retrieve Metadata From Repository: {repository_id}',
                context = {
                    "error_type": type(err).__name__,
                    "error_msg": str(err)
                }
            )
    
    # --- Create New DataSet in Repository ---
    def create_new_dataset(self,
        dataset_name:Optional[str] = None,
        repository_id:Optional[Union[str, int]] = None,
        dataset_scription:Optional[str] = None
    ) -> list[dict[str, any]]:
        
        if not dataset_name:
            dataset_name = self.configs["general"]["dataset_name"]
        if not repository_id:
            repository_id = self.configs["general"]["repository_id_upload"]
        if not dataset_scription:
            dataset_scription = self.configs["general"]["dataset_description"]

        try:
            response = self.alphacast.datasets.create(
                dataset_name = dataset_name, 
                repo_id = repository_id,
                description = dataset_scription,
                returnIdIfExists = True
            )
            if response.get("id") and response.get("createdAt"):
                return response
            
            raise ErrorCreateNewDataset(
                message = f'Unknown Error, Could Not Create New Dataset...',
                context = {
                    "error_type": "ErrorCreateNewDataset",
                    "error_msg": response
                }
            )
        
        except Exception as err:
            raise ErrorCreateNewDataset(
                message = f'Error, Unable Create Dataset | Params.: "dataset_name": {dataset_name}, "repository_id": {repository_id}, "description":{dataset_scription}',
                context = {
                    "error_type": type(err).__name__,
                    "error_msg": str(err)
                }
            )

    # --- Upload New Dataset ---
    def upload_dataset(self,
        dataset_id:Union[str, int],
        df:pd.DataFrame
    ): #No esta formateada la salida de la API
        try:
            return self.alphacast.datasets.dataset(dataset_id).upload_data_from_df(
                df = df,
                uploadIndex = False,
                dateColumnName = "Date",
                dateFormat = "%Y-%m-%d",
                entitiesColumnNames = ['Country'],
                stringColumnNames = ['Region'],
                acceptNewColumns = True
            )

        except Exception as err:
            raise ErrorUploadDataset(
                message = f'Error: Could Not Load New Dataset... | DatasetID: {dataset_id}',
                context = {
                    "error_type": type(err).__name__,
                    "error_msg": str(err)
                }
            )



# ---------- Tools ----------
    # --- Load Configs ---
    async def load_configs(self) -> None:
        configs = AsyncConfigManager()
        self.configs = {
            "general": await configs.get_configs("GeopoliticalRiskIndex", "general_configs"),
            "notify_system": await configs.get_configs("GeopoliticalRiskIndex", "notify_system")
        }





# ---- Init Process ---
async def main():
    manager = MainManagerGeopoliticalRisk()
    await manager.create_new_process()

if __name__ == "__main__":
    asyncio.run(main())