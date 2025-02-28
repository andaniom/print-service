import usb.core
import usb.util

from api.logger import logger


def list_usb_printers():
    devices = usb.core.find(find_all=True)
    printers = []
    for device in devices:
        try:
            vendor_id = device.idVendor
            product_id = device.idProduct
            manufacturer = usb.util.get_string(device, device.iManufacturer)
            product = usb.util.get_string(device, device.iProduct)

            printers.append({
                "vendor_id": vendor_id,
                "product_id": product_id,
                "manufacturer": manufacturer,
                "product": product,
            })
        except usb.core.USBError as e:
            logger.error(f"Error accessing device: {e}")
    return printers
