# backend/ingestion/loaders.py

from pypdf import PdfReader
from docx import Document
from pathlib import Path


class DocumentProcessor:
    def __init__(self, document_paths: Path | list[Path]) -> None:
        self.document_dict: dict[str, str] = {}

        if isinstance(document_paths, (str, Path)):
            document_paths = [Path(document_paths)]
        else:
            document_paths = [Path(p) for p in document_paths]

        for doc_path in document_paths:
            suffix = doc_path.suffix.lower()

            try:
                if suffix == ".pdf":
                    self.document_dict[doc_path.name] = self._load_pdf(doc_path)

                elif suffix == ".docx":
                    self.document_dict[doc_path.name] = self._load_docx(doc_path)

                elif suffix == ".txt":
                    self.document_dict[doc_path.name] = doc_path.read_text(encoding="utf8")

                else:
                    print(f"Skipping unsupported file: {doc_path.name}")

            except Exception as e:
                print(f"Failed processing {doc_path.name}: {e}")

    def _load_pdf(self, path: Path) -> str:
        reader = PdfReader(path)
        return "\n".join([p.extract_text() or "" for p in reader.pages])

    def _load_docx(self, path: Path) -> str:
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
