# 发送post请求到localhost/index.php/post
import requests
import json


def post():
    url = 'http://localhost/post_message.php'
    data = {
        'nickname': 'zhangsan',
        'message': 'HELLO',
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(response.text)


if __name__ == '__main__':
    post()
