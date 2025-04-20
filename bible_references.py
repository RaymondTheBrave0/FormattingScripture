"""
bible_references.py - Module for standardizing Bible references with corrected parsing and validation.
"""

import re
from typing import List, Tuple, Pattern
import logging

# Dictionary mapping Bible book abbreviations to standardized names
BIBLE_BOOKS = {
    'gen': 'Genesis', 'ge': 'Genesis', 'gn': 'Genesis', 'genesis': 'Genesis',
    'exod': 'Exodus', 'ex': 'Exodus', 'exo': 'Exodus', 'exodus': 'Exodus',
    'lev': 'Leviticus', 'le': 'Leviticus', 'lv': 'Leviticus', 'leviticus': 'Leviticus',
    'num': 'Numbers', 'nu': 'Numbers', 'nm': 'Numbers', 'numbers': 'Numbers',
    'deut': 'Deuteronomy', 'dt': 'Deuteronomy', 'de': 'Deuteronomy', 'deuteronomy': 'Deuteronomy',
    'josh': 'Joshua', 'jos': 'Joshua', 'jsh': 'Joshua', 'joshua': 'Joshua',
    'judg': 'Judges', 'jdg': 'Judges', 'jg': 'Judges', 'judges': 'Judges',
    'ruth': 'Ruth', 'rth': 'Ruth', 'ru': 'Ruth',
    '1 sam': '1 Samuel', '1sam': '1 Samuel', '1 sa': '1 Samuel', '1sa': '1 Samuel', '1 samuel': '1 Samuel',
    '2 sam': '2 Samuel', '2sam': '2 Samuel', '2 sa': '2 Samuel', '2sa': '2 Samuel', '2 samuel': '2 Samuel',
    '1 kgs': '1 Kings', '1kgs': '1 Kings', '1 ki': '1 Kings', '1ki': '1 Kings', '1 kings': '1 Kings',
    '2 kgs': '2 Kings', '2kgs': '2 Kings', '2 ki': '2 Kings', '2ki': '2 Kings', '2 kings': '2 Kings',
    '1 chr': '1 Chronicles', '1chr': '1 Chronicles', '1 ch': '1 Chronicles', '1ch': '1 Chronicles', '1 chronicles': '1 Chronicles',
    '2 chr': '2 Chronicles', '2chr': '2 Chronicles', '2 ch': '2 Chronicles', '2ch': '2 Chronicles', '2 chronicles': '2 Chronicles',
    'ezra': 'Ezra', 'ezr': 'Ezra', 'ez': 'Ezra',
    'neh': 'Nehemiah', 'ne': 'Nehemiah', 'nehemiah': 'Nehemiah',
    'esth': 'Esther', 'est': 'Esther', 'es': 'Esther', 'esther': 'Esther',
    'job': 'Job', 'jb': 'Job',
    'ps': 'Psalm', 'psa': 'Psalm', 'psm': 'Psalm', 'psalm': 'Psalm', 'Ps.': 'Psalm',
    'pss': 'Psalms', 'psalms': 'Psalms',
    'prov': 'Proverbs', 'pro': 'Proverbs', 'pr': 'Proverbs', 'prv': 'Proverbs', 'proverbs': 'Proverbs',
    'eccl': 'Ecclesiastes', 'ecc': 'Ecclesiastes', 'ec': 'Ecclesiastes', 'ecclesiastes': 'Ecclesiastes',
    'song': 'Song of Solomon', 'sos': 'Song of Solomon', 'ss': 'Song of Solomon', 'song of solomon': 'Song of Solomon',
    'Isa.': 'Isaiah', 'is': 'Isaiah', 'isaiah': 'Isaiah',
    'jer': 'Jeremiah', 'je': 'Jeremiah', 'jeremiah': 'Jeremiah',
    'lam': 'Lamentations', 'la': 'Lamentations', 'lamentations': 'Lamentations',
    'ezek': 'Ezekiel', 'eze': 'Ezekiel', 'ezk': 'Ezekiel', 'ezekiel': 'Ezekiel',
    'dan': 'Daniel', 'da': 'Daniel', 'dn': 'Daniel', 'daniel': 'Daniel',
    'hos': 'Hosea', 'ho': 'Hosea', 'hosea': 'Hosea',
    'joel': 'Joel', 'jl': 'Joel',
    'amos': 'Amos', 'am': 'Amos',
    'obad': 'Obadiah', 'ob': 'Obadiah', 'obadiah': 'Obadiah',
    'jonah': 'Jonah', 'jon': 'Jonah',
    'mic': 'Micah', 'mi': 'Micah', 'micah': 'Micah',
    'Nah.': 'Nahum', 'na': 'Nahum', 'nahum': 'Nahum',
    'Hab.': 'Habakkuk', 'hb': 'Habakkuk', 'habakkuk': 'Habakkuk',
    'Zeph.': 'Zephaniah', 'zep': 'Zephaniah', 'zp': 'Zephaniah', 'zephaniah': 'Zephaniah',
    'Hag.': 'Haggai', 'hg': 'Haggai', 'haggai': 'Haggai',
    'Zech.': 'Zechariah', 'zec': 'Zechariah', 'zc': 'Zechariah', 'zechariah': 'Zechariah',
    'Mal.': 'Malachi', 'Mal': 'Malachi', 'malachi': 'Malachi',
    'Matt.': 'Matthew', 'Matt': 'Matthew', 'mat': 'Matthew', 'mt': 'Matthew',
    'mark': 'Mark', 'Mk.': 'Mark', 'Mar.': 'Mark', 'mk': 'Mark', 
    'luke': 'Luke', 'Lk.': 'Luke', 'lk': 'Luke',
    'john': 'John', 'jn': 'John', 'jhn': 'John',
    'acts': 'Acts', 'ac': 'Acts', 'act': 'Acts',
    'rom': 'Romans', 'ro': 'Romans', 'rm': 'Romans', 'romans': 'Romans', 'Rom.': 'Romans',
    '1 Cor.': '1 Corinthians', '1cor': '1 Corinthians', '1 co': '1 Corinthians', '1co': '1 Corinthians', '1 corinthians': '1 Corinthians',
    '2 Cor.': '2 Corinthians', '2cor': '2 Corinthians', '2 co': '2 Corinthians', '2co': '2 Corinthians', '2 corinthians': '2 Corinthians',
    'gal': 'Galatians', 'Gal.': 'Galatians', 'galatians': 'Galatians', 'gal.': 'Galatians',
    'Eph.': 'Ephesians', 'ep': 'Ephesians', 'ephesians': 'Ephesians', 'eph.': 'Ephesians',
    'phil': 'Philippians', 'php': 'Philippians', 'Php.': 'Philippians', 'philippians': 'Philippians',
    'Col.': 'Colossians', 'co': 'Colossians', 'col.': 'Colossians', 'colossians': 'Colossians',
    '1 thess': '1 Thessalonians', '1thess': '1 Thessalonians', '1 th': '1 Thessalonians', '1th': '1 Thessalonians', '1 thessalonians': '1 Thessalonians',
    '2 thess': '2 Thessalonians', '2thess': '2 Thessalonians', '2 th': '2 Thessalonians', '2th': '2 Thessalonians', '2 thessalonians': '2 Thessalonians',
    '1 Tim.': '1 Timothy', '1tim.': '1 Timothy', '1 ti': '1 Timothy', '1ti': '1 Timothy', '1 timothy': '1 Timothy',
    '2 Tim.': '2 Timothy', '2tim.': '2 Timothy', '2 ti': '2 Timothy', '2ti': '2 Timothy', '2 timothy': '2 Timothy',
    'titus': 'Titus', 'tit': 'Titus', 'ti': 'Titus',
    'phlm': 'Philemon', 'phm': 'Philemon', 'pm': 'Philemon', 'philemon': 'Philemon',
    'heb': 'Hebrews', 'he': 'Hebrews', 'hebrews': 'Hebrews',
    'Jas.': 'James', 'jm': 'James', 'ja': 'James', 'james': 'James',
    '1 pet': '1 Peter', '1pet': '1 Peter', '1 pe': '1 Peter', '1pe': '1 Peter', '1 peter': '1 Peter',
    '2 pet': '2 Peter', '2pet': '2 Peter', '2 pe': '2 Peter', '2pe': '2 Peter', '2 peter': '2 Peter',
    '1 john': '1 John', '1john': '1 John', '1 jn': '1 John', '1jn': '1 John',
    '2 john': '2 John', '2john': '2 John', '2 jn': '2 John', '2jn': '2 John',
    '3 john': '3 John', '3john': '3 John', '3 jn': '3 John', '3jn': '3 John',
    'jude': 'Jude', 'jud': 'Jude', 'jd': 'Jude',
    'rev': 'Revelation', 're': 'Revelation', 'rv': 'Revelation', 'revelation': 'Revelation'
}

