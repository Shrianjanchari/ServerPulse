import sqlite3
connection=sqlite3.connect("monitor.db")
cursor=connection.cursor()
cursor.execute("""
create table if not exists system_metrics(
id INTEGER primary key autoincrement,
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
hostname TEXT,
CPU REAL,
RAM REAL,
disk REAL
)
""")
connection.commit()
print("Table Created Successfully")
connection.close()
