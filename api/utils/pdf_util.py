# import os
#
# from pdf2image import convert_from_path
#
# from api.logger import logger
#
#
# def convert_pdf_to_images(pdf_file):
#     try:
#         poppler_path = os.path.join(os.path.dirname(__file__), "poppler", "bin")
#         logger.info(f"poppler_path: {poppler_path}")
#         images = convert_from_path(pdf_file, fmt="jpeg", poppler_path=poppler_path)
#         logger.info(f"Converted PDF to images: {pdf_file} {len(images)}")
#         return images
#     except Exception as e:
#         logger.error(f"Failed to convert PDF to images: {e}")
#         return []
