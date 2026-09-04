from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
import visitor


@dataclass
class ProgramBody:
    func_defs: dict[str, str] = field(default_factory=dict)
    funcs: dict[str, str] = field(default_factory=dict)
    structs: dict[str, str] = field(default_factory=dict)
    classes: dict[str, str] = field(default_factory=dict)

    def to_str(self) -> str:
        result = StringIO()
        for func in self.funcs.values():
            result.write(f"{func}\n")
        for struct in self.structs.values():
            result.write(f"{struct};\n")
        for _class in self.classes.values():
            result.write(f"{_class};\n")
        result.seek(0)
        return result.read()
        

@dataclass
class MyImport:
    name: str
    path: Path
    parents: set[Path]
    body: ProgramBody
    scope: visitor.Scope = field(default_factory=dict)


class ImportManager:
    def __init__(self):
        self._imports: dict[Path, MyImport] = {}
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._imports):
            self._index = 0
            raise StopIteration
        item = list(self._imports.values())[self._index]
        self._index += 1
        return item

    def create_import(
        self, name: str, path: Path | str, parent: Path | str
    ) -> MyImport:
        if isinstance(path, str):
            path = Path(path).absolute().resolve()
        if isinstance(parent, str):
            parent = Path(parent).absolute().resolve()
        if path not in self._imports:
            my_import = MyImport(name=name, path=path, parents={parent}, body=ProgramBody())
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
