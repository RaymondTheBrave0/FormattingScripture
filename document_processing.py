"""
document_processing.py - Module for processing Word documents to standardize Bible references.
"""

from typing import Dict, List, Tuple, Optional
from docx import Document
from docx.text.paragraph import Paragraph
from bible_references import get_patterns
import re

def process_paragraph(paragraph: Paragraph, patterns: List[Tuple[re.Pattern, str]]) -> bool:
    """Process a single paragraph to standardize Bible references."""
    changed = False
    runs = list(paragraph.runs)
    
    if not runs:
        return False

    for i, run in enumerate(runs):
        if run.text:
            new_text, run_changed = process_run(run.text, patterns)
            if run_changed:
                run.text = new_text
                changed = True

    return changed

def process_run(text: str, patterns: List[Tuple[re.Pattern, str]]) -> Tuple[str, bool]:
    """Process a single run's text to standardize Bible references."""
    original_text = text
    changed = False

    for pattern, replacement_func in patterns:
        text = pattern.sub(replacement_func, text)

    # Clean up spaces after commas
    text = re.sub(r'(\d+),\s+(\d+)', r'\1,\2', text)

    # Handle multi-chapter references
    from bible_references import BIBLE_BOOKS
    text = re.sub(
        r'((?:' + '|'.join(map(re.escape, BIBLE_BOOKS.values())) + r')\s+)(\d+)-(\d+)(?!\s*:)',
        r'\1\2:1-\3:1',
        text,
        flags=re.IGNORECASE
    )

    # Clean up curly braces if they remain
    text = re.sub(r'\{([^}]+)\}', r'\1', text)

    changed = text != original_text
    return text, changed

def process_document(doc_path: str, output_path: Optional[str] = None, create_backup: bool = True) -> Dict:
    """Process a Word document to standardize Bible references."""
    from file_utils import create_backup

    result = {
        'success': False,
        'changes_made': False,
        'paragraphs_processed': 0,
        'paragraphs_changed': 0,
        'backup_path': None,
        'output_path': doc_path,
        'error': None
    }

    # Check if file exists
    import os
    if not os.path.exists(doc_path):
        result['error'] = f"File not found: {doc_path}"
        return result

    # Create backup
    if create_backup:
        backup_success, backup_result = create_backup(doc_path)
        if backup_success:
            result['backup_path'] = backup_result
        else:
            result['error'] = f"Failed to create backup: {backup_result}"
            return result

    try:
        # Get patterns
        patterns = get_patterns()

        # Open document
        document = Document(doc_path)

        # Process paragraphs
        for paragraph in document.paragraphs:
            result['paragraphs_processed'] += 1
            if process_paragraph(paragraph, patterns):
                result['paragraphs_changed'] += 1
                result['changes_made'] = True

        # Process tables
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        result['paragraphs_processed'] += 1
                        if process_paragraph(paragraph, patterns):
                            result['paragraphs_changed'] += 1
                            result['changes_made'] = True

        # Save document
        if output_path:
            result['output_path'] = output_path
        document.save(result['output_path'])
        result['success'] = True

    except Exception as e:
        result['error'] = str(e)

    return result