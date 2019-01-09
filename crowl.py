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

options = ChromeOptions()            
options.add_argument('--headless')
driver = Chrome(options=options)
driver.set_window_size(2560,1600)

def request(url,render_js,morebutton_xpath=""):
    
    html=""
    if render_js:
        
        if url!="_nextpage_":
            driver.get(url)

        # 「さらに表示」ボタンをクリック
        if morebutton_xpath:
            get_button=lambda:driver.find_element_by_xpath(morebutton_xpath)
            button=get_button()
            while button.is_displayed():
                print("morebutton:", button.text)
                button.click()
                driver.execute_script('scroll(0,document.body.scrollHeight)')
                button=get_button()
                #wait=WebDriverWait(driver,5)
                #button=wait.until(EC.element_to_be_clickable((By.XPATH,morebutton_xpath)))
        
        sleep(1) # ボタンを押してからロード時間の待機が必要
        html = driver.page_source
        driver.save_screenshot("page.png") # print screen
    else:
        # 不具合の可能性あり
        html=urlopen(url).read()
    
    return html


def crowl(config_file_path):

    # 設定ファイルに記述するパスは、このプログラムが置かれているディレクトリを基準とする
    root=os.path.dirname(os.path.abspath(__file__))
    
    config={}
    with open(config_file_path,"r") as f:
        config=json.load(f)
        
    starting_urls=config["starting_urls"]
    ending_url=config["ending_url"]
    target_xpath=config["target_xpath"]
    nextpage_xpath=config["nextpage_xpath"]
    save_dir=os.path.join(root,config["save_dir"])
    render_js=config["render_js"] if "render_js" in config else 1
    morebutton_xpath=config["morebutton_xpath"] if "morebutton_xpath" in config else None
    nextscript_xpath=config["nextscript_xpath"] if "nextscript_xpath" in config else None
    nextbutton_xpath=config["nextbutton_xpath"] if "nextbutton_xpath" in config else None

    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)
    #os.rmdir(save_dir)
    os.mkdir(save_dir)
    
    # タイムスタンプを残す
    path=os.path.join(root,"{0}/{1}".format(save_dir,datetime.date.today().strftime("%Y%m%d")))
    with open(path,"w") as f:
        pass

    for url in starting_urls:
        while url!=ending_url:
            
            print("crowling...{0}".format(url))
            
            html=request(url,render_js,morebutton_xpath)
            dom=lxml.html.fromstring(html)
            
            if target_xpath=="":
                path=os.path.join(root,"{0}/{1}.html".format(save_dir,uuid.uuid1()))
                with open(path,"w") as f:
                    f.write(html) # ファイル出力
            else:
                # 1ページにダウンロードするURLが複数ある場合
                for target in dom.xpath(target_xpath):
                    url=urljoin(starting_urls[0],target)
                    html=request(url,render_js)
                    path=os.path.join(root,"{0}/{1}.html".format(save_dir,uuid.uuid1()))
                    with open(path,"w") as f:
                        f.write(html) # ファイル出力
            
            url="" # urlが空白の場合はループを抜ける
            
            # 次のページへのボタンをクリック
            if nextscript_xpath:
                next_script=dom.xpath(nextscript_xpath)
                if len(next_script)!=0:
                    driver.execute_script(next_script[0])
                    url="_nextpage_"
 
            # ページ切り替えボタンをクリック（mineo専用）
            endflag=dom.xpath("//li[@class='num_2']/a[@class='on']")
            if nextbutton_xpath:
                button=driver.find_element_by_xpath(nextbutton_xpath)
                if len(endflag)==0:
                    button.click()
                    url="_nextpage_"
                    print(dom.xpath("//li[@class='num_2']/a/@href"))
                    
            # 次のページへのURLを取得
            if nextpage_xpath!="":
                nextpage=dom.xpath(nextpage_xpath)
                if len(nextpage)!=0:
                    url=urljoin(starting_urls[0],nextpage[0])

    
if __name__ == '__main__':

    crowl("projects/support_devices/mvno/mineo/crowl.config")