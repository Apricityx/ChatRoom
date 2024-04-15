import asyncio
import websockets
import pymysql as sql
import json

database_url = 'localhost'
clients = []


def debug(content):
    ifDebug = True
    if ifDebug:
        print(f"\033[33mDebug:{content}\033[0m")


# 和数据库交互
class DB:
    def __init__(self):
        # 连接到数据库
        f = open("passwd")
        passwd = f.read()
        f.close()
        db = sql.connect(host="localhost", user="root", password=passwd, database='chatchannel', charset='utf8')
        cursor = db.cursor()
        cursor.execute('use chatchannel;')
        self.cursor = cursor

    def pull_message(self, count):
        cursor = self.cursor
        cursor.execute(f'select * from storage order by id desc limit {count};')
        data = cursor.fetchall()
        # 将data转换为类JSON列表
        result = []
        for i in range(0, len(data)):
            result.append({
                'nickname': data[i][1],
                'message': data[i][2],
                'timestamp': data[i][3]
            })
        return result

    def post_message(self, nickname, message):
        cursor = self.cursor
        cursor.execute(f"insert into storage (nickname, message) values ('{nickname}', '{message}');")
        cursor.execute("commit;")  # 此处需要commit才能生效


database = DB()
database.post_message("zhangsan", "HELLO")


async def send_update_to_all():
    global clients
    time = len(clients)
    del_clients = []
    for i in range(0, time):
        debug(f"尝试广播")
        client = clients[i]
        try:
            await client.send("update")
        except Exception:
            del_clients.append(i)
            continue
    for i in range(0, len(del_clients)):
        clients.pop(i)


async def on_message(message, client):
    message = json.loads(message)
    debug(f"Received client ws message: {message}")
    if message["method"] == "ping":
        print("新连接建立")
    # on_websocket_send 定义有以下方法pull push update
    elif message["method"] == "pull":
        count = message["pullNum"]
        result = database.pull_message(count)
        debug(f"pull_message: {result}")
        await client.send(str(result))  # 这里数据发不出去
        return result


async def server_start(websocket, path):
    global clients
    # 每一个客户端建立连接都会执行此处的指令
    clients.append(websocket)
    debug(f"当前在线：{len(clients)}")
    async for message in websocket:
        await on_message(message, websocket)


# pull_message(1)

start_server = websockets.serve(server_start, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
