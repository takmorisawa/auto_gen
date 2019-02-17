from urllib.request import urlopen
from urllib.parse import urljoin

import json
import lxml.html
from time import sleep
import os
import uuid
import shutil
import datetime

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import Select
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.common.by import By

"""
config

starting_urls
ending_url
target_xpath
nextpage_xpath
save_dir
render_js
morebutton_xpath
nextscript_xpath
"""

class HtmlGrabber:

    def __init__(self,root):

        options = ChromeOptions()
        options.add_argument('--headless')
        self._driver = Chrome(options=options)
        self._driver.set_window_size(2560,1600)

        self._root_dir=root
        self._html=""
        self._dom=None

        self._sibling_func_map={
            1:self.__to_sibling_by_script,
            2:self.__to_sibling_by_button,
            3:self.__to_sibling_by_url
        }
        self._child_func_map={
            1:self.__to_child_by_url,
            2:self.__to_child_by_select
        }

    def __check_state(self,config,state):

        url=state["url"]
        # optional
        morebutton_xpath=config[0]["morebutton_xpath"] if "morebutton_xpath" in config[0] else ""

        # ページリクエスト
        if self._driver.current_url!=url:
            self._driver.get(url)

        # 「さらに表示」ボタンをクリック
        while morebutton_xpath and self.__click_button(morebutton_xpath):
            # ページを下までスクロール
            self._driver.execute_script('scroll(0,document.body.scrollHeight)')

        self.__update()

    def __update(self):
        sleep(1) # ボタンを押してからロード時間の待機が必要
        self._html = self._driver.page_source
        self._driver.save_screenshot("page.png") # print screen
        self._dom=lxml.html.fromstring(self._html)

    # ボタンをクリックしてページを追加ロード
    def __click_button(self,button_xpath):

        button=self._driver.find_element_by_xpath(button_xpath)
        if button.is_displayed():
            button.click()
            self.__update()
            return True
        else:
            return False


    # Javascripを実行して次のページに遷移
    def __to_sibling_by_script(self,config,state):

        script_xpath=config[0]["sibling_xpath_list"][0]
        url=state["url"]
        page_count=state["page_count"]

        script=self._dom.xpath(script_xpath)
        if len(script)!=0:
            self._driver.execute_script(script[0])
            self.__update()
            self.process(config,{
                "url":url,
                "page_count":page_count+1
            })

    # ボタンをクリックして次のページに遷移
    def __to_sibling_by_button(self,config,state):

        button_xpath=config[0]["sibling_xpath_list"][0]
        counter_xpath=config[0]["sibling_xpath_list"][1]
        url=state["url"]
        page_count=state["page_count"]

        button=self._driver.find_element_by_xpath(button_xpath)
        if button.is_displayed():
            button.click()
            self.__update()

            counter=int(self._dom.xpath(counter_xpath))
            if counter!=page_count:
                self.process(config,{
                    "url":url,
                    "page_count":counter
                })

    # 次のページへのURLを取得
    def __to_sibling_by_url(self,config,state):

        nextpage_xpath=config[0]["sibling_xpath_list"][0]
        ending_url=config[0]["sibling_xpath_list"][1]
        url=state["url"]
        page_count=state["page_count"]

        nextpage=self._dom.xpath(nextpage_xpath)
        if len(nextpage)!=0:
            # 未テスト
            url=urljoin(self._driver.current_url(),nextpage[0])
            if url==ending_url:
                self.process(config,{
                    "url":url,
                    "page_count":page_count+1
                })


    def __to_child_by_url(self,config,state):

        url_list_xpath=config[0]["child_xpath_list"][0]

        url_list=self._dom.xpath(url_list_xpath)
        for child_url in url_list:
            # 再帰処理
            self.process(config[1:],{
                "url":child_url,
                "page_count":1
            })

    def __to_child_by_select(self,config,state):

        url=state["url"]
        options_xpath=config[0]["child_xpath_list"][0]
        select_xpath=config[0]["child_xpath_list"][1]

        options=self._dom.xpath(options_xpath)
        for option in options:
            print("select:",option)
            elm=self._driver.find_element_by_xpath(select_xpath)
            Select(elm).select_by_value(option)
            self.process(config[1:],{
                "url":url,
                "page_count":1
            })


    def __write(self,dir):
        path=os.path.join(dir,"{0}.html".format(uuid.uuid1()))
        self._html=self._driver.page_source
        with open(path,"w") as f:
            f.write(self._html) # ファイル出力

    def process(self,config,state):

        # ページ情報読み込み
        url=state["url"] if "url" in state else ""
        page_count=state["page_count"] if "page_count" in state else -1

        # 設定データ読み込み
        child_type=config[0]["child_type"] if "child_type" in config[0] else -1
        sibling_type=config[0]["sibling_type"] if "sibling_type" in config[0] else -1
        save_dir=os.path.join(self._root_dir,config[0]["save_dir"]) if "save_dir" in config[0] else None

        print("crowling...\n\t{0},{1},\n\t{2}".format(url,page_count,save_dir))

        self.__check_state(config,state)

        # 子ページの処理
        if child_type in self._child_func_map:
            self._child_func_map[child_type](config,state)

        # HTMLファイル書き出し
        if save_dir:
            self.__write(save_dir)

        #次のページに遷移
        if sibling_type in self._sibling_func_map:
            self._sibling_func_map[sibling_type](config,state)


def crowl(root,config_file_path):

    config=[]
    with open(os.path.join(root,config_file_path),"r") as f:
        config=json.load(f)

    starting_urls=config[0]["starting_urls"]
    save_dir=os.path.join(root,config[0]["save_dir"])

    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)
    #os.rmdir(save_dir)
    os.mkdir(save_dir)

    # タイムスタンプを残す
    path=os.path.join(root,"{0}/{1}".format(save_dir,datetime.date.today().strftime("%Y%m%d")))
    with open(path,"w") as f:
        pass

    for url in starting_urls:

        # グラバを作成
        grabber=HtmlGrabber(root)
        grabber.process(config[1:],{
            "url":url,
            "page_count":None
        })


if __name__ == '__main__':

    crowl("/Users/tkyk/Documents/repo/supported_devices","mvno/mineo/crowl.config")
