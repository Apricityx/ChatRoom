import requests
import json


def main():
    url = 'http://localhost/pull_message.php?count=5'
    response = requests.get(url)
    unpack(response.json())


def unpack(data):
    for item in data:
        print(item['nickname'], 'said', item['message'], 'at', item['timestamp'])


if __name__ == '__main__':
    main()
