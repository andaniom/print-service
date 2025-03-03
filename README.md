# print-service

pyinstaller --onefile -F api/api.py --clean --noconsole  
pyinstaller --onefile --add-data "dist/api.exe:." --add-data "view:view" --add-data "print.exe:." --add-data "app.ico:." --icon "app.ico" --noconsole --name "Ecalyptus Printer" main.py