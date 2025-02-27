from sqlalchemy.orm import Session

from api.models import Printer


def get_printers_from_db(db: Session):
    return db.query(Printer).all()
