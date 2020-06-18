import json
import lxml.html
import sys
import os
import pandas as pd
import logging.config

class Scraper:
    def __init__(self,root,config_file_path):

        self.root=root

        logging.config.fileConfig(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "logging.conf"))
        self.logger=logging.getLogger()

        self.df=pd.DataFrame()

        # 設定ファイルを読み込む
        config={}
        with open(os.path.join(root,config_file_path),"r") as f:
            config=json.load(f)

        self.column_xpath=config["column_xpath"] if "column_xpath" in config else None
        self.targets_xpath=config["targets_xpath"]
        self.title_list_xpath=config["header_tag_xpath"] if "header_tag_xpath" in config else None
        self.value_list_xpath=config["data_tag_xpath"] if "data_tag_xpath" in config else None
        self.writefile_path=os.path.join(root,config["writefile_path"])

    def scrape_direct(self,target,series,column_xpath):

        # 各カラムに対応するXpathで探索して結果を保存する
        for cx in column_xpath if column_xpath!=None else []:
            series[cx[0]]=target.xpath(cx[1])

    def scrape_by_list(self,target,series,title_list_xpath,value_list_xpath):

        for th,td in zip(
            target.xpath(title_list_xpath),
            target.xpath(value_list_xpath)) if title_list_xpath!=None else []:

            title="/".join(th.xpath(".//text()")).strip()
            value="/".join(td.xpath(".//text()")).strip()

            if title!="":
                series[title]=value

    def execute(self,dom):

        # 行に対応するXpathで探索してイテレート
        for target in dom.xpath(self.targets_xpath):
            series=pd.Series()
            self.scrape_direct(target,series,self.column_xpath)
            self.scrape_by_list(target,series,self.title_list_xpath,self.value_list_xpath)
            self.df=self.df.append(series,ignore_index=True)

    def write(self):

        # ディレクトリを作成
        write_dir=os.path.dirname(self.writefile_path)
        if os.path.exists(write_dir)==False:
            os.mkdir(write_dir)

        # ファイル出力する
        self.df.index.name="id"
        self.df.to_csv(self.writefile_path)


def scrape(root,config_file_path):

    scraper=Scraper(root,config_file_path)

    # 設定ファイルを読み込む
    config={}
    with open(os.path.join(root,config_file_path),"r") as f:
        config=json.load(f)
    html_files=os.path.join(root,config["html_files"])


    # 指定ディレクトリからHTMLファイルを取得する
    files = os.listdir(html_files)
    files.sort()
    for file in [_ for _ in files if os.path.splitext(_)[1]==".html"]:

        path=html_files+"/"+file
        #self.logger.info("scraping...{0}".format(path))

        # htmlファイルを開く
        html=""
        with open(os.path.join(root,path)) as f:
            html=f.read()

        # Documentオブジェクト
        dom=lxml.html.fromstring(html)
        scraper.execute(dom)

    scraper.write()


if __name__ == '__main__':

    args=sys.argv
    root_dir=args[1]
    config_dir=args[2]
    scrape(root_dir,config_dir)
