import sqlite3, json
from .file_logger import logger
from .constants import *

class Database():
    def __init__(self, filename, table_dict):
        self.filename = filename
        self.tables_dict = table_dict
        self.create()

    def create(self):
        connection = sqlite3.connect(self.filename)
        cursor = connection.cursor()

        create_table_queries = []
        for table_name, columns in self.tables_dict.items():
            columns_str = ",\n    ".join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])
            query = f"""CREATE TABLE IF NOT EXISTS {table_name} (
            {columns_str}
        );"""
            create_table_queries.append(query)
        for query in create_table_queries:
            cursor.execute(query)

        connection.commit()
        connection.close()

    def add(self, table: str, data: dict):
        connection = sqlite3.connect(self.filename)
        cursor = connection.cursor()

        if self.isIdExist(table, data['id'],cursor=cursor):
            connection.close()
            return False
    
        keys_str = f"({', '.join(data.keys())})"
        placeholder_str = f"({', '.join(['?'] * len(data))})"
        values = tuple(map(self.__convert_value, data.values()))

        cursor.execute(f'''
            INSERT INTO {table} {keys_str}
            VALUES {placeholder_str}
        ''', values)
        connection.commit()
        connection.close()
        return True

    def remove(self, table: str, data: dict):
        connection = sqlite3.connect(self.filename)
        cursor = connection.cursor()

        if not self.isIdExist(table, data['id'], cursor=cursor):
            connection.close()
            return False
        

        where_str = " AND ".join([f"{key} = ?" for key in data.keys()])
        values = tuple(map(self.__convert_value, data.values()))
        
        cursor.execute(f'''
            DELETE FROM {table}
            WHERE {where_str}
        ''', values)
        connection.commit()
        connection.close()
        return True

    def update(self, table: str, data: dict):
        connection = sqlite3.connect(self.filename)
        cursor = connection.cursor()

        if not self.isIdExist(table,data['id'], cursor=cursor):
            connection.close()
            return False

        set_str = ", ".join([f"{key} = ?" for key in data.keys() if key != 'id'])
        values = tuple(map(self.__convert_value, (data[key] for key in data.keys() if key != 'id')))
        cursor.execute(f'''
            UPDATE {table}
            SET {set_str}
            WHERE id = ?
        ''', values + (data['id'],))
        connection.commit()
        connection.close()
        return True

    def find(self, table: str, key: str, value):
        connection = sqlite3.connect(self.filename)
        cursor = connection.cursor()

        if isinstance(value, int|str|bool):
            value = (value,)   
        else:
            value = tuple(map(self.__convert_value,value))
        cursor.execute(f'SELECT * FROM {table} WHERE {key} = ?', value)
        result_list = cursor.fetchall()

        parsed_list = self.parse_results(table,result_list)

        connection.close()
        return parsed_list

    def getTableDict(self, table: str):
        connection = sqlite3.connect(self.filename)
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM {table}')
        result_list = cursor.fetchall()
        parsed_list = self.parse_results(table,result_list)
        connection.close()
        return parsed_list

    def isIdExist(self, table: str, id: int|str, cursor=None):
        if not cursor:
            need_to_close = True
            connection = sqlite3.connect(self.filename)
            cursor = connection.cursor()
        else:
            need_to_close = False
            
        cursor.execute(f'SELECT 1 FROM {table} WHERE id = ?', (id,))
        if cursor.fetchone():
            result = True
        else:
            result = False
        if need_to_close:
            connection.close()
        return result

    def parse_results(self, table, results):
        def convert_value(value, value_type):
                if value is None:
                    return None
                if 'INTEGER' in value_type:
                    return int(value)
                elif 'TEXT' in value_type:
                    try:
                        json_compatible_str = value.replace("'", '"')
                        return json.loads(json_compatible_str) if isinstance(value, str) and value.startswith('{') else value
                    except json.JSONDecodeError:
                        return value  # Оставляем как есть, если не удается преобразовать
                elif 'BOOLEAN' in value_type:
                    return bool(value)
                return value  # Если тип неизвестен, возвращаем значение как есть
        keys = list(self.tables_dict[table].keys())  # Извлекаем ключи из схемы таблицы            
        parsed_list = []
        for row in results:
            row_dict = {
                key: convert_value(value, self.tables_dict[table][key])
                for key, value in zip(keys, row)
            }
            parsed_list.append(row_dict)
        return parsed_list

    def __convert_value(self, value):
        if isinstance(value, (int, bool, str)):
            return value
        else:
            return str(value)  # Прочие типы также преобразуем в строку

db = Database(path.abspath('data/database.db'), TABLES_DICT)

if __name__ == "__main__":
    pass