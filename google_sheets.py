import gspread, json
from oauth2client.service_account import ServiceAccountCredentials




class GoogleSheets:

    class Car:
        def __init__(self, table_row = list()):
            self.brand  = str()
            self.region = str()
            self.data = list()
            if len(table_row):
                self.data = table_row
                self.region = self.data[0]
                self.brand = self.data[1]


    def __init__(self, configs):
        self.configs = configs

        self.columns  = list()
        self.brands   = dict()
        self.cars     = list()

        try:
            print("Google API auth...")
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(filename=self.configs['api-key-filename'],
                                                                     scopes=scope)
            self.client = gspread.authorize(creds)
            print("Authorized")
        except Exception as err:
            print("Google API auth ERROR:")
            print(err, '\n\n')

    def update(self):  # Обновить локальные данные в ./data
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
with open('settings\\settings.json', 'r', encoding='utf-8') as file:
    bot_configs = json.load(file)
    carTable = GoogleSheets(bot_configs)
