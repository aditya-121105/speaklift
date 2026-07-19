import logging
from typing import Any

import pdfplumber

logger = logging.getLogger(__name__)


class DocumentReconstructionEngine:
    """
    Reconstructs the logical reading order of a document.
    Detects layouts (single-column vs multi-column) and preserves block relationships
    (e.g., aligning dates or technologies on the right with titles on the left).
    """

    def __init__(self, y_tolerance: float = 5.0, x_tolerance: float = 5.0):
        self.y_tolerance = y_tolerance
        self.x_tolerance = x_tolerance

    def reconstruct(self, page: pdfplumber.page.Page) -> str:
        """
        Reconstruct the logical reading order of a single page.
        """
        boxes = page.textboxhorizontals
        if not boxes:
            # Fallback if laparams weren't used or no text boxes detected
            text = page.extract_text(layout=False)
            return text or ""

        # Group boxes by row based on top coordinate
        rows: list[float] = []
        box_rows: dict[float, list[dict[str, Any]]] = {}

        for box in boxes:
            y = box["top"]
            # Find matching row within tolerance
            matching_row = None
            for r in rows:
                if abs(r - y) <= self.y_tolerance:
                    matching_row = r
                    break
            
            if matching_row is None:
                rows.append(y)
                matching_row = y
                box_rows[matching_row] = []
                
            box_rows[matching_row].append(box)

        # Sort rows top to bottom
        sorted_rows = sorted(rows)

        page_text = []
        last_y = None
        
        for r in sorted_rows:
            # Sort boxes in this row left to right
            row_boxes = sorted(box_rows[r], key=lambda b: b["x0"])
            
            # If there's a significant vertical gap, insert a blank line
            # We use 8.0 points as a threshold because paragraphs within a block
            # have a gap of ~5.8-6.0 pt, while new major blocks have a gap > 9.0 pt.
            if last_y is not None and (r - last_y) > 8.0:
                page_text.append("")  # This will create an extra newline when joined
                
            # Update last_y based on the bottom of the lowest box in this row
            # If it's a multi-line box, we want to know its bottom to measure gap to next row
            row_bottom = max(b["bottom"] for b in row_boxes)
            last_y = row_bottom
            
            # Join boxes on the same row with a space
            row_text_parts = []
            for b in row_boxes:
                # Remove trailing newlines from within the box to keep it clean
                text = b["text"].strip()
                if text:
                    row_text_parts.append(text)
            
            if row_text_parts:
                # If there are multiple boxes in the same row, it implies columns
                # We separate them with a " | " to help downstream extractors parse them
                row_str = " | ".join(row_text_parts)
                page_text.append(row_str)

        return "\n".join(page_text)
