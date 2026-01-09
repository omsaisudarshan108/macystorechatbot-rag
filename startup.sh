#!/bin/bash
# Startup script to download required models and data

echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt_tab')"

echo "Pre-downloading embedding models..."
python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; SentenceTransformer('all-MiniLM-L6-v2'); CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

echo "Startup complete!"
