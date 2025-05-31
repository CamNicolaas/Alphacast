import pandas as pd
from pathlib import Path
from typing import Union, Optional
from Modules.Geopriskindex import ScraperGeoPoliticalRiskIndex
from Utils.FilesManager import (
    CSVFilesManager,
    create_route_folder,
    create_folder
)
from Utils.Exceptions import(
    ExceptionTableResults
)



class TransformDataGeoPoliticalRiskIndex(ScraperGeoPoliticalRiskIndex):
    def __init__(self,
        new_list_result:Optional[list] = None,
        dataframe:Optional[pd.DataFrame] = None
    ):
        super().__init__()
        # --- Scraping Result & DataFrame ---
        self.new_list_result = new_list_result
        self.results_dataframe = dataframe


# ---------- Get Data ----------
    # --- Get New Table ---
    async def download_risk_table(self) -> list[dict[str, str]]:
        status, response = await self.get_risk_table()
        if not status:
            raise ExceptionTableResults(
                message = f'Error, Table Could Not Be Retrieved... ',
                context = {
                    "error_type": 'ExceptionTableResults',
                    "error_msg": response
                }
            )
        self.new_list_result = response
        return response


# ---------- Parsing Data ----------
    # --- Transform Response ---
    def transform_data_to_pd(self,
        results:Optional[list[dict[str, str]]] = None,
        numeric_columns:Optional[dict[str, type]] = None,
        convert_to_datetime:Optional[dict[str, str]] = None,
        order_columns:Optional[list[str]] = None,
        rename_columns:Optional[dict[str, str]] = None
    ) -> pd.DataFrame:
        
        if not self.new_list_result and not results:
            raise ValueError("[TransformDataToPd] Error, Method Need Data Source...")

        if results:
            self.new_list_result = results

        df = pd.DataFrame(self.new_list_result)
        if not any([numeric_columns, convert_to_datetime, order_columns, rename_columns]):
            return df

        df.columns = [column.lower() for column in df.columns]
        # --- Convert Columns text to Float ---
        if numeric_columns:
            for column, coltype in numeric_columns.items():
                column_lower = column.lower()
                if column_lower not in df.columns:
                    raise KeyError(f'[NumericColumns] Error Searching Column [{column}] in DataFrame...')
                try:
                    df[column_lower] = df[column_lower].astype(coltype)
                except Exception as err:
                    raise ValueError(f'[NumericColumns] Error Converting Column [{column}] to "{coltype}" | Message: {err}')

        # --- Convert Date Columns ---
        if convert_to_datetime:
            for column, colfotmat in convert_to_datetime.items():
                column_lower = column.lower()
                if column_lower not in df.columns:
                    raise KeyError(f'[ConvertToTime] Error Searching Column [{column}] in DataFrame...')
                try:
                    df[column_lower] = pd.to_datetime(df[column_lower], errors = "coerce")

                    if df[column_lower].isnull().any():
                        raise ValueError(f"[ConvertToTime] Some values in column [{column}] could not be parsed as dates.")
                    
                    df[column_lower] = df[column_lower].dt.strftime(colfotmat)

                except Exception as err:
                    raise ValueError(f'[ConvertToTime] The Data In Column [{column}] Cannot Be Converted To Time Format. | Message: {err}')

        # --- Reorder Columns ---
        if order_columns:
            order_columns = [columns.lower() for columns in order_columns]

            df_columns = set(df.columns)
            reorder_columns = set(order_columns)

            result_actual_order = df_columns - reorder_columns
            if result_actual_order:
                raise ValueError(f'[OrderColumns] Error Reorganizing Columns, Missing: [{result_actual_order}]')
            
            result_new_order = reorder_columns - df_columns
            if result_new_order:
                raise ValueError(f'[OrderColumns] Error Reorganizing Columns, Column [{result_new_order}] Not Exist In DataFrame...')

            df = df[order_columns]

        # --- Rename Columns ---
        if rename_columns:
            update_columns = dict()
            for old_column, new_column in rename_columns.items():
                column_lower = old_column.lower()
                if column_lower not in df.columns:
                    raise KeyError(f'[RenameColumns] Error Searching Column [{old_column}] in DataFrame...')
                update_columns[column_lower] = new_column.lower()

            df = df.rename(columns = update_columns)

        df.columns = [column.title() for column in df.columns]

        self.results_dataframe = df
        return df

    # --- Save Data to CSV ---
    async def save_table_result(self,
        file_name:str,
        folder:Optional[Path] = "Data/Geopriskindex",
        data:Optional[pd.DataFrame] = None
    ) -> list[bool, Union[Path, str]]:

        if (data is None and self.results_dataframe.empty):
            raise ValueError('[SaveTableResult] Error, Method Need Data Source...')

        if data is not None:
            self.results_dataframe = data

        # --- Set Root Folder ---
        root = create_folder(create_route_folder(folder))

        # --- Save Data ---
        manager = CSVFilesManager()
        return await manager.create_new_csv(
            filename = file_name,
            folder_path = root,
            data = self.results_dataframe
        )
