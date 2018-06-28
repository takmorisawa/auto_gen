import pandas as pd
import os
import re

def postprocess():

    current_dir=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(current_dir))
    
    df=pd.read_csv(os.path.join(current_dir,"current/csv/devices_uq-scraped.csv"),index_col=0)
    df_edited=pd.DataFrame()

    for idx,col in df.iterrows():
    
        col["org_name"]=col["name"]
        
        # モデル名称を抽出
        m=re.match("(.+)[¥(|（](.+)[¥)|）]",col["name"]) # モデル名称にマッチ
        col["model"]=m.groups()[1].strip() if m else ""
        col["name"]=m.groups()[0].strip() if m else col["name"]

        m=re.match("(.+)/(.+)",col["sim1"])
        col["sim1"]=m.groups()[0].strip() if m else col["sim1"]
        col["sim2"]=m.groups()[1].strip() if m else ""

        # 不要な注記を除去
        col["name"]=col["name"].replace("™","")
        col["name"]=col["name"].replace("®","")
        
        df_edited=df_edited.append(col,ignore_index=True)
    
    df_edited.index.name="id"      
    df_edited.to_csv(os.path.join(current_dir,"current/csv/devices_uq-scraped-edited.csv"))
    

if __name__ == '__main__':

    postprocess()
