import pymysql as sql

# 使用上下文管理器确保文件正确关闭
with open("passwd") as f:
    passwd = f.read().strip()  # 移除尾随的换行符或空格

print("警告，会删除表中所有数据，是否继续？(y/n)")
n = input()
if n == 'y':
    # 使用上下文管理器确保数据库连接和游标正确关闭
    with sql.connect(host="localhost", user="root", password=passwd, database='chatchannel', charset='utf8') as db:
        with db.cursor() as cursor:
            try:
                cursor.execute('drop table if exists storage;')
                cursor.execute('create table storage (id int primary key auto_increment, nickname varchar(255), '
                               'message TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);')
                cursor.execute(f"insert into storage (nickname, message) values ('Apricityx', 'Hello world');")

                # 提交更改到数据库
                db.commit()
                print("Database initialized.")
            except sql.Error as e:
                # 如果发生错误，回滚更改
                db.rollback()
                print(f"An error occurred: {e}")
elif n == 'n':
    print("Operation canceled.")
else:
    print("Invalid input.")
