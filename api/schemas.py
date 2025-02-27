from pydantic import BaseModel

class PrinterCreate(BaseModel):
    name: str
    label: str
    vendor_id: str
    product_id: str

class Printer(BaseModel):
    id: int
    name: str
    label: str
    vendor_id: str
    product_id: str

    class Config:
        orm_mode = True

class MappingPrinterCreate(BaseModel):
    label: str
    printer_name: str
    printer_label: str
    vendor_id: str
    product_id: str

class MappingPrinter(BaseModel):
    id: int
    label: str
    printer_name: str
    printer_label: str
    vendor_id: str
    product_id: str

    class Config:
        orm_mode = True
