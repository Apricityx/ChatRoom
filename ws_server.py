import asyncio
import websockets
import pymysql as sql
import json
import ssl

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
        passwd = f.read().strip()
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
                'timestamp': data[i][3].strftime('%Y-%m-%d %H:%M:%S')
            })
        # debug(type(result[1]['timestamp']))
        # result = str(result)
        return result

    def post_message(self, nickname, message):
        cursor = self.cursor
        debug(f"尝试运行数据库指令insert into storage (nickname, message) values ('{nickname}', '{message}');")
        cursor.execute(f"insert into storage (nickname, message) values ('{nickname}', '{message}');")
        cursor.execute("commit;")  # 此处需要commit才能生效


database = DB()


# database.post_message("zhangsan", "HELLO")


async def check_online():
    global clients
    time = len(clients)
    del_clients = []
    for i in range(0, time):
        debug('检测是否在线')
        client = clients[i]
        try:
            await client.send({
                "method": "ping"
            })
        except Exception:
            del_clients.append(i)
            continue
    for i in range(0, len(del_clients)):
        clients.pop(i)
    debug(f"已删除：{len(del_clients)}个离线客户端")


async def send_update_to_all():
    global clients
    time = len(clients)
    del_clients_num = []
    for i in range(0, time):
        debug(f"尝试广播")
        client = clients[i]

        try:
            await client.send(json.dumps({
                "method": "update",
                "data": database.pull_message(1)
            }))
        except Exception as ConnectionClosedOK:
            debug(f"客户端已断开连接: {ConnectionClosedOK}")
            del_clients_num.append(i)
            continue
        except Exception as e:
            debug(f"未知错误: {e}")
            continue
    i = 0
    for client in del_clients_num:
        clients.pop(client - i)
        i += 1
    debug(f"已删除{len(del_clients_num)}个离线客户端")


async def on_message(message, client):
    message = json.loads(message)  # 将收到的JSON数据转换为字典
    debug(f"Received client ws message: {message}")
    if message["method"] == "ping":
        print("新连接建立")
    # on_websocket_send 定义有以下方法pull push update
    elif message["method"] == "pull":
        count = message["pullNum"]
        result = {"method": "pull", "data": database.pull_message(count)}
        debug(f"pull_message: {result}")
        await client.send(json.dumps(result))  # 这里数据发不出去
        return result
    elif message["method"] == "push":
        debug("pushing")
        data = message["data"]
        nickname = data["nickname"]
        message = data["message"]
        database.post_message(nickname, message)
        await send_update_to_all()


async def server_start(websocket, path):
    global clients
    # 每一个客户端建立连接都会执行此处的指令
    clients.append(websocket)
    debug(f"当前在线：{len(clients)}")
    async for message in websocket:
        await on_message(message, websocket)


# pull_message(1)
# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# ssl_context.load_cert_chain('pve.zwtsvx.xyz_bundle.pem', 'pve.zwtsvx.xyz.key')
#
# start_server = websockets.serve(
#     server_start,
#     "localhost",
#     8083,
#     ssl=ssl_context
# )
start_server = websockets.serve(server_start, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
