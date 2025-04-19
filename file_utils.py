"""
file_utils.py - Module for file-related utilities.
"""

import os
import shutil
from datetime import datetime
from typing import List, Tuple

def create_backup(file_path: str) -> Tuple[bool, str]:
    """Create a backup of the original file."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename, extension = os.path.splitext(file_path)
        backup_path = f"{filename}_backup_{timestamp}{extension}"
        shutil.copy2(file_path, backup_path)
        return True, backup_path
    except Exception as e:
        return False, str(e)

def get_docx_files(directory: str) -> List[str]:
    """Get all .docx files in a directory."""
    docx_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.docx') and not file.startswith('~$'):
                docx_files.append(os.path.join(root, file))
    return docx_files