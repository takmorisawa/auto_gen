import pandas as pd
import os
import re

def postprocess():

    current_dir=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(current_dir))
    
    df=pd.read_csv(os.path.join(current_dir,"current/csv/devices_mineo-scraped.csv"),index_col=0)
    df_edited=pd.DataFrame()
    dfA_edited=pd.DataFrame()

    for idx,col in df.iterrows():
    
        col["org_name"]=col["name"]
        
        # 端末名称からモデル名称を分離
        m=re.match("(.+)【(.+)】",col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        col["model"]=m.groups()[1].strip() if m else ""
        
        # 余分な文字を切り取る
        m=re.match("([^ ]+).+",col["device_type"])
        col["device_type"]=m.groups()[0] if m else col["device_type"]
        
        # planの振り分け
        if col["plan"]=="ドコモプラン(Dプラン)":
            df_edited=df_edited.append(col,ignore_index=True)
        else:
            dfA_edited=dfA_edited.append(col,ignore_index=True)
    
    # カラムの並び替え
    #df_edited=df_edited.loc[:,["plan","device_type","carrier","maker","name","model","org_name","sim1","sim2","single","dual","tethering","sms","version","note"]]

    df_edited.index.name="id"      
    df_edited.to_csv(os.path.join(current_dir,"current/csv/devices_mineoD-scraped-edited.csv"))
    dfA_edited.index.name="id"      
    dfA_edited.to_csv(os.path.join(current_dir,"current/csv/devices_mineoA-scraped-edited.csv"))
    
if __name__ == '__main__':

    postprocess()
