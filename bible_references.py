"""
bible_references.py - Module containing Bible reference data and standardization logic.
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
    'ps': 'Psalm', 'psa': 'Psalm', 'psm': 'Psalm', 'psalm': 'Psalm', 'ps.': 'Psalm',
    'pss': 'Psalms', 'psalms': 'Psalms',
    'prov': 'Proverbs', 'pro': 'Proverbs', 'pr': 'Proverbs', 'prv': 'Proverbs', 'proverbs': 'Proverbs',
    'eccl': 'Ecclesiastes', 'ecc': 'Ecclesiastes', 'ec': 'Ecclesiastes', 'ecclesiastes': 'Ecclesiastes',
    'song': 'Song of Solomon', 'sos': 'Song of Solomon', 'ss': 'Song of Solomon', 'song of solomon': 'Song of Solomon',
    'isa': 'Isaiah', 'is': 'Isaiah', 'isaiah': 'Isaiah',
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
    'nah': 'Nahum', 'na': 'Nahum', 'nahum': 'Nahum',
    'hab': 'Habakkuk', 'hb': 'Habakkuk', 'habakkuk': 'Habakkuk',
    'zeph': 'Zephaniah', 'zep': 'Zephaniah', 'zp': 'Zephaniah', 'zephaniah': 'Zephaniah',
    'hag': 'Haggai', 'hg': 'Haggai', 'haggai': 'Haggai',
    'zech': 'Zechariah', 'zec': 'Zechariah', 'zc': 'Zechariah', 'zechariah': 'Zechariah',
    'mal': 'Malachi', 'ml': 'Malachi', 'malachi': 'Malachi',
    'matt': 'Matthew', 'mt': 'Matthew', 'mat': 'Matthew', 'matthew': 'Matthew',
    'mark': 'Mark', 'mk': 'Mark', 'mr': 'Mark',
    'luke': 'Luke', 'lk': 'Luke', 'lu': 'Luke',
    'john': 'John', 'jn': 'John', 'jhn': 'John',
    'acts': 'Acts', 'ac': 'Acts', 'act': 'Acts',
    'rom': 'Romans', 'ro': 'Romans', 'rm': 'Romans', 'romans': 'Romans', 'rom.': 'Romans',
    '1 cor': '1 Corinthians', '1cor': '1 Corinthians', '1 co': '1 Corinthians', '1co': '1 Corinthians', '1 corinthians': '1 Corinthians',
    '2 cor': '2 Corinthians', '2cor': '2 Corinthians', '2 co': '2 Corinthians', '2co': '2 Corinthians', '2 corinthians': '2 Corinthians',
    'gal': 'Galatians', 'ga': 'Galatians', 'galatians': 'Galatians','gal.': 'Galatians',
    'eph': 'Ephesians', 'ep': 'Ephesians', 'ephesians': 'Ephesians', 'eph.': 'Ephesians',
    'phil': 'Philippians', 'php': 'Philippians', 'pp': 'Philippians', 'philippians': 'Philippians',
    'col': 'Colossians', 'co': 'Colossians', 'col.': 'Colossians', 'colossians': 'Colossians',
    '1 thess': '1 Thessalonians', '1thess': '1 Thessalonians', '1 th': '1 Thessalonians', '1th': '1 Thessalonians', '1 thessalonians': '1 Thessalonians',
    '2 thess': '2 Thessalonians', '2thess': '2 Thessalonians', '2 th': '2 Thessalonians', '2th': '2 Thessalonians', '2 thessalonians': '2 Thessalonians',
    '1 tim': '1 Timothy', '1tim.': '1 Timothy', '1 ti': '1 Timothy', '1ti': '1 Timothy', '1 timothy': '1 Timothy',
    '2 tim': '2 Timothy', '2tim.': '2 Timothy', '2 ti': '2 Timothy', '2ti': '2 Timothy', '2 timothy': '2 Timothy',
    'titus': 'Titus', 'tit': 'Titus', 'ti': 'Titus',
    'phlm': 'Philemon', 'phm': 'Philemon', 'pm': 'Philemon', 'philemon': 'Philemon',
    'heb': 'Hebrews', 'he': 'Hebrews', 'hebrews': 'Hebrews',
    'jas': 'James', 'jm': 'James', 'ja': 'James', 'james': 'James',
    '1 pet': '1 Peter', '1pet': '1 Peter', '1 pe': '1 Peter', '1pe': '1 Peter', '1 peter': '1 Peter',
    '2 pet': '2 Peter', '2pet': '2 Peter', '2 pe': '2 Peter', '2pe': '2 Peter', '2 peter': '2 Peter',
    '1 john': '1 John', '1john': '1 John', '1 jn': '1 John', '1jn': '1 John',
    '2 john': '2 John', '2john': '2 John', '2 jn': '2 John', '2jn': '2 John',
    '3 john': '3 John', '3john': '3 John', '3 jn': '3 John', '3jn': '3 John',
    'jude': 'Jude', 'jud': 'Jude', 'jd': 'Jude',
    'rev': 'Revelation', 're': 'Revelation', 'rv': 'Revelation', 'revelation': 'Revelation'
}

# Compile book pattern once - allow for various punctuation after book abbreviation
BOOK_PATTERN = r'\b(' + '|'.join(map(re.escape, BIBLE_BOOKS.keys())) + r')([\.\s,;]*)?\b'

# Pre-compile regex patterns for performance
PATTERNS = [
    # Parenthesized comma-separated references: "(Gal, 3:27*, Ephesians 4:24*, Col. 3:10*)"
    (re.compile(r'\(([^)]+)\)', re.IGNORECASE),
     lambda m: process_parenthesized_references(m)),

    # Period format: "Gal. 3:27*" or "1 Cor. 13.4-7" (match individual references)
    (re.compile(rf'{BOOK_PATTERN}\s*(\d+)\.(\d+)(?:-(\d+))?([*#]?)', re.IGNORECASE),
     lambda m: standardize_period_format(m)),

    # Format: "John 3:16" or "John 3:16-17" (with optional special char)
    (re.compile(rf'{BOOK_PATTERN}\s*(\d+):(\d+)(?:-(\d+))?([*#]?)', re.IGNORECASE),
     lambda m: standardize_reference(m, standardize_verse=False)),

    # Chapter-verse format: "John chapter 3 verse 16"
    (re.compile(rf'{BOOK_PATTERN}\s*chapter\s*(\d+)\s*verse\s*(\d+)(?:-(\d+))?([*#]?)', re.IGNORECASE),
     lambda m: standardize_reference(m)),

    # Space format: "John 3 16"
    (re.compile(rf'{BOOK_PATTERN}\s*(\d+)\s+(\d+)(?:-(\d+))?([*#]?)', re.IGNORECASE),
     lambda m: standardize_reference(m)),

    # Standalone chapter: "Psalm 23" - must not have colon or period followed by digits
    # Negative lookahead to ensure the match isn't part of an existing chapter:verse reference
    (re.compile(rf'{BOOK_PATTERN}\s+(\d+)(?![:\.]\d+|\s+\d+)([*#]?)(?!\s*\d+[-:]\d+)', re.IGNORECASE),
     lambda m: standardize_standalone_chapter(m)),

    # Fix invalid range: "Acts 2:12:16" to "Acts 2:12-16"
    (re.compile(rf'{BOOK_PATTERN}\s*(\d+):(\d+):(\d+)([*#]?)', re.IGNORECASE),
     lambda m: standardize_invalid_range(m)),
]
def standardize_standalone_chapter(match) -> str:
    """Standardize standalone chapter references to 'Book Chapter:1' format."""
    original_text = match.group(0)
    surrounding_text = original_text
    
    # Make sure this is not a chapter:verse reference
    if ':' in original_text or '.' in original_text:
        logging.debug(f"Skipping standalone chapter formatting for: {original_text}")
        return original_text
        
    # Check if this is part of a larger reference
    # that already has a chapter:verse format somewhere
    if re.search(r'\d+[:\.]\d+', surrounding_text):
        return original_text
    
    book_abbr = match.group(1).lower().rstrip('.')
    book_name = BIBLE_BOOKS.get(book_abbr, book_abbr.title())
    chapter = match.group(2)
    special_char = match.group(3) if len(match.groups()) >= 3 and match.group(3) else ''
    
    # Ensure we're not doubling special characters
    if special_char and (original_text.endswith(special_char)):
        result = f"{book_name} {chapter}:1"
    else:
        result = f"{book_name} {chapter}:1{special_char}"
        
    return result

def standardize_reference(match, separator: str = ':', is_period_format: bool = False, standardize_verse: bool = True) -> str:
    """Standardize Bible reference to 'Book Chapter:Verse' format."""
    book_abbr = match.group(1).lower()
    # Strip trailing characters that might have been captured
    book_abbr = re.sub(r'[\.,\s;]+$', '', book_abbr)
    book_name = BIBLE_BOOKS.get(book_abbr, book_abbr.title())
    chapter = match.group(2).strip()
    verse_start = match.group(3).strip() if match.group(3) else "1"
    
    # Handle verse end and special characters
    verse_end = None
    special_char = ""
    
    # Extract verse_end and special_char from groups
    if len(match.groups()) >= 4 and match.group(4):
        if match.group(4) in ['*', '#']:
            special_char = match.group(4)
        else:
            verse_end = match.group(4).strip()
    
    # Check for special character in the last group
    if len(match.groups()) >= 5 and match.group(5):
        special_char = match.group(5)

    # Check for special character in original text if not found yet
    original_text = match.group(0)
    if not special_char and '*' in original_text:
        special_char = '*'
    elif not special_char and '#' in original_text:
        special_char = '#'
    
    # Build the standardized reference - ensure proper formatting
    # Build proper reference based on standardization needs
    if standardize_verse:
        # Format with standardized chapter:verse
        reference = f"{book_name} {chapter}:{verse_start}"
        if verse_end and verse_end not in ['*', '#']:
            reference += f"-{verse_end}"
    else:
        # Keep original exact formatting from match text
        # Just replace the book name part
        book_part = re.match(rf'{BOOK_PATTERN}', original_text, re.IGNORECASE).group(0)
        remaining = original_text[len(book_part):].lstrip()
        reference = f"{book_name} {remaining}"
    
    # Ensure we're not adding duplicate special characters
    if special_char and not original_text.endswith(special_char):
        reference += special_char
    elif special_char and original_text.endswith(special_char):
        # Make sure the reference doesn't already end with the special char
        if not reference.endswith(special_char):
            reference += special_char
    logging.debug(f"Standardized reference: {match.group(0)} -> {reference}")
    return reference

def standardize_period_format(match) -> str:
    """Standardize period-separated verse format like '1 Cor. 13.4-7' to '1 Corinthians 13:4-7'."""
    book_abbr = match.group(1).lower()
    # Strip trailing characters that might have been captured
    book_abbr = re.sub(r'[\.,\s;]+$', '', book_abbr)
    book_name = BIBLE_BOOKS.get(book_abbr, book_abbr.title())
    
    # Get the original text and extract components
    original_text = match.group(0)
    
    # Extract the chapter and verse parts from the match groups
    chapter = match.group(2).strip()
    verse_start = match.group(3).strip() if match.group(3) else "1"
    verse_end = match.group(4) if len(match.groups()) >= 4 and match.group(4) else None
    
    # Extract special character
    special_char = ''
    if len(match.groups()) >= 5 and match.group(5):
        special_char = match.group(5)
    elif '*' in original_text:
        special_char = '*'
    elif '#' in original_text:
        special_char = '#'
    
    # Build the standardized reference correctly
    # Find where the book part ends
    book_part = re.match(rf'{BOOK_PATTERN}', original_text, re.IGNORECASE).group(0)
    
    # Extract the precise formatting of the verse reference
    number_part = original_text[len(book_part):].strip()
    
    # Replace the first period with a colon but preserve the rest
    if '.' in number_part:
        chapter_verse_parts = number_part.split('.', 1)
        number_part = f"{chapter_verse_parts[0]}:{chapter_verse_parts[1]}"
    
    # Final standardized reference
    reference = f"{book_name} {number_part}"
    
    # Only add special char if it's not already there
    if special_char and not reference.endswith(special_char):
        reference += special_char
    
    logging.debug(f"Standardized period format: {match.group(0)} -> {reference}")
    return reference

def standardize_invalid_range(match) -> str:
    """Standardize invalid verse range like 'Acts 2:12:16' to 'Acts 2:12-16'."""
    book_abbr = match.group(1).lower()
    # Strip trailing characters that might have been captured
    book_abbr = re.sub(r'[\.,\s;]+$', '', book_abbr)
    book_name = BIBLE_BOOKS.get(book_abbr, book_abbr.title())
    chapter = match.group(2)
    verse_start = match.group(3)
    verse_end = match.group(4) if len(match.groups()) >= 4 and match.group(4) else None
    special_char = match.group(5) if len(match.groups()) >= 5 and match.group(5) else ''
    result = f"{book_name} {chapter}:{verse_start}-{verse_end}{special_char}"
    logging.debug(f"Standardized invalid range: {match.group(0)} -> {result}")
    return result

def parse_reference_components(ref_str):
    """Parse a reference string into its components: book, chapter, verse, etc."""
    # Extract the book name
    book_match = re.search(r'^([A-Za-z0-9\s\.]+?)[\s\.,]*(?=\d|$)', ref_str, re.IGNORECASE)
    if not book_match:
        return None
    
    book_abbr = book_match.group(1).strip().lower()
    book_abbr = re.sub(r'[\.,\s;]+$', '', book_abbr)
    
    # Try to find chapter:verse pattern
    cv_match = re.search(r'(\d+):(\d+)(?:-(\d+))?([*#]?)', ref_str, re.IGNORECASE)
    if cv_match:
        chapter = cv_match.group(1)
        verse_start = cv_match.group(2)
        verse_end = cv_match.group(3) if cv_match.group(3) else None
        special_char = cv_match.group(4) if cv_match.group(4) else ''
        return {
            'book_abbr': book_abbr,
            'chapter': chapter,
            'verse_start': verse_start,
            'verse_end': verse_end,
            'special_char': special_char
        }
    
    # Try to find chapter.verse pattern (with period separator)
    cv_match = re.search(r'(\d+)\.(\d+)(?:-(\d+))?([*#]?)', ref_str, re.IGNORECASE)
    if cv_match:
        chapter = cv_match.group(1)
        verse_start = cv_match.group(2)
        verse_end = cv_match.group(3) if cv_match.group(3) else None
        special_char = cv_match.group(4) if cv_match.group(4) else ''
        return {
            'book_abbr': book_abbr,
            'chapter': chapter,
            'verse_start': verse_start,
            'verse_end': verse_end,
            'special_char': special_char
        }
    
    # Try to find just a chapter
    c_match = re.search(r'(\d+)([*#]?)', ref_str)
    if c_match:
        chapter = c_match.group(1)
        special_char = c_match.group(2) if c_match.group(2) else ''
        return {
            'book_abbr': book_abbr,
            'chapter': chapter,
            'verse_start': '1',  # Default to verse 1
            'verse_end': None,
            'special_char': special_char
        }
    
    return None

def standardize_book_name(book_abbr):
    """Standardize a book abbreviation to its full name."""
    # Strip trailing punctuation
    book_abbr = re.sub(r'[\.,\s;]+$', '', book_abbr.lower())
    
    # Check if the abbreviation is in our dictionary
    if book_abbr in BIBLE_BOOKS:
        return BIBLE_BOOKS[book_abbr]
    
    # Handle some common abbreviations that might not be in the dictionary
    if book_abbr in ['gal', 'gal.']:
        return 'Galatians'
    elif book_abbr in ['col', 'col.']:
        return 'Colossians'
    elif book_abbr in ['eph', 'eph.']:
        return 'Ephesians'
    elif book_abbr in ['cor', 'cor.']:
        return '1 Corinthians'  # Default to 1 Corinthians if not specified
    
    # If we can't match it, just capitalize the first letter
    return book_abbr.title()

def process_parenthesized_references(match) -> str:
    """Process a group of comma-separated references within parentheses."""
    content = match.group(1)
    logging.debug(f"Processing parenthesized references: {content}")
    
    # Split the content by commas, but handle special case with comma after book abbreviation
    content_fixed = re.sub(r'([A-Za-z]+),\s*(\d+)', r'\1 \2', content)
    parts = re.split(r',\s*', content_fixed)
    
    references = [part.strip() for part in parts if part.strip()]
    result = []
    last_book = None
    
    for ref in references:
        # Try to parse the reference using the helper function
        components = parse_reference_components(ref)
        
        if components:
            book_abbr = components['book_abbr']
            book_name = standardize_book_name(book_abbr)
            
            if book_name:
                last_book = book_name
            elif last_book:
                book_name = last_book
            else:
                logging.warning(f"Could not determine book name for: {ref}")
                result.append(ref)  # Keep as is
                continue
            
            chapter = components['chapter']
            verse_start = components['verse_start']
            verse_end = components['verse_end']
            special_char = components['special_char']
            
            # Check for special character in the original text if not found yet
            if not special_char and '*' in ref:
                special_char = '*'
            elif not special_char and '#' in ref:
                special_char = '#'
            
            # Create the standardized reference
            std_ref = f"{book_name} {chapter}:{verse_start}"
            if verse_end and verse_end not in ['*', '#']:
                std_ref += f"-{verse_end}"
            std_ref += special_char
            
            # Add to result list
            result.append(std_ref)
        else:
            # Try one more attempt to extract information
            book_match = re.search(r'([A-Za-z0-9\s\.]+)(?:,?\s*(\d+))?', ref, re.IGNORECASE)
            if book_match and book_match.group(2):
                # Book and numbers found
                book_abbr = book_match.group(1).strip()
                std_book = standardize_book_name(book_abbr)
                
                # Check if there's a chapter:verse pattern
                cv_match = re.search(r'(\d+):(\d+)', ref)
                if cv_match:
                    chapter = cv_match.group(1)
                    verse = cv_match.group(2)
                else:
                    # Just a chapter number
                    chapter = book_match.group(2)
                    verse = '1'  # Default to verse 1
                
                # Extract any special character (* or #)
                special_char = ''
                if '*' in ref:
                    special_char = '*'
                elif '#' in ref:
                    special_char = '#'
                
                std_ref = f"{std_book} {chapter}:{verse}{special_char}"
                result.append(std_ref)
                logging.info(f"Non-standard reference '{ref}' converted to '{std_ref}'")
            else:
                # Keep original if no pattern matched at all
                result.append(ref)
                logging.warning(f"Could not parse reference: {ref}")
    
    standardized = ', '.join(result)
    return f"({standardized})"

def get_patterns() -> List[Tuple[Pattern, str]]:
    """Return pre-compiled regex patterns."""
    return PATTERNS

def standardize_text(text: str) -> str:
    """
    Apply Bible reference standardization to a text string.
    
    This function takes a text string that may contain Bible references
    and returns a version with all references standardized.
    
    Args:
        text (str): The input text containing Bible references.
        
    Returns:
        str: The text with standardized Bible references.
    
    Example:
        >>> standardize_text("See Gal. 3:27* and 1 Cor. 13.4-7")
        "See Galatians 3:27* and 1 Corinthians 13:4-7"
    """
    # Apply each pattern and transform the text
    transformed_text = text
    patterns = get_patterns()
    
    for pattern, replacement_func in patterns:
        # Look for matches
        matches = list(pattern.finditer(transformed_text))
        if matches:
            # Process each match
            for match in matches:
                match_text = match.group(0)
                # Apply the replacement function
                replacement = pattern.sub(replacement_func, match_text)
                # Update the text with the replacement
                transformed_text = transformed_text.replace(match_text, replacement)
    
    return transformed_text

if __name__ == "__main__":
    # Simple example usage when run directly
    import sys
    
    if len(sys.argv) > 1:
        # Use the text provided as command line argument
        test_text = " ".join(sys.argv[1:])
    else:
        # Use a default example
        test_text = "See Gal. 3:27* and 1 Cor. 13.4-7"
    
    print(f"Original text: {test_text}")
    standardized = standardize_text(test_text)
    print(f"Standardized text: {standardized}")
