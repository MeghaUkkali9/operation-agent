import re
from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import get_settings
from app.rag.loader import LoadedDocument

SECTION_PATTERN = re.compile(r"^## (\d+)\. (.+)$", re.MULTILINE)


@dataclass
class Chunk:
    chunk_id: str
    document_name: str
    document_type: str
    section: str
    text: str


def split_into_sections(text: str) -> list[tuple[str, str]]:
    matches = list(SECTION_PATTERN.finditer(text))
    sections = []
    for i, match in enumerate(matches):
        section_number, section_title = match.group(1), match.group(2)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = f"{section_title}\n\n{text[start:end].strip()}"
        sections.append((section_number, section_text))
    return sections


def chunk_document(document: LoadedDocument, splitter: RecursiveCharacterTextSplitter) -> list[Chunk]:
    chunks = []
    for section_number, section_text in split_into_sections(document.text):
        for i, piece in enumerate(splitter.split_text(section_text)):
            chunks.append(
                Chunk(
                    chunk_id=f"{document.document_type}-s{section_number}-{i:02d}",
                    document_name=document.document_name,
                    document_type=document.document_type,
                    section=section_number,
                    text=piece,
                )
            )
    return chunks


def chunk_documents(documents: list[LoadedDocument]) -> list[Chunk]:
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return [chunk for document in documents for chunk in chunk_document(document, splitter)]
