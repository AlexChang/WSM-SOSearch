import requests
import base64
import random

def rand_int(range):
    """int in [range[0], range[1]]"""
    return random.randint(range[0], range[1])

def rand_item(my_list):
    """random item from my_list"""
    return random.choice(my_list)

def base_code(username, password):
    str = '%s:%s' % (username, password)
    encodestr = base64.b64encode(str.encode('utf-8'))
    return '%s' % encodestr.decode()

def test_proxy():

    url = "http://myip.ipip.net/"

    ip_port = '180.118.247.15:4945'
    username = 'alexzhangfm@126.com'
    password = 'WSM19proxy'

    headers = {
        'Proxy-Authorization': 'Basic %s' % (base_code(username, password))
    }

    proxy = {
        'http': 'http://{}'.format(ip_port),
        # 'http': 'http://{}'.format('tunnel.qingtingip.com:8080'),
        # 'https': 'socks5://{}'.format(ip_port)
    }

    try:
        r = requests.get(url, proxies=proxy, headers=headers)
        # r = requests.get(url, proxies=proxy)
        print('response: {}, text: {}'.format(r, r.text))
    except Exception as e:
        print(e)

def main():
    test_proxy()
    return

if __name__ == '__main__':
    main()