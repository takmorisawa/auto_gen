import pandas as pd
import os
import re

def postprocess():

    root=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(root))
    
    df=pd.read_csv(os.path.join(root,"current/csv/devices_rakuten-scraped.csv"),index_col=0)
    df_edited=pd.DataFrame()
        
    carrier_list=["SIMフリー","docomo","au","SoftBank","ワイモバイル","WILLCOM","イー・モバイル","ディズニー・モバイル"]
    
    for idx,col in df.iterrows():

        col["ord_name"]=col["name"]
    
        # モデル名称にマッチ
        m=re.match("(.*)[\(（](.*版)[\)）](.*)",col["name"])
        col["carrier"]=m.groups()[1].strip() if m else ""
        col["name"]=(m.groups()[0]+m.groups()[2]).strip() if m else col["name"]
    
        # モデル名称にマッチ
        m=re.match("(.*)[\(（](.*)[\)）]",col["name"])
        col["model"]=m.groups()[1].strip() if m else ""
        col["name"]=m.groups()[0].strip() if m else col["name"]

        # simの分割
        m=re.match("(.+)/(.+)",col["sim"])
        col["sim1"]=m.groups()[0].strip() if m else col["sim"]
        col["sim2"]=m.groups()[1].strip() if m else ""
        col=col.drop("sim")
        
        # カラムを追加
        col["org_id"]=idx
    
        # carrierを分割
        m=re.match("(.*)／(.*)",col["carrier"])
        if m:
            col["carrier"]=m.groups()[0].strip()
            df_edited=df_edited.append(col.copy(),ignore_index=True)
            col["carrier"]=m.groups()[1].strip()
            df_edited=df_edited.append(col.copy(),ignore_index=True)
        else:
            df_edited=df_edited.append(col,ignore_index=True)
    
    df_edited.index.name="id"
    df_edited.to_csv(os.path.join(root,"current/csv/devices_rakuten-scraped-edited.csv"))
    

if __name__ == '__main__':

    postprocess()