# Compile book pattern
BOOK_PATTERN = r'\b(' + '|'.join(map(re.escape, BIBLE_BOOKS.keys())) + r')\b'

# Regex patterns for different reference formats
PATTERNS = [
    # Parenthesized references: "(mt 4:23, mk 1:14-15)"
    (re.compile(r'\(([^)]+)\)', re.IGNORECASE),
     lambda m: process_parenthesized_references(m)),

    # Period-separated: "1 Cor. 13.4-7"
    (re.compile(rf'{BOOK_PATTERN}\s*(\d+)\s*\.\s*(\d+)(?:-(\d+))?([*#]?)', re.IGNORECASE),
     lambda m: standardize_reference(m)),

    # Standard or colon-separated: "gal: 3:27", "Acts 2:12-16"
    (re.compile(rf'{BOOK_PATTERN}\s*(\d+)\s*:\s*(\d+)(?:-(\d+))?([*#]?)', re.IGNORECASE),
     lambda m: standardize_reference(m)),

    # Space-separated: "Matt 5 3-10"
    (re.compile(rf'{BOOK_PATTERN}\s*(\d+)\s+(\d+)(?:-(\d+))?([*#]?)', re.IGNORECASE),
     lambda m: standardize_reference(m)),

    # Chapter-verse format: "John chapter 3 verse 16"
    (re.compile(rf'{BOOK_PATTERN}\s*chapter\s*(\d+)\s*verse[s]?\s*(\d+)(?:-(\d+))?([*#]?)', re.IGNORECASE),
     lambda m: standardize_reference(m)),

    # Standalone chapter: "Psalm 23"
    (re.compile(rf'{BOOK_PATTERN}\s*(\d+)([*#]?)(?!\s*[:\.-]\d+)', re.IGNORECASE),
     lambda m: standardize_standalone_chapter(m)),
]

