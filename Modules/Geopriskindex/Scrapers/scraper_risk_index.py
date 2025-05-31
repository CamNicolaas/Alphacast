from bs4 import BeautifulSoup
from Utils.FetchMethods import FetchsMethodsClass
from Utils.Exceptions import (
    ErrorEstructureHTMLNotFound,
    ErrorFormatterData
)


class ScraperGeoPoliticalRiskIndex(FetchsMethodsClass):
    def __init__(self):
        super().__init__()


# ---------- Scraping Data ----------
    async def get_risk_table(self,
        url_website:str = "https://www.geopriskindex.com/results-final-risk-index/"
    ) -> list[dict[str, str]]:
        
        status_code, response = await self.fetch_GET(
            url = url_website,
            #proxy = "",
            timeout_seconds = 10,
            return_json = False,
            headers = self.gen_new_headers()
        )
        if not status_code:
            return False, f"Req. Error Trying To Retrieve Table... | Code: {status_code} | Message : {response}"

        return self.parsing_get_table_content(response)



# ---------- Parsing Data ----------
    # --- Return Ready Data ---
    def parsing_get_table_content(self, 
        response:str
    ) -> list[dict[str, str]]:
        
        soup = BeautifulSoup(response, "html.parser")

        # --- Get Headers Table ---
        headers = self.parsing_get_headers(soup)
        # --- Return Formatted Content Tabble ---
        return self.parsing_get_data(soup, headers)

    # --- Parsing Headers ---
    def parsing_get_headers(self, 
        soup:BeautifulSoup
    ) -> list[str]:

        try:
            columns_raw = soup.find("tr", {"class" : "footable-header"})
            if not columns_raw:
                raise ErrorEstructureHTMLNotFound(
                    message = f'Table Could Not Be Found, Appears HTML Has Changed... ',
                    context = {
                        "error_type": 'ErrorEstructureHTMLNotFound',
                        "error_msg": 'The Headers For The Table "Final Geopolitical Risk Index" Could Not Be Found.'
                    }
                )
            return [
                parsing_column.replace('\ufeff', '')  for column in columns_raw if (parsing_column := column.text.strip())
            ]

        except Exception as err:
            raise ErrorFormatterData(f"Error Fatal Occurred While Formatting HTML Body....",
                context = {
                    "error_type": type(err).__name__,
                    "error_msg": str(err)
                }
            ) from err

    # --- Parsing Table Data ---
    def parsing_get_data(self,
        soup:BeautifulSoup,
        headers:list[str]
    ) -> list[dict[str, str]]:
        
        try:
            table_raw = soup.find("tbody")
            if not table_raw:
                raise ErrorEstructureHTMLNotFound(
                    message = f'Table Could Not Be Found, Appears HTML Has Changed... ',
                    context = {
                        "error_type": 'ErrorEstructureHTMLNotFound',
                        "error_msg": 'The Contents Of The Table "Final Geopolitical Risk Index" Could Not Be Found.'
                    }
                )
            data = list()
            for row in table_raw.find_all("tr"):
                campo = row.find_all("td")
                record_row = dict()

                for i, header in enumerate(headers):
                    record_row[header] = campo[i].text.strip() if i < len(campo) else None
                data.append(record_row)
            return True, data

        except Exception as err:
            raise ErrorFormatterData(f"Error Fatal Occurred While Formatting HTML Body....",
                context = {
                    "error_type": type(err).__name__,
                    "error_msg": str(err)
                }
            ) from err