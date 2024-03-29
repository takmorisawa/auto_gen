from urllib.request import urlopen
from urllib.parse import urljoin

import logging.config
import logging.handlers

import json
import lxml.html
from time import sleep
import sys
import os
import uuid
import shutil
import datetime
import time

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import Select
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.common.by import By

class GlobalState:

    def __init__(self):
        self._file_index=0

class HtmlGrabber:

    def __init__(self,work_dir,global_state,is_headless=True):

        options = ChromeOptions()
        if is_headless:
            options.add_argument('--headless')
        self._driver = Chrome(options=options)
        self._driver.set_window_size(1600,2560)

        self._work_dir=work_dir
        self._dom=None
        self._global_state=global_state
        self._interval=1

        self._sibling_func_map={
            1:self.__to_sibling_by_script,
            2:self.__to_sibling_by_button,
            3:self.__to_sibling_by_url
        }
        self._child_func_map={
            1:self.__to_child_by_url,
            2:self.__to_child_by_select,
            3:self.__to_child_by_button
        }
        self._operation_func_map={
            1:self.__operation_button,
        }

    def dispose(self):
        self._driver.quit()

    # 現在の状態を検証して必要があれば状態を修正する
    def __check_state(self,config,state):

        url=state["url"]
        # optional
        morebutton_xpath=config[0]["morebutton_xpath"] if "morebutton_xpath" in config[0] else None

        # ページリクエスト
        if self._driver.current_url!=url:
            self._driver.get(url)
            self.update()

        # 「さらに表示」ボタンをクリック
        count=0
        while morebutton_xpath:
            count+=1
            print("extend page: {}".format(count),end="\r")
            # ページを下までスクロール
            self._driver.execute_script('scroll(0,document.body.scrollHeight)')
            # 少し戻ろないとボタンが有効にならない
            self._driver.execute_script('scroll(0,-1600)')
            if self.__click_button(morebutton_xpath)==False:
                break

    # 状態を更新する
    def update(self):
        sleep(self._interval) # ボタンを押してからロード時間の待機が必要
        html = self._driver.page_source
        #self._driver.save_screenshot("page.png") # print screen
        self._dom=lxml.html.fromstring(html)

    def xpath(self,path):
        return self._dom.xpath(path)

    def get(self,url):
        self._driver.get(url)
        self.update()


    # ボタンをクリックしてページを追加ロード
    def __click_button(self,button_xpath):

        button=self._driver.find_element_by_xpath(button_xpath)
        if button.is_displayed():
            button.click()
            self.update()
            return True
        else:
            return False

    def __write(self):
        #path=os.path.join(self._work_dir,"{0}.html".format(uuid.uuid1()))
        path=os.path.join(self._work_dir,"{0:04}.html".format(self._global_state._file_index))
        self._global_state._file_index+=1
        html=self._driver.page_source
        with open(path,"w") as f:
            f.write(html) # ファイル出力


    # ボタンをクリック
    def __operation_button(self,config,state):

        logger = logging.getLogger()

        button_xpath=config[0]["operation_xpath_list"][0]
        check_xpath=config[0]["operation_xpath_list"][1]

        buttons=self._driver.find_elements_by_xpath(button_xpath)
        result=True
        for button in buttons:
            if button.is_displayed():
                done=False
                count=0
                while done==False and count < 10:
                    self._driver.execute_script("arguments[0].scrollIntoView();", button)
                    self._driver.execute_script(
                        "window.scrollTo(0, window.pageYOffset - " + str(500) + ");")
                    button.click()
                    time.sleep(0.1)
                    done=len(button.find_elements_by_xpath(check_xpath))>0
                    count+=1
                if done==True:
                    print("click: {}/{}".format(buttons.index(button)+1,len(buttons)),end="\r")
                else:
                    logger.info("timeout")
                result*=True
            else:
                result=True

        if result:
            self.update()
            self.process(config[1:],{
            "url":self._driver.current_url,
            "page_count":1
            })


    # Javascripを実行して次のページに遷移
    def __to_sibling_by_script(self,config,state):

        script_xpath=config[0]["sibling_xpath_list"][0]
        page_count=state["page_count"]

        script=self._dom.xpath(script_xpath)
        if len(script)!=0:
            self._driver.execute_script(script[0])
            self.update()
            self.process(config,{
                "url":self._driver.current_url,
                "page_count":page_count+1
            })

    # ボタンをクリックして次のページに遷移
    def __to_sibling_by_button(self,config,state):

        button_xpath=config[0]["sibling_xpath_list"][0]
        counter_xpath=config[0]["sibling_xpath_list"][1]
        page_count=state["page_count"]

        button=self._driver.find_element_by_xpath(button_xpath)
        if button.is_displayed():
            button.click()
            self.update()

            counter=int(self._dom.xpath(counter_xpath))
            if counter!=page_count:
                self.process(config,{
                    "url":self._driver.current_url,
                    "page_count":counter
                })

    # 次のページへのURLを取得
    def __to_sibling_by_url(self,config,state):

        sibling_xpath_list=config[0]["sibling_xpath_list"]
        nextpage_xpath=sibling_xpath_list[0]
        url=state["url"]
        page_count=state["page_count"]
        # optional
        ending_url=sibling_xpath_list[1] if len(sibling_xpath_list)>2 else None

        nextpage=self._dom.xpath(nextpage_xpath)
        if len(nextpage)>0:
            # 未テスト
            url=urljoin(self._driver.current_url,nextpage[0])
            if url!=ending_url:
                self.process(config,{
                    "url":url,
                    "page_count":page_count+1
                })


    def __to_child_by_url(self,config,state):

        url_list_xpath=config[0]["child_xpath_list"][0]

        url_list=self._dom.xpath(url_list_xpath)
        for child_url in url_list:
            child_url=urljoin(self._driver.current_url,child_url)
            # 再帰処理
            # グラバを作成
            grabber=HtmlGrabber(self._work_dir,self._global_state)
            grabber.process(config[1:],{
                "url":child_url,
                "page_count":1
            })
            grabber.dispose()

    def __to_child_by_select(self,config,state):

        child_xpath_list=config[0]["child_xpath_list"]
        options_xpath=child_xpath_list[0]
        select_xpath=child_xpath_list[1]
        #optional
        search_xpath=child_xpath_list[2] if len(child_xpath_list)>2 else None

        options=self._dom.xpath(options_xpath)
        for option in options:
            print("select:",option)

            elm=self._driver.find_element_by_xpath(select_xpath)
            Select(elm).select_by_value(option)
            self.update()

            # 検索ボタンをクリック
            if search_xpath:
                self._driver.find_element_by_xpath(search_xpath).click()
                self.update()

            self.process(config[1:],{
                "url":self._driver.current_url,
                "page_count":1
            })
            # 親ページの状態を復元
            self.__check_state(config,state)

    def __to_child_by_button(self,config,state):

        button_xpath=config[0]["child_xpath_list"][0]

        button=self._driver.find_element_by_xpath(button_xpath)
        if button.is_displayed():
            button.click()
            self.update()

            self.process(config[1:],{
                "url":self._driver.current_url,
                "page_count":1
            })


    def process(self,config,state):

        logger = logging.getLogger()

        # ページ情報読み込み
        url=state["url"] if "url" in state else ""
        page_count=state["page_count"] if "page_count" in state else -1

        # 設定データ読み込み
        child_type=config[0]["child_type"] if "child_type" in config[0] else -1
        sibling_type=config[0]["sibling_type"] if "sibling_type" in config[0] else -1
        operation_type=config[0]["operation_type"] if "operation_type" in config[0] else -1
        writing=config[0]["writing"] if "writing" in config[0] else False

        logger.info("crowling...{0},{1},{2}".format(url,page_count,writing))

        self.__check_state(config,state)

        # 子ページの処理
        if child_type in self._child_func_map:
            self._child_func_map[child_type](config,state)

        # 子ページから復帰後に元のページに戻る
        self.__check_state(config,state)

        # HTMLファイル書き出し
        if writing:
            self.__write()

        #次のページに遷移
        if sibling_type in self._sibling_func_map:
            self._sibling_func_map[sibling_type](config,state)

        if operation_type in self._operation_func_map:
            self._operation_func_map[operation_type](config,state)


def crowl(root,config_file_path):

    # ログ設定ファイルからログ設定を読み込み
    logging.config.fileConfig(os.path.join(root,"auto_gen/logging.conf"))

    config=[]
    with open(os.path.join(root,config_file_path),"r") as f:
        config=json.load(f)

    starting_urls=config[0]["starting_urls"]
    work_dir=os.path.join(root,config[0]["save_dir"])
    start_index=config[0]["start_index"] if "start_index" in config[0] else 0

    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    #os.rmdir(work_dir)
    os.mkdir(work_dir)

    # タイムスタンプを残す
    path=os.path.join(work_dir,datetime.date.today().strftime("%Y%m%d"))
    with open(path,"w") as f:
        pass

    gState=GlobalState()
    gState._file_index=start_index

    for url in starting_urls:

        # グラバを作成
        grabber=HtmlGrabber(work_dir,gState)
        grabber.process(config[1:],{
            "url":url,
            "page_count":1
        })
        grabber.dispose()


if __name__ == '__main__':

    args=sys.argv
    root_dir=args[1]
    config_dir=args[2]
    crowl(root_dir,config_dir)
