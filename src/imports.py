from dataclasses import dataclass, field
from pathlib import Path

from visitor import Scope


@dataclass
class MyImport:
    name: str
    path: Path
    parents: set[Path]
    scope: Scope = field(default_factory=dict)


class ImportManager:
    def __init__(self):
        self._imports: dict[Path, MyImport] = {}

    def create_import(
        self, name: str, path: Path | str, parent: Path | str
    ) -> MyImport:
        if isinstance(path, str):
            path = Path(path).absolute().resolve()
        if isinstance(parent, str):
            parent = Path(parent).absolute().resolve()
        if path not in self._imports:
            my_import = MyImport(name=name, path=path, parents={parent})
            self._imports[path] = my_import
        else:
            my_import = self._imports[path]
            my_import.parents.add(parent)
        return my_import

    def get_import_by_name(self, name: str) -> MyImport | None:
        for my_import in self._imports.values():
            if my_import.name == name:
                return my_import
        return None

    def get_import_by_path(self, path: Path) -> MyImport | None:
        return self._imports.get(path)
