from backend.ingestion.loaders import DocumentProcessor
from pathlib import Path

processor = DocumentProcessor(
    [
        Path(r"D:\WORKSPACE\Macy_Chatbot\Macy's KB articles\all_docs\ELSKiosk_Issue.docx"),
        Path(r"D:\WORKSPACE\Macy_Chatbot\Macy's KB articles\uploaded\Expeditor on the CT40.pdf"),
        Path(r"D:\WORKSPACE\Macy_Chatbot\Macy's KB articles\uploaded\Handbook_2.txt")
    ]
    )

print(processor.document_dict.keys())
