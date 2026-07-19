import pytest
from app.ai.document_processing.layout_reconstructor import DocumentReconstructionEngine
from unittest.mock import MagicMock

def test_document_reconstruction_engine_merges_columns():
    engine = DocumentReconstructionEngine()
    
    # Mock a PDF page with boxes on the same line
    mock_page = MagicMock()
    mock_page.textboxhorizontals = [
        {"text": "Software Engineer", "top": 100.0, "bottom": 110.0, "x0": 50.0, "x1": 150.0},
        {"text": "June 2025", "top": 100.5, "bottom": 110.5, "x0": 300.0, "x1": 380.0},
    ]
    
    text = engine.reconstruct(mock_page)
    
    assert "Software Engineer | June 2025" in text

def test_document_reconstruction_engine_inserts_paragraph_gaps():
    engine = DocumentReconstructionEngine()
    
    # Mock a PDF page with a significant vertical gap between two paragraphs
    mock_page = MagicMock()
    mock_page.textboxhorizontals = [
        {"text": "First paragraph ending.", "top": 100.0, "bottom": 110.0, "x0": 50.0, "x1": 200.0},
        # Gap > 8.0 points (current top - previous bottom)
        {"text": "Second paragraph starting.", "top": 125.0, "bottom": 135.0, "x0": 50.0, "x1": 200.0},
    ]
    
    text = engine.reconstruct(mock_page)
    
    assert "First paragraph ending.\n\nSecond paragraph starting." in text

def test_document_reconstruction_engine_preserves_close_lines():
    engine = DocumentReconstructionEngine()
    
    # Mock a PDF page with tightly packed lines (gap <= 8.0 points)
    mock_page = MagicMock()
    mock_page.textboxhorizontals = [
        {"text": "Line one of paragraph.", "top": 100.0, "bottom": 110.0, "x0": 50.0, "x1": 200.0},
        # Gap = 115.0 - 110.0 = 5.0 <= 8.0
        {"text": "Line two of paragraph.", "top": 115.0, "bottom": 125.0, "x0": 50.0, "x1": 200.0},
    ]
    
    text = engine.reconstruct(mock_page)
    
    assert "Line one of paragraph.\nLine two of paragraph." in text
