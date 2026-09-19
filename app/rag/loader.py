from dataclasses import dataclass
from pathlib import Path

DOCUMENTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "documents"


@dataclass
class LoadedDocument:
    document_name: str
    document_type: str
    text: str


def load_documents(documents_dir: Path = DOCUMENTS_DIR) -> list[LoadedDocument]:
    return [_load_document(path) for path in sorted(documents_dir.glob("*.md"))]


def _load_document(path: Path) -> LoadedDocument:
    text = path.read_text()
    return LoadedDocument(
        document_name=_extract_title(text),
        document_type=path.stem,
        text=text,
    )


def _extract_title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled Document"
