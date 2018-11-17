import pandas as pd
import os
import re

def postprocess():

    root=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(root))
    
    df=pd.read_csv(os.path.join(root,"tmp/csv/devices_rakuten-scraped.csv"),index_col=0)
    dfD_edited=pd.DataFrame()
    dfA_edited=pd.DataFrame()
    dicPlanToDf={"ドコモ":dfD_edited,"au":dfA_edited}
    
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
    
        # plan
        m=re.match("(.+)/(.+)",col["plan"])
        plans=m.groups() if m else [col["plan"]]

        # carrierを分割
        m=re.match("(.*)／(.*)",col["carrier"])
        for plan in plans:
            if m:
                col["carrier"]=m.groups()[0].strip()
                dicPlanToDf[plan]=dicPlanToDf[plan].append(col.copy(),ignore_index=True)
                col["carrier"]=m.groups()[1].strip()
                dicPlanToDf[plan]=dicPlanToDf[plan].append(col.copy(),ignore_index=True)
            else:
                dicPlanToDf[plan]=dicPlanToDf[plan].append(col,ignore_index=True)
    
    dicPlanToDf["ドコモ"].index.name="id"
    dicPlanToDf["ドコモ"].to_csv(os.path.join(root,"tmp/csv/devices_rakutenD-scraped-edited.csv"))
    dicPlanToDf["au"].index.name="id"
    dicPlanToDf["au"].to_csv(os.path.join(root,"tmp/csv/devices_rakutenA-scraped-edited.csv"))
    

if __name__ == '__main__':

    postprocess()
