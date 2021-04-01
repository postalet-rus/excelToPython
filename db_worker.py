import sqlite3
import re
from tkinter import messagebox
from pathlib import Path


class DBWorker:

    def __init__(self, db_name):
        self.db_name = db_name

    def filter(self, *args, **kwargs) -> list:
        self.open_connection()
        if self.cursor:
            params = []
            query = """
                    SELECT * FROM %(table_name)s WHERE id=id
                    """ % {"table_name": re.sub(r"['`\"]", "", kwargs.get("table_name"))}
            
            for key, value in kwargs.items():
                if key != "table_name":
                    if "__greater" in key:
                        key = key.replace("__greater", "")
                        query += "AND %(key)s>?" % {"key": re.sub(r"['`\"]", "", key)}    
                    elif "__lesser" in key:
                        key = key.replace("__lesser", "")
                        query += "AND %(key)s<?" % {"key": re.sub(r"['`\"]", "", key)}
                    else:
                        query += "AND %(key)s=?" % {"key": re.sub(r"['`\"]", "", key)}
                    print(type(value))
                    
                    params.append(value)
            self.cursor.execute(query, params)
            data = self.cursor.fetchall()    
            self.close_connection()
            return data
        else: 
            print("\033[96mCursor object doesn't exists (db_worker)\033[0m")
            try:
                self.close_connection()
            except:
                print("\033[96mFatal error has occured\033[0m")
                raise OSError

    @staticmethod
    def check_db(db_name) -> bool:
        if Path(Path.cwd() / db_name).is_file():
            print("\033[96mDatabase file already exists\033[0m")
            return True
        else:
            print("\033[91mDatabase file doesn't exists attempting to create one from excel\033[0m")    
            return False

    def open_connection(self):
        if Path(Path.cwd() / self.db_name).is_file():
            try:
                self.conn = sqlite3.connect(self.db_name)  # create temp database
                self.cursor = self.conn.cursor()  # create cursor object

                print("database has been successfully connected")

            except sqlite3.Error as error:
                messagebox.showerror("Ошибка", "An error has occured when trying connect to sqlite")
                print(
                    f"\033[91mAn error has occured when trying connect to sqlite\n {error}\033[0m")
        else:
            messagebox.showerror("Ошибка", "\033[91mDatabase file doesn't exists\033[0m")
            print("\033[91mDatabase file doesn't exists\033[0m")

    def close_connection(self):
        self.conn.close()


def main():
    dbworker = DBWorker("tmp.db")

if __name__ == "__main__":
    main()
