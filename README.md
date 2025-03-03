# print-service

pyinstaller -F api/api.py --clean --noconsole
pyinstaller --onefile --add-data "api:api" --add-data "view:view" --add-data "print.exe:." --add-data "app.ico:." --icon "app.ico" --noconsole --name "Ecalyptus Printer" main.py