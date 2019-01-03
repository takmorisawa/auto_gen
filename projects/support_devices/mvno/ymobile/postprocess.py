import pandas as pd
import os
import re

def postprocess():

    current_dir=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(current_dir))
    
    df=pd.read_csv(os.path.join(current_dir,"current/csv/devices_ymobile-scraped.csv"),index_col=0)
    df_edited=pd.DataFrame()

    for idx,col in df.iterrows():
    
        col["org_name"]=col["name"]

        # 余分な文字を切り取る
        m=re.match(".*select_(.+)_contents.*",col["device_type"])
        col["device_type"]=m.groups()[0] if m else col["device_type"]

        # キャリアと備考にマッチ
        m=re.match("(.+)\t[\(（](.+)版[\)）]\t(.*)",col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        col["carrier"]=m.groups()[1].strip() if m else ""
        col["unlock"]=m.groups()[2].strip() if m else ""

        # キャリアのみにマッチ
        m=re.match("(.*)\t[\(（](.*)版[\)）]",col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        col["carrier"]=m.groups()[1].strip() if m else col["carrier"]
    
        # モデルにマッチ
        m=re.match("(.*)[\(（](.*)[\)）]",col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        col["model"]=m.groups()[1].strip() if m else ""
        
        # simの分割
        m=re.match("(.+)/(.+)",col["sim"])
        col["sim1"]=m.groups()[0].strip() if m else col["sim"]
        col["sim2"]=m.groups()[1].strip() if m else ""
        col=col.drop("sim")
        
        # 不要な注記を除去
        col["name"]=col["name"].replace("™","")
        col["name"]=col["name"].replace("®","")
        col["os"]=col["os"].replace("™","")
        
        # タブを置換
        col["name"]=col["name"].replace("\t"," ")
    
        # carrierを分割
        for carrier in col["carrier"].split("/"):
            col=col.copy()
            col["carrier"]=carrier
            df_edited=df_edited.append(col,ignore_index=True)

    # カラムの並び替え
    #df_edited=df_edited.loc[:,["device_type","maker","name","model","carrier","unlock","org_name","sim","os","note"]]
    
    df_edited.index.name="id"      
    df_edited.to_csv(os.path.join(current_dir,"current/csv/devices_ymobile-scraped-edited.csv"))


if __name__ == '__main__':

    postprocess()
