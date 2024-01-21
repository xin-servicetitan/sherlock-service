import pyodbc

class DatabaseHandler:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def connect(self):
        self.conn = pyodbc.connect(self.connection_string)
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)

            if query.strip().lower().startswith("select"):
                return self.cursor.fetchall()
            else:
                self.conn.commit()
                return None
        except Exception as e:
            print(f"Error executing query: {e}")
            return None

    def commit(self):
        self.conn.commit()