def preprocess_text(text: str) -> str:
    """Preprocess text to normalize formatting."""
    # Normalize spaces, preserve reference structure
    text = re.sub(r'\s+', ' ', text.strip())
    # Normalize multiple colons to one, preserve periods
    text = re.sub(r':+', ':', text)
    return text

def standardize_reference(match) -> str:
    """Standardize a Bible reference to 'Book Chapter:Verse' format."""
    original_text = match.group(0)
    book_abbr = match.group(1).lower().strip()
    book_name = BIBLE_BOOKS.get(book_abbr, book_abbr.title())
    
    # Extract groups safely
    chapter = match.group(2).strip() if match.group(2) else None
    verse_start = match.group(3).strip() if len(match.groups()) > 2 and match.group(3) else None
    verse_end = match.group(4).strip() if len(match.groups()) > 3 and match.group(4) else None
    special_char = match.group(5).strip() if len(match.groups()) > 4 and match.group(5) else ''
    
    # Fallback for special characters
    if not special_char and ('*' in original_text or '#' in original_text):
        special_char = '*' if '*' in original_text else '#'
    
    # Validate inputs
    if not chapter or not chapter.isdigit():
        logging.warning(f"Invalid chapter in reference: {original_text} (value: {chapter})")
        return original_text
    if not verse_start or not verse_start.isdigit():
        logging.warning(f"Invalid verse_start in reference: {original_text} (value: {verse_start})")
        return original_text
    if verse_end and not verse_end.isdigit():
        logging.warning(f"Invalid verse_end in reference: {original_text} (value: {verse_end})")
        return original_text
    
    # Convert to integers
    try:
        chapter_int = int(chapter)
        verse_start_int = int(verse_start)
        verse_end_int = int(verse_end) if verse_end else None
    except ValueError as e:
        logging.warning(f"Number conversion failed in reference: {original_text} (error: {str(e)})")
        return original_text
    
    # Special case for Matthew Beatitudes (verses 3-10)
    if book_name == 'Matthew' and chapter_int == 5 and verse_start_int in range(3, 11):
        chapter = '5'
        if verse_end_int and verse_end_int > 11:
            verse_end = '10'
    
    result = f"{book_name} {chapter}:{verse_start}"
    if verse_end:
        result += f"-{verse_end}"
    if special_char:
        result += special_char
    
    logging.debug(f"Standardized reference: {original_text} -> {result}")
    return result

