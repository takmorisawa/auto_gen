import requests
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import urllib.parse as urlparse

class CallbackServer(BaseHTTPRequestHandler):
    def __init__(self, callback, *args):
        self.callback = callback
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        query = parsed_path.query
        self.send_response(200)
        self.end_headers()
        result = self.callback(query)
        message = '\r\n'.join(result)
        #self.wfile.write(message)
        dic={kv.split("=")[0]:kv.split("=")[1] for kv in query.split("&")}
        print("message is {0}\n:".format(dic["msg"]))
        return

#import sys
#import CallbackServer

def callback_method(query):
    return ['Hello', 'World!', 'with', query]


import threading

if __name__ == '__main__':
      
    #port = sys.argv[1]
    port = 12353
    #start(port, callback_method)
    
    def handler(*args):
        CallbackServer(callback_method, *args)
    server = HTTPServer(('', int(port)), handler)
    #server.serve_forever()
    
    th=threading.Thread(target=lambda:server.serve_forever())
    th.start()

    import logging.config
    import logging.handlers
     
    # ログ設定ファイルからログ設定を読み込み
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger()
    
    logger.log(20, 'info')
    logger.log(30, 'warning')
    #logger.log(50, 'test')
     
    logger.info('info')
    logger.warning('warning')
    logger.critical("send to slack")
    

    server.server_close()

    import requests
    import json

    data = json.dumps({
        'text': u'Test', # 投稿するテキスト
        'username': u'me', # 投稿のユーザー名
        'icon_emoji': u':ghost:', # 投稿のプロフィール画像に入れる絵文字
        'link_names': 1, # メンションを有効にする
        })
    #print(data)

    #requests.post("https://hooks.slack.com/services/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",
    #              data = json.dumps({
    #                    'text': u'Test', # 投稿するテキスト
    #                    'username': u'me', # 投稿のユーザー名
    #                    'icon_emoji': u':ghost:', # 投稿のプロフィール画像に入れる絵文字
    #                    'link_names': 1, # メンションを有効にする
    #                    }))