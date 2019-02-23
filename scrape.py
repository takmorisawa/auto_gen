import csv
import json
import lxml.html
import os

def scrape(root,config_file_path):

    # 設定ファイルに記述するパスは、このプログラムが置かれているディレクトリを基準とする
    #root=os.path.dirname(os.path.abspath(__file__))
    
    increment_no=0
    
    # 設定ファイルを読み込む
    config={}
    with open(os.path.join(root,config_file_path),"r") as f:
        config=json.load(f)
    
    html_files=os.path.join(root,config["html_files"])
    column_xpath=config["column_xpath"]
    targets_xpath=config["targets_xpath"]
    writefile_path=os.path.join(root,config["writefile_path"])
    
    # カラムを作成する
    rows=[["id"]] # インデックスのカラムを追加
    rows[0].extend([cx[0] for cx in column_xpath])
    # 指定ディレクトリからHTMLファイルを取得する
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
        for target in dom.xpath(targets_xpath):
            
            # インデックスを追加
            rows.append([increment_no])
            
            # 各カラムに対応するXpathで探索して結果を保存する
            rows[-1].extend([target.xpath(cx[1]) for cx in column_xpath])
            increment_no+=1
            
        # リストデータはタブ区切りの文字列に変換
        rows=[map(lambda x:"\t".join(x).strip() if isinstance(x,list) 
        else x.strip() if isinstance(x,str) 
        else x, row) for row in rows]
    
    # ディレクトリを作成
    write_dir=os.path.dirname(writefile_path)
    if os.path.exists(write_dir)==False:
        os.mkdir(write_dir)
    
    # ファイル出力する
    with open(writefile_path,"w") as f:
        writer=csv.writer(f, lineterminator='\r\n')
        writer.writerows(rows)
        
    
if __name__ == '__main__':

    scrape("/Users/tkyk/Documents/repo/supported_devices","/Users/tkyk/Documents/repo/supported_devices/mvno/nifmo/scrape.config")
