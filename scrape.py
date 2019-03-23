import json
import lxml.html
import os
import pandas as pd
import logging.config

def scrape_direct(target,series,column_xpath):

    # 各カラムに対応するXpathで探索して結果を保存する
    for cx in column_xpath if column_xpath!=None else []:
        series[cx[0]]=target.xpath(cx[1])

def scrape_by_list(target,series,title_list_xpath,value_list_xpath):

    for th,td in zip(
        target.xpath(title_list_xpath),
        target.xpath(value_list_xpath)) if title_list_xpath!=None else []:

        title="/".join(th.xpath(".//text()")).strip()
        value="/".join(td.xpath(".//text()")).strip()

        if title!="":
            series[title]=value

def scrape(root,config_file_path):

    logging.config.fileConfig(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "logging.conf"))
    logger=logging.getLogger()

    df=pd.DataFrame()

    # 設定ファイルを読み込む
    config={}
    with open(os.path.join(root,config_file_path),"r") as f:
        config=json.load(f)

    html_files=os.path.join(root,config["html_files"])
    column_xpath=config["column_xpath"] if "column_xpath" in config else None
    targets_xpath=config["targets_xpath"]
    title_list_xpath=config["header_tag_xpath"] if "header_tag_xpath" in config else None
    value_list_xpath=config["data_tag_xpath"] if "data_tag_xpath" in config else None
    writefile_path=os.path.join(root,config["writefile_path"])

    # 指定ディレクトリからHTMLファイルを取得する
    files = os.listdir(html_files)
    for file in [_ for _ in files if os.path.splitext(_)[1]==".html"]:

        path=html_files+"/"+file
        logger.info("scraping...{0}".format(path))

        # htmlファイルを開く
        html=""
        with open(os.path.join(root,path)) as f:
            html=f.read()

        # Documentオブジェクト
        dom=lxml.html.fromstring(html)

        # 行に対応するXpathで探索してイテレート
        for target in dom.xpath(targets_xpath):
            series=pd.Series()
            scrape_direct(target,series,column_xpath)
            scrape_by_list(target,series,title_list_xpath,value_list_xpath)
            df=df.append(series,ignore_index=True)

    # ディレクトリを作成
    write_dir=os.path.dirname(writefile_path)
    if os.path.exists(write_dir)==False:
        os.mkdir(write_dir)

    # ファイル出力する
    df.index.name="id"
    df.to_csv(writefile_path)


if __name__ == '__main__':

    root="/Users/tkyk/Documents/repo/wifi_spec"
    scrape(root,"service/uq/scrape.config")
