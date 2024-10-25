import gspread, json
from oauth2client.service_account import ServiceAccountCredentials

from file_logger import logger


class GoogleSheets:

    class Car:
        def __init__(self, table_row = list()):
            self.brand  = str()
            self.region = str()
            self.name = str()

            self.data = list()
            if len(table_row):
                self.data = table_row
                self.region = self.data[0]
                self.brand = self.data[1]
                self.model = self.data[2]
                self.configuration = self.data[4]


    def __init__(self, configs):
        self.configs = configs

        self.columns  = list()
        self.brands   = dict()
        self.cars     = list()

        try:
            logger.info("Google API: Auth...")
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(filename=self.configs['api-key-filename'],
                                                                     scopes=scope)
            self.client = gspread.authorize(creds)
            logger.info("Google API: Auth is OK")
        except Exception as err:
            logger.error(f"Google API: Auth ERROR:\n{err}")

    def update(self):  # Обновить локальные данные
        logger.info("Google API: Table updating")

        spreadsheet = self.client.open_by_url(self.configs['docs-google-link'])
        sheet = spreadsheet.worksheet(self.configs['list-name'])
    
        self.columns.clear()
        self.brands.clear()
        self.cars.clear()

        data_list = sheet.get_all_values()
        self.columns = data_list[0] # Заполнение колонок
        for data in data_list[1:]:

            if data[0] not in self.brands.keys():
                if data[0] == '':
                    continue
                self.brands[data[0]] = list()

            if data[1] not in self.brands[data[0]]:
                if data[1] == '':
                    continue
                self.brands[data[0]].append(data[1])

            self.cars.append(self.Car(data))



# -------------------------------------------------------
carTable = None
with open('settings/settings.json', 'r', encoding='utf-8') as file:
    bot_configs = json.load(file)
    carTable = GoogleSheets(bot_configs)
