import logging
from download_release_notes import download_release_notes
from download_document_list import download_document_list
from extract_document_list import extract_document_list
from extract_release_notes import extract_release_notes
from post_process import process

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    steps = [
        ("Downloading release notes", download_release_notes),
        ("Downloading document list", download_document_list),
        ("Extracting document list", extract_document_list),
        ("Extracting release notes", extract_release_notes),
        ("Post processing", process)
    ]
    
    for description, func in steps:
        try:
            logger.info(f"Starting: {description}")
            func()
            logger.info(f"Completed: {description}")
        except Exception as e:
            logger.error(f"Failed: {description} - {str(e)}", exc_info=True)
            raise

if __name__ == "__main__":
    try:
        main()
        logger.info("All steps completed successfully.")
        print("All steps completed successfully.")
    except Exception as e:
        logger.critical(f"Application failed: {str(e)}", exc_info=True)