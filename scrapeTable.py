import json
import lxml.html
import os
import numpy as np
import pandas as pd

"""
config

html_files
header_xpath
extra_xpath
tables_xpath
writefile_path
header_size
"""

def fillCells(df, td, irow):
    
    icol=np.where(df.iloc[irow,:].values==None)[0][0]
    
    rspan=td.xpath("normalize-space(./@rowspan)")
    rspan=int(rspan) if rspan!="" else 1
    
    cspan=td.xpath("normalize-space(./@colspan)")
    cspan=int(cspan) if cspan!="" else 1
    
    df.iloc[irow:irow+rspan,icol:icol+cspan]="\t".join(td.xpath(".//text()"))


def table2df(table,header_xpath,header_size,extra_cols):
    
    # theadを使用しない場合を考慮
    #ths=table.xpath("./thead//th | ./tbody/tr[1][not(./td)]/th")
    ths=table.xpath(header_xpath)
    trs=table.xpath("./tbody/tr[./td]")
    
    cols=["".join(th.xpath(".//text()")) for th in ths]
    
    # ヘッダが複数行にわたる場合
    if header_size[0]>0:
        htrs=table.xpath("./tbody/tr[./th]") # ヘッダ行
        df_col=pd.DataFrame(np.full((header_size[0], header_size[1]),None))
        for tr,irow in zip(htrs,range(header_size[0])):
            for td in tr.xpath("./th"):
                fillCells(df_col,td,irow)
        cols=["_".join(item) for idx, item in df_col.iteritems()]
    
    # 先にテーブルの必要な領域を確保
    df=pd.DataFrame(np.full((len(trs),len(cols)),None),columns=cols)
    
    # 追加用カラムを初期化
    for col in [item[0] for item in extra_cols]:
        df[col]=""
    
    for tr,irow in zip(trs,range(len(trs))): # 行のイテレート
        for td in tr.xpath("./th | ./td"): # 列のイテレート（ヘッダカラムを考慮）
            fillCells(df,td,irow)
        
        # 追加用カラムに値を入力
        for val in [item[1] for item in extra_cols]:
            df.iloc[irow,len(cols)]=tr.xpath(val)
            
    return df
            

def scrapeTable(config_file_path):

    # 設定ファイルに記述するパスは、このプログラムが置かれているディレクトリを基準とする
    root=os.path.dirname(os.path.abspath(__file__))
    
    # 設定ファイルを読み込む
    config={}
    with open(config_file_path,"r") as f:
        config=json.load(f)
    
    html_files=os.path.join(root,config["html_files"])
    header_xpath=config["header_xpath"]
    extra_cols=config["extra_cols"] if "extra_cols" in config else []
    tables_xpath=config["tables_xpath"]
    header_size=config["header_size"] if "header_size" in config else [0,0]
    writefile_path=os.path.join(root,config["writefile_path"])

    # デフォルト値を設定
    if header_xpath == "" : header_xpath="./thead//th | ./tbody/tr[1][not(./td)]/th"
    if tables_xpath == "" : tables_xpath="//table"

    # 指定ディレクトリからHTMLファイルを取得する
    df=pd.DataFrame()
    files = os.listdir(html_files)
    for file in [_ for _ in files if os.path.splitext(_)[1]==".html"]:
        
        path=html_files+"/"+file
        print("scraping...{0}".format(path))
        
        # htmlファイルを開く
        html=""
        with open(os.path.join(root,path)) as f:
            html=f.read()
        
        # Documentオブジェクト
        dom=lxml.html.fromstring(html)
        
        # 行に対応するXpathで探索してイテレート
        for table in dom.xpath(tables_xpath):
            
            df=df.append(table2df(table,header_xpath,header_size,extra_cols),ignore_index=True)

    # ディレクトリを作成
    write_dir=os.path.dirname(writefile_path)
    if os.path.exists(write_dir)==False:
        os.mkdir(write_dir)
        
    # ファイル出力する
    df.to_csv(writefile_path)
        
    
if __name__ == '__main__':

    scrapeTable("projects/support_devices/smp_spec/scrape.config")
