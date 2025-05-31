from pathlib import Path
from typing import Union


def get_root_proyect() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def create_route_folder(
    relative_path:str
) -> Path:
    
    return Path(get_root_proyect()) / relative_path


def create_folder(
    path:Union[str, Path],
    base_path:Union[Path, None] = None
) -> Path:

    path = Path(path)
    if not path.is_absolute() and base_path:
        path = base_path / path

    path.mkdir(parents = True, exist_ok = True)
    return path.resolve()
