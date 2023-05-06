import sqlite3

# создание соединения с базой данных
conn = sqlite3.connect("./instance/database.db")

# получение курсора
cur = conn.cursor()

# выполнение запроса и получение всех строк

cur.execute("SELECT * FROM chathistory")
row = cur.fetchone()

# вывод всех строк

print(row)

# закрытие соединения с базой данных
conn.close()
