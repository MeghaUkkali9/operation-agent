from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.chunking import chunk_document, chunk_documents, split_into_sections
from app.rag.loader import LoadedDocument, load_documents

EXPECTED_DOCUMENT_TYPES = {
    "terminal_operations_manual",
    "damaged_container_handling",
    "reefer_container_handling",
    "yard_safety_procedure",
    "vessel_operations_procedure",
    "container_inspection_procedure",
    "delay_management_procedure",
}


def test_load_documents_finds_all_seven():
    documents = load_documents()
    assert {d.document_type for d in documents} == EXPECTED_DOCUMENT_TYPES


def test_load_documents_extracts_title_from_heading():
    documents = load_documents()
    damaged = next(d for d in documents if d.document_type == "damaged_container_handling")
    assert damaged.document_name == "Damaged Container Handling Procedure"


def test_split_into_sections_uses_numbered_headings():
    text = "# Title\n\nintro\n\n## 1. First\n\nfirst body\n\n## 2. Second\n\nsecond body\n"
    sections = split_into_sections(text)

    assert [number for number, _ in sections] == ["1", "2"]
    assert "first body" in sections[0][1]
    assert "second body" in sections[1][1]
    assert "second body" not in sections[0][1]


def test_chunks_respect_chunk_size():
    long_body = " ".join(f"word{i}" for i in range(300))
    text = f"# Title\n\n## 1. Long Section\n\n{long_body}\n"
    document = LoadedDocument(document_name="Test Doc", document_type="test_doc", text=text)
    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)

    chunks = chunk_document(document, splitter)

    assert len(chunks) > 1
    assert all(len(c.text) <= 100 for c in chunks)


def test_chunk_overlap_shares_content_between_adjacent_chunks():
    long_body = " ".join(f"word{i}" for i in range(300))
    text = f"# Title\n\n## 1. Long Section\n\n{long_body}\n"
    document = LoadedDocument(document_name="Test Doc", document_type="test_doc", text=text)
    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)

    chunks = chunk_document(document, splitter)

    # chunks[0] is just the short section heading; the body starts splitting from chunks[1]
    words_a = set(chunks[1].text.split())
    words_b = set(chunks[2].text.split())
    assert words_a & words_b


def test_chunk_metadata_is_populated():
    documents = load_documents()
    chunks = chunk_documents(documents)

    sample = chunks[0]
    assert sample.chunk_id
    assert sample.document_name
    assert sample.document_type in EXPECTED_DOCUMENT_TYPES
    assert sample.section.isdigit()


def test_chunk_ids_are_unique_across_corpus():
    documents = load_documents()
    chunks = chunk_documents(documents)

    chunk_ids = [c.chunk_id for c in chunks]
    assert len(chunk_ids) == len(set(chunk_ids))
