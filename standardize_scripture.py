#!/usr/bin/env python3
"""
standardize_scripture.py - Main script to standardize Bible references in Word documents.

This script processes Word documents in a directory to standardize Bible references
to the format "Book Chapter:Verse" (e.g., "John 3:16"). It supports batch processing,
creates backups, and includes proper error handling.

Dependencies:
    - python-docx: pip install python-docx
    - Standard libraries: re, os, sys, shutil, datetime, argparse, multiprocessing, logging
"""

import os
import sys
import argparse
import logging
from typing import Dict
from multiprocessing import Pool
from document_processing import process_document
from file_utils import get_docx_files

# Configure logging to both file and console
try:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scripture_standardization.log', mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )
except Exception as e:
    print(f"✗ Failed to initialize logging: {str(e)}")
    sys.exit(1)


def process_file(args_tuple: tuple) -> Dict:
    """Process a single document with given arguments."""
    file_path, output_dir = args_tuple
    logging.info(f"Starting to process file: {file_path}")
    try:
        output_path = os.path.join(output_dir, os.path.basename(
            file_path)) if output_dir else None
        result = process_document(file_path, output_path)
        logging.info(f"Finished processing file: {file_path}")
        return result
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {str(e)}")
        return {'success': False, 'error': str(e), 'output_path': file_path}


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Standardize Bible references to 'Book Chapter:Verse' format in Word documents",
        epilog="""Example: python standardize_scripture.py ./docs -o ./output
        
Note: Standalone chapter references (like 'Psalm 23') will be converted to 'Psalm 23:1'"""
    )

    parser.add_argument(
        "input_path",
        help="Path to a Word document or directory containing Word documents"
    )

    parser.add_argument(
        "-o", "--output",
        help="Directory where processed documents should be saved (if not specified, overwrites originals)"
    )

    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backups of original documents"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Display detailed processing information"
    )

    parser.add_argument(
        "-p", "--processes",
        type=int,
        default=os.cpu_count(),
        help="Number of processes to use for parallel processing"
    )

    args = parser.parse_args()
   
    # Validate input path
    if not os.path.exists(args.input_path):
        print(f"✗ Error: Path not found: {args.input_path}")
        logging.error(f"Path not found: {args.input_path}")
        sys.exit(1)

    # Create output directory if specified
    if args.output:
        try:
            os.makedirs(args.output, exist_ok=True)
        except Exception as e:
            print(f"✗ Error creating output directory: {str(e)}")
            logging.error(f"Error creating output directory: {str(e)}")
            sys.exit(1)

    # Get list of files to process
    try:
        if os.path.isfile(args.input_path):
            files = [args.input_path]
        else:
            files = get_docx_files(args.input_path)
    except Exception as e:
        print(f"✗ Error finding files: {str(e)}")
        logging.error(f"Error finding files: {str(e)}")
        sys.exit(1)

    if not files:
        print("✗ Error: No .docx files found in the specified path")
        logging.error("No .docx files found in the specified path")
        sys.exit(1)

    print(f"Processing {len(files)} document(s)...")
    logging.info(f"Processing {len(files)} document(s)")

    # Prepare arguments for multiprocessing
    process_args = [(f, args.output, not args.no_backup) for f in files]

    # Process files in parallel
    try:
        with Pool(processes=args.processes) as pool:
            results = pool.map(process_file, process_args)
        logging.info("All files processed")
    except Exception as e:
        print(f"✗ Error during parallel processing: {str(e)}")
        logging.error(f"Error during parallel processing: {str(e)}")
        sys.exit(1)

    # Aggregate results
    total_processed = len(results)
    successful = sum(1 for r in results if r['success'])
    changes_made = sum(1 for r in results if r['changes_made'])
    total_paragraphs = sum(r['paragraphs_processed'] for r in results)
    changed_paragraphs = sum(r['paragraphs_changed'] for r in results)

    # Print summary
    print(f"\nSummary:")
    print(f"✓ Processed {total_processed} document(s)")
    print(f"✓ Successfully processed {successful} document(s)")
    print(f"✓ Made changes to {changed_paragraphs} out of {total_paragraphs} paragraphs")
    logging.info(f"Summary: Processed {total_processed}, Successful {successful}, Changes {changed_paragraphs}/{total_paragraphs}")

    if args.verbose:
        print("\nDetailed statistics:")
        print(f"  - Documents processed: {total_processed}")
        print(f"  - Documents with changes: {changes_made}")
        print(f"  - Paragraphs processed: {total_paragraphs}")
        print(f"  - Paragraphs changed: {changed_paragraphs}")
        print(f"  - Change percentage: {changed_paragraphs/max(total_paragraphs, 1)*100:.1f}%")

        for result in results:
            if result['success']:
                print(f"\nFile: {result['output_path']}")
                if result['backup_path']:
                    print(f"  ✓ Backup created at: {result['backup_path']}")
                print(f"  ✓ Paragraphs changed: {result['paragraphs_changed']}/{result['paragraphs_processed']}")
            else:
                print(f"✗ Error in {result['output_path']}: {result['error']}")
                logging.error(f"Error in {result['output_path']}: {result['error']}")

    if successful < total_processed:
        print("✗ Some documents failed to process. Check errors above and 'scripture_standardization.log'.")
        logging.error("Some documents failed to process")
        sys.exit(1)

    print("Check 'scripture_standardization.log' for detailed processing information.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"✗ Fatal error: {str(e)}")
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)
