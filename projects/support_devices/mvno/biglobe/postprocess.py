import pandas as pd
import os
import re

def postprocess():

    current_dir=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(current_dir))
    
    df=pd.read_csv(os.path.join(current_dir,"current/csv/devices_biglobe-scraped.csv"),index_col=0)
    df_edited=pd.DataFrame()
    dfA_edited=pd.DataFrame()
    

    # 対象をスマートフォンに限る
    for idx,col in df.iterrows():

        col["org_name"]=col["name"]
        
        # モデル名称を抽出
        m=re.match("(.*)[\(|（](.*)[\)|）]",col["name"]) # モデル名称にマッチ
        col["name"]=m.groups()[0].strip() if m else col["name"]
        model=m.groups()[1].strip() if m else ""
        
        # carrier, model
        m=re.match("(.+販売).*",model)
        col["carrier"]=m.groups()[0] if m else ""
        m=re.match("(SIMロックフリー版).*",model)
        col["carrier"]=m.groups()[0] if m else col["carrier"]
        m=re.match(".*モデル(.+)",model)
        col["model"]=m.groups()[0] if m else ""      

        # carrier
        m=re.match("(BIGLOBE販売)(.+)",col["device_type"])
        col["carrier"]=m.groups()[0].strip() if m else col["carrier"]
        col["device_type"]=m.groups()[1].strip() if m else col["device_type"]
        
        services=col["func"].split("\t")
        col["call"]="◯" if "音声通話" in services else ""
        #col["sms"]="◯" if "SMS" in services else ""
        col["data"]="◯" if "データ通信" in services else ""
 
        # simの分割
        m=re.match("(.+), (.+)",col["sim"])
        col["sim1"]=m.groups()[0].strip() if m else col["sim"]
        col["sim2"]=m.groups()[1].strip() if m else ""
        col=col.drop("sim")
        
        # プランの振り分け
        if "タイプD" in col["plan"]:
            df_edited=df_edited.append(col,ignore_index=True)
        if "タイプA" in col["plan"]:
            dfA_edited=dfA_edited.append(col,ignore_index=True)
    
    # カラムの並び替え
    #df_edited=df_edited.loc[:,['device_type', 'carrier', 'maker', 'name', 'model' 'os', 'sim', 'plan', 'LTE/3G', 'call', 'data', 'tethering', 'note']]
    
    df_edited.index.name="id"
    df_edited.to_csv(os.path.join(current_dir,"current/csv/devices_biglobeD-scraped-edited.csv"))

    dfA_edited.index.name="id"
    dfA_edited.to_csv(os.path.join(current_dir,"current/csv/devices_biglobeA-scraped-edited.csv"))


if __name__ == '__main__':

    postprocess()
