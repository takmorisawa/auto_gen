from urllib.request import urlopen
from urllib.parse import urljoin

import json
import lxml.html
from time import sleep
import os
import uuid
import shutil

from selenium.webdriver import Chrome, ChromeOptions

options = ChromeOptions()            
options.add_argument('--headless')
driver = Chrome(options=options)
    
def request(url,render_js):
    
    html=""
    if render_js:
        driver.get(url)
        html = driver.page_source
    else:
        # 不具合の可能性あり
        html=urlopen(url).read()
    
    sleep(1)
    
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
    save_dir=config["save_dir"]
    render_js=config["render_js"] if "render_js" in config else 1

    shutil.rmtree(save_dir)
    #os.rmdir(save_dir)
    os.mkdir(save_dir)

    for url in starting_urls:
        
        while url!=ending_url:
            
            print("crowling...{0}".format(url))
            
            html=request(url,render_js)
            dom=lxml.html.fromstring(html)
            
            targets=[]
            if target_xpath=="":    
                path=os.path.join(root,"{0}/{1}.html".format(save_dir,uuid.uuid1()))
                with open(path,"w") as f:
                    f.write(html) # ファイル出力
                url=""
            else:
                targets=dom.xpath(target_xpath)
                
            for target in targets:
                url=urljoin(starting_urls[0],target)
                html=request(url,render_js)
                path=os.path.join(root,"{0}/{1}.html".format(save_dir,uuid.uuid1()))
                with open(path,"w") as f:
                    f.write(html) # ファイル出力
            
            if nextpage_xpath!="":
                nextpage=dom.xpath(nextpage_xpath)
                if len(nextpage)==0:
                    break
                else:
                    url=urljoin(starting_urls[0],nextpage[0])

    
if __name__ == '__main__':

    crowl("projects/support_devices/mvno/dmm/crowl.config")