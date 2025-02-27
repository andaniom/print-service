from sqlalchemy.orm import Session

from api.logger import logger
from api.models import MappingPrinter


def get_mapping_printer_by_label(db: Session, label: str):
    return db.query(MappingPrinter).filter(MappingPrinter.label == label).first()

def get_mapping_printers_from_db(db: Session):
    return db.query(MappingPrinter).all()

def save_mapping_printers_to_db(db: Session, printer: MappingPrinter):
    # for printer in printers:
    db_printer = MappingPrinter(
        label=printer.label,
        printer_name=printer.printer_name,
        printer_label=printer.printer_label,
        vendor_id=printer.vendor_id,
        product_id=printer.product_id
    )
    db.add(printer)
    db.commit()
    db.refresh(db_printer)
    logger.info("Printers saved successfully")
