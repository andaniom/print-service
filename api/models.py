from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Printer(Base):
    __tablename__ = "printers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    label = Column(String, unique=True, index=True)
    vendor_id = Column(String, index=True)
    product_id = Column(String, index=True)

class MappingPrinter(Base):
    __tablename__ = "mapping_printers"
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, index=True)
    printer_name = Column(String, index=True)
    printer_label = Column(String, index=True)
    vendor_id = Column(String, index=True)
    product_id = Column(String, index=True)
