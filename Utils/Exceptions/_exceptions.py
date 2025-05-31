from typing import Optional

# ---------- General Exception ----------
class AlphacastExceptions(Exception):
    def __init__(self, 
        message:Optional[str] = None, 
        *, 
        context:Optional[dict] = None
    ):
        super().__init__(message)
        self.context = context

    def __str__(self):
        return f'{super().__str__()} {con if (con := self.context) else ""}'
    

# ---------- Scrapers Exceptions ----------
class ScrapersError(AlphacastExceptions):
    def __init__(self, 
        message: str,
        *, 
        context:Optional[dict] = ""
    ) -> None:
        super().__init__(message, context = context)


class InvalidFormatHTML(ScrapersError):...
class ErrorEstructureHTMLNotFound(ScrapersError):...
class ErrorFormatterData(ScrapersError):...


# ---------- Modules Exceptions ----------
class GeopoliticalRiskError(AlphacastExceptions):
    def __init__(self, 
        message: str,
        *, 
        context:Optional[dict] = ""
    ) -> None:
        super().__init__(message, context = context)

class ExceptionTableResults(GeopoliticalRiskError):...
class ErrorUnexpected(GeopoliticalRiskError):...


# ---------- AphaCast SKD Exceptions ----------
class AlphaCastAPIError(AlphacastExceptions):
    def __init__(self, 
        message: str,
        *, 
        context:Optional[dict] = ""
    ) -> None:
        super().__init__(message, context = context)

class ErrorAuthenticationAccount(AlphaCastAPIError):...
class InvalidIDRepository(AlphaCastAPIError):...
class ErrorCreateNewDataset(AlphaCastAPIError):...
class ErrorUploadDataset(AlphaCastAPIError):...