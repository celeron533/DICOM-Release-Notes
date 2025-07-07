import download_release_notes, download_document_list
import extract_release_notes, extract_document_list
import post_process

download_release_notes.download_release_notes()
download_document_list.download_document_list()
extract_document_list.extract_document_list()
extract_release_notes.extract_release_notes()
post_process.process()

print("All steps completed successfully.")