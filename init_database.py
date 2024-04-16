import pymysql as sql


print("警告，会删除表中所有数据，是否继续？(y/n)")
n = input()
if n == 'y':
    db = sql.connect(host="localhost", user="root", password="520520SQL", database='chatchannel', charset='utf8')
    cursor = db.cursor()
    cursor.execute('use chatchannel;')
    cursor.execute('drop table if exists storage;')
    cursor.execute('create table storage (id int primary key auto_increment, nickname varchar(255), '
                   'message TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);')
    cursor.execute(f"insert into storage (nickname, message) values ('Apricityx', 'Hello world');")
    cursor.execute("commit;")
    cursor.close()
    db.close()
    print("Database initialized.")
elif n == 'n':
    print("Operation canceled.")
else:
    print("Invalid input.")