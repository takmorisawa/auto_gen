import pandas as pd
import os
import re

def postprocess():

    current_dir=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(current_dir))
    
    df=pd.read_csv(os.path.join(current_dir,"current/csv/devices_dmm-scraped.csv"),index_col=0)
    df=df.rename(columns={'メーカー':"maker", '種別':"device_type", '端末':"name", 'LTE':"data", 'SIMカードサイズ':"sim1", 
                  'テザリング':"tethering", 'アンテナピクト表示':"pict", '音声通話':"call",'動作確認時のバージョン':"os", '備考':"note"})
    df=df.fillna("")
    df_edited=pd.DataFrame()


    for idx,row in df.iterrows():
        
        row["note"]=row["note"].replace("\n","")
        m=re.match(".*※(.+版)はSIMロックの解除が必要です。.*",row["note"])        
        unlocks=re.findall("[^、]+版",m.groups()[0]) if m else []

        # simを分離
        m=re.match("(.+)\t(.+)",row["sim1"])
        row["sim1"]=m.groups()[0] if m else row["sim1"]
        row["sim2"]=m.groups()[1] if m else ""
        
        # carrierを分割
        m=re.findall("[^/]+版",row["name"].split(" ")[-1])
        row["name"]=" ".join(row["name"].split(" ")[0:-1]) if len(m)>0 else row["name"]
        
        # 行を追加する
        carriers=m if len(m)>0 else [""]
        for carrier in carriers:
            row=row.copy()
            row["carrier"]=carrier
            row["unlock"]="必要" if carrier in unlocks else ""
            df_edited=df_edited.append(row,ignore_index=True)
            

    df_edited.index.name="id"      
    df_edited.to_csv(os.path.join(current_dir,"current/csv/devices_dmm-scraped-edited.csv"))


if __name__ == '__main__':

    postprocess()
