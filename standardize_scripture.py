#!/usr/bin/env python3
"""
standardize_scripture.py - Main script to process Word documents and standardize Bible references.
"""

import argparse
import os
import logging
from document_processing import process_document
from typing import List, Dict

def setup_logging(verbose: bool = False, log_file: str = 'scripture_standardization.log') -> None:
    """Set up logging to file and console."""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels

    # Clear any existing handlers
    logger.handlers = []

    # File handler
    try:
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except PermissionError as e:
        print(f"Warning: Cannot write to log file '{log_file}': {e}")
        print("Logging to console only.")
        logging.error(f"Failed to set up file logging: {e}")

    # Console handler (only if verbose)
    if verbose:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

def validate_file_path(file_path: str) -> bool:
    """Validate if the file path exists."""
    return os.path.isfile(file_path)

def validate_output_path(output_path: str) -> bool:
    """Validate if the output path is writable."""
    output_dir = os.path.dirname(output_path) or '.'
    return os.access(output_dir, os.W_OK)

def process_files(file_paths: List[str], output_dir: str = None, verbose: bool = False, create_backup: bool = True) -> Dict:
    """Process a list of Word documents to standardize Bible references."""
    results = {
        'total_files': len(file_paths),
        'successful': 0,
        'failed': 0,
        'files_with_changes': 0,
        'total_paragraphs_processed': 0,
        'total_paragraphs_changed': 0,
        'file_results': []
    }

    for file_path in file_paths:
        logging.info(f"Processing file: {file_path}")

        if not validate_file_path(file_path):
            logging.error(f"File not found: {file_path}")
            results['failed'] += 1
            results['file_results'].append({'file': file_path, 'success': False, 'error': 'File not found'})
            continue

        output_path = file_path
        if output_dir:
            output_filename = os.path.basename(file_path)
            output_path = os.path.join(output_dir, output_filename)

        if output_dir and not validate_output_path(output_path):
            logging.error(f"Output directory not writable: {output_dir}")
            results['failed'] += 1
            results['file_results'].append({'file': file_path, 'success': False, 'error': 'Output directory not writable'})
            continue

        result = process_document(file_path, output_path, create_backup)
        results['file_results'].append({
            'file': file_path,
            'success': result['success'],
            'changes_made': result['changes_made'],
            'paragraphs_processed': result['paragraphs_processed'],
            'paragraphs_changed': result['paragraphs_changed'],
            'backup_path': result['backup_path'],
            'output_path': result['output_path'],
            'error': result['error']
        })

        if result['success']:
            results['successful'] += 1
            if result['changes_made']:
                results['files_with_changes'] += 1
            results['total_paragraphs_processed'] += result['paragraphs_processed']
            results['total_paragraphs_changed'] += result['paragraphs_changed']
        else:
            results['failed'] += 1
            logging.error(f"Failed to process {file_path}: {result['error']}")

    return results

def print_summary(results: Dict) -> None:
    """Print a summary of the processing results."""
    print(f"\nProcessing {results['total_files']} document(s)...")
    print("\nSummary:")
    print(f"✓ Processed {results['total_files']} document(s)")
    print(f"✓ Successfully processed {results['successful']} document(s)")
    print(f"✓ Made changes to {results['total_paragraphs_changed']} out of {results['total_paragraphs_processed']} paragraphs")
    
    print("\nDetailed statistics:")
    print(f"  - Documents processed: {results['total_files']}")
    print(f"  - Documents with changes: {results['files_with_changes']}")
    print(f"  - Paragraphs processed: {results['total_paragraphs_processed']}")
    print(f"  - Paragraphs changed: {results['total_paragraphs_changed']}")
    if results['total_paragraphs_processed'] > 0:
        change_percentage = (results['total_paragraphs_changed'] / results['total_paragraphs_processed']) * 100
        print(f"  - Change percentage: {change_percentage:.2f}%")
    
    for result in results['file_results']:
        print(f"\nFile: {result['output_path']}")
        if result['success']:
            if result['backup_path']:
                print(f"  ✓ Backup created at: {result['backup_path']}")
            print(f"  ✓ Paragraphs changed: {result['paragraphs_changed']}/{result['paragraphs_processed']}")
        else:
            print(f"  ✗ Error: {result['error']}")
    
    print("\nCheck 'scripture_standardization.log' for detailed processing information.")

def main():
    """Main function to handle command-line arguments and process documents."""
    parser = argparse.ArgumentParser(description="Standardize Bible references in Word documents.")
    parser.add_argument('files', nargs='+', help="Word document(s) to process")
    parser.add_argument('-o', '--output-dir', help="Output directory for processed documents")
    parser.add_argument('--no-backup', action='store_false', dest='create_backup', help="Do not create backup files")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Set up logging
    log_file = os.path.join(os.getcwd(), 'scripture_standardization.log')
    setup_logging(args.verbose, log_file)
    
    # Validate output directory
    if args.output_dir and not os.path.exists(args.output_dir):
        try:
            os.makedirs(args.output_dir)
            logging.debug(f"Created output directory: {args.output_dir}")
        except OSError as e:
            logging.error(f"Failed to create output directory '{args.output_dir}': {e}")
            print(f"Error: Cannot create output directory '{args.output_dir}': {e}")
            return
    
    # Process files
    results = process_files(args.files, args.output_dir, args.verbose, args.create_backup)
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    main()
