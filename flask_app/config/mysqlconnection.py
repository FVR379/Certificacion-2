import pymysql.cursors


class MySQLConnection:
    def __init__(self, db):
        self.connection = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            db=db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

    def query_db(self, query, data=None):
        try:
            with self.connection.cursor() as cursor:
                if data is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query, data)

                if query.lstrip().lower().startswith("insert"):
                    return cursor.lastrowid
                if query.lstrip().lower().startswith("select"):
                    return cursor.fetchall()
                return cursor.rowcount
        finally:
            self.connection.close()


def connectToMySQL(db):
    return MySQLConnection(db)