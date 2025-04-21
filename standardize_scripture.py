"""
standardize_scripture.py - Main script to process Word documents and standardize Bible references.
"""

import os
import argparse
import logging  # Import logging here

# Configure logging
logging.basicConfig(level=logging.DEBUG)

from document_processing import process_document
from file_utils import get_docx_files

def main():
    logging.debug("Starting the main function...")

    try:
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="Standardize Bible references in Word documents.")
        parser.add_argument('input_path', help="Path to a .docx file or a directory containing .docx files.")
        parser.add_argument('output_path', help="Path to save the processed file(s).")
        parser.add_argument('--no-backup', action='store_false', dest='create_backup', help="Do not create backup files.")
        args = parser.parse_args()

        input_path = args.input_path
        output_path = args.output_path
        create_backup = args.create_backup

        # Debugging: Log the input arguments
        logging.debug(f"Input path: {input_path}")
        logging.debug(f"Output path: {output_path}")
        logging.debug(f"Create backup: {create_backup}")

        # Check if input path is a directory or a single file
        if os.path.isdir(input_path):
            logging.debug(f"Processing directory: {input_path}")
            # Process all .docx files in the directory
            docx_files = get_docx_files(input_path)
            for docx_file in docx_files:
                output_file = os.path.join(output_path, os.path.basename(docx_file))
                result = process_document(docx_file, output_file, should_create_backup=create_backup)
                if result['success']:
                    logging.info(f"Processed: {docx_file} -> {output_file}")
                else:
                    logging.error(f"Failed to process {docx_file}: {result['error']}")
        elif os.path.isfile(input_path) and input_path.endswith('.docx'):
            logging.debug(f"Processing single file: {input_path}")
            # Process a single .docx file
            result = process_document(input_path, output_path, should_create_backup=create_backup)
            if result['success']:
                logging.info(f"Processed: {input_path} -> {output_path}")
            else:
                logging.error(f"Failed to process {input_path}: {result['error']}")
        else:
            logging.error("Invalid input path. Please provide a .docx file or a directory containing .docx files.")

    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        raise

if __name__ == "__main__":
    main()