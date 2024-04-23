import asyncio
import time

import websockets
import pymysql as sql
import json
import ssl

database_url = 'localhost'
clients = {}


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


def client_del(client):
    global clients
    clients.pop(client.self_id)
    del client


# database.post_message("zhangsan", "HELLO")
class WebSocketClient:
    ws_core = None  # ws_core是一个可遍历的对象，可以用来接收消息
    self_id = None

    # self_clock = 10  # 10秒没收到ping包就认为掉线

    async def client_start(self):
        debug("WebSocket client start")

    def __init__(self, websocket, self_id):
        self.ws_core = websocket
        self.self_id = self_id
        asyncio.ensure_future(self.client_start())

    async def send(self, raw_message):  # 此处raw_message是字典
        await self.ws_core.send(json.dumps(raw_message))
        debug(f"Sent client ws message: {raw_message}")

    async def on_message(self, raw_message):  # 此处raw_message是字典
        message = raw_message
        debug(f"Received client ws message: {message}")
        if message["method"] == "ping":
            print("新连接建立")
        # on_websocket_send 定义有以下方法pull push update
        elif message["method"] == "pull":
            count = message["pullNum"]
            result = {"method": "pull", "data": database.pull_message(count)}
            debug(f"pull_message: {result}")
            await self.send(result)  # 这里数据发不出去
            return result
        elif message["method"] == "push":
            debug("pushing")
            data = message["data"]
            nickname = data["nickname"]
            message = data["message"]
            database.post_message(nickname, message)
            await send_update_to_all()
        elif message["method"] == "ping":
            debug("ping")
            await self.send(json.dumps({"method": "ping", "data": "pong!!"}))  # 未实现


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
    del_id_list = []
    for key in clients:
        client = clients[key]
        debug(f"尝试广播")
        try:
            await client.send({
                "method": "update",
                "data": database.pull_message(1)
            })
        except Exception as ConnectionClosedOK:
            debug(f"客户端已断开连接: {ConnectionClosedOK}")
            del_id_list.append(key)
            continue
        except Exception as e:
            debug(f"未知错误: {e}")
            del_id_list.append(key)
            continue
    for del_id in del_id_list:
        clients.pop(del_id)
    debug(f"已删除：{len(del_id_list)}个离线客户端")


# async def on_message(message, client):
#     message = json.loads(message)  # 将收到的JSON数据转换为字典
#     debug(f"Received client ws message: {message}")
#     if message["method"] == "ping":
#         print("新连接建立")
#     # on_websocket_send 定义有以下方法pull push update
#     elif message["method"] == "pull":
#         count = message["pullNum"]
#         result = {"method": "pull", "data": database.pull_message(count)}
#         debug(f"pull_message: {result}")
#         await client.send(json.dumps(result))  # 这里数据发不出去
#         return result
#     elif message["method"] == "push":
#         debug("pushing")
#         data = message["data"]
#         nickname = data["nickname"]
#         message = data["message"]
#         database.post_message(nickname, message)
#         await send_update_to_all()
#     elif message["method"] == "ping":
#         debug("ping")
#         await client.send(json.dumps({}))  # 未实现


async def server_start(websocket, path):
    # 传进来一个websocket对象，可以用来发送消息
    # websocket对象拥有send方法，可以用来发送消息
    client_id = int(time.time())
    client = WebSocketClient(websocket, client_id)
    global clients
    # 每一个客户端建立连接都会执行此处的指令
    clients[client_id] = client
    debug(f"当前在线：{len(clients)}")
    await client.send("Hello, world!")
    async for message in client.ws_core:
        debug(f"Received client ws message: {message}")
        message = json.loads(message)  # 将收到的JSON数据转换为字典
        await client.on_message(message)  # 处理客户端发来的消息


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