def standardize_standalone_chapter(match) -> str:
    """Standardize standalone chapter references to 'Book Chapter:1' format."""
    original_text = match.group(0)
    book_abbr = match.group(1).lower().strip()
    book_name = BIBLE_BOOKS.get(book_abbr, book_abbr.title())
    chapter = match.group(2).strip() if match.group(2) else None
    special_char = match.group(3).strip() if len(match.groups()) > 2 and match.group(3) else ''
    
    # Validate chapter
    if not chapter or not chapter.isdigit():
        logging.warning(f"Invalid chapter in standalone reference: {original_text} (value: {chapter})")
        return original_text
    
    try:
        chapter_int = int(chapter)
    except ValueError as e:
        logging.warning(f"Number conversion failed in standalone reference: {original_text} (error: {str(e)})")
        return original_text
    
    result = f"{book_name} {chapter}:1"
    if special_char:
        result += special_char
    
    logging.debug(f"Standardized standalone chapter: {original_text} -> {result}")
    return result

def process_parenthesized_references(match) -> str:
    """Process a group of comma-separated references within parentheses."""
    content = preprocess_text(match.group(1))
    logging.debug(f"Processing parenthesized references: {content}")
    
    # Split on commas
    parts = [part.strip() for part in content.split(',') if part.strip()]
    result = []
    
    for ref in parts:
        matched = False
        for pattern, replacement_func in PATTERNS[1:]:  # Skip parenthesized pattern
            match = pattern.fullmatch(ref)
            if match:
                std_ref = replacement_func(match)
                result.append(std_ref)
                matched = True
                break
        if not matched:
            logging.warning(f"Could not parse parenthesized reference: {ref}")
            result.append(ref)
    
    standardized = ', '.join(result)
    return f"({standardized})"

def get_patterns() -> List[Tuple[Pattern, str]]:
    """Return pre-compiled regex patterns."""
    return PATTERNS

def standardize_text(text: str) -> str:
    """
    Apply Bible reference standardization to a text string.
    """
    transformed_text = preprocess_text(text)
    patterns = get_patterns()
    matched = False
    
    # Process patterns in reverse order to prioritize specific patterns
    for pattern, replacement_func in reversed(patterns):
        matches = list(pattern.finditer(transformed_text))
        if matches:
            matched = True
            # Process matches in reverse to preserve text order
            for match in reversed(matches):
                match_text = match.group(0)
                try:
                    replacement = replacement_func(match)
                    transformed_text = transformed_text[:match.start()] + replacement + transformed_text[match.end():]
                except Exception as e:
                    logging.error(f"Error standardizing reference '{match_text}': {str(e)}")
                    continue
    
    if not matched:
        logging.debug(f"No Bible reference patterns matched in text: {transformed_text}")
    
    return transformed_text

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_text = " ".join(sys.argv[1:])
    else:
        test_text = "See gal: 3:27* and 1 Cor. 13.4-7"
    
    print(f"Original text: {test_text}")
    standardized = standardize_text(test_text)
    print(f"Standardized text: {standardized}")
