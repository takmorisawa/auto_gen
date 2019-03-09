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
"""

def fill_cells(df, td, irow):

    # 指定行で値がNodeである列を検索する
    #cols=np.where(df.iloc[irow,:].values==None)
    cols=np.where(df[irow,:]==None)
    icol=cols[0][0]

    str_rspan=td.xpath("normalize-space(./@rowspan)")
    rspan=int(str_rspan) if str_rspan!="" else 1

    str_cspan=td.xpath("normalize-space(./@colspan)")
    cspan=int(str_cspan) if str_cspan!="" else 1

    # 指定範囲のセルを埋める
    df[irow:irow+rspan,icol:icol+cspan]="\t".join(td.xpath(".//text()"))


def rows_to_array(tag_rows):

    col_xpath="./th | ./td"

    # 行数を計算
    rows=len(tag_rows)

    # 列数を計算
    colspan_list=[th.xpath("./@colspan") for th in tag_rows[0].xpath(col_xpath)]
    cols=sum([int(span[0]) if len(span)>0 else 1 for span in colspan_list])

    # 配列を作成
    array=np.full((rows, cols),None)

    for tr,irow in zip(tag_rows,range(rows)):
        for col in tr.xpath(col_xpath):
            fill_cells(array,col,irow)

    return array


def table_to_df(table,header_xpath,extra_cols):

    # ヘッダ行を検索
    htrs=table.xpath(header_xpath) # ヘッダ行
    tmp_header=rows_to_array(htrs)
    # ヘッダを１行に連結
    header=["_".join(item) for item in tmp_header.transpose()]

    # データ行を検索
    trs=table.xpath("./tbody/tr[./td]")
    data=rows_to_array(trs)

    # DataFrameを作成
    df=pd.DataFrame(data,columns=header)

    # 追加用カラムを初期化
    for col in [item[0] for item in extra_cols]:
        df[col]=""

     # 追加用カラムに値を設定
    for tr,irow in zip(trs,range(len(trs))):
        df.iloc[irow,len(header):]=[tr.xpath(item[1]) for item in extra_cols]

    return df


def scrape_table(root,config_file_path):

    # 設定ファイルを読み込む
    config={}
    with open(os.path.join(root,config_file_path),"r") as f:
        config=json.load(f)

    html_files=os.path.join(root,config["html_files"])
    header_xpath=config["header_xpath"]
    extra_cols=config["extra_cols"] if "extra_cols" in config else []
    tables_xpath=config["tables_xpath"]
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
            df=df.append(table_to_df(table,header_xpath,extra_cols),ignore_index=True)

    # ディレクトリを作成
    write_dir=os.path.dirname(os.path.join(root,writefile_path))
    if os.path.exists(write_dir)==False:
        os.mkdir(write_dir)

    # ファイル出力する
    df.to_csv(writefile_path)


if __name__ == '__main__':

    scrape_table("/Users/tkyk/Documents/repo/smp_spec",
                "scrape.config")
