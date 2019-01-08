import pandas as pd
import os
import re

def postprocess():

    PLAN_NAME_DOCOMO="ドコモ"
    PLAN_NAME_AU="au"
    TETHERING_COLUMNS={PLAN_NAME_DOCOMO:"tethering_d",PLAN_NAME_AU:"tethering_a"}
    
    root=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(root))
    
    df=pd.read_csv(os.path.join(root,"current/csv/devices_rakuten-scraped.csv"),index_col=0)
    dfD_edited=pd.DataFrame()
    dfA_edited=pd.DataFrame()
    dicPlanToDf={PLAN_NAME_DOCOMO:dfD_edited,PLAN_NAME_AU:dfA_edited}
    
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
        m=re.match("(.*)[／/](.*)",col["carrier"])
        for plan in plans:
            if m:
                col["carrier"]=m.groups()[0].strip()
                dicPlanToDf[plan]=dicPlanToDf[plan].append(col.copy(),ignore_index=True)
                col["carrier"]=m.groups()[1].strip()
                dicPlanToDf[plan]=dicPlanToDf[plan].append(col.copy(),ignore_index=True)
            else:
                dicPlanToDf[plan]=dicPlanToDf[plan].append(col,ignore_index=True)
    
    for plan in [PLAN_NAME_DOCOMO,PLAN_NAME_AU]:
        dicPlanToDf[plan].index.name="id"
        # tetheringの編集
        tether_rename=[tether[1] for tether in TETHERING_COLUMNS.items() if tether[0]==plan][0]
        tether_drop=[tether[1] for tether in TETHERING_COLUMNS.items() if tether[0]!=plan][0]
        dicPlanToDf[plan]=dicPlanToDf[plan].rename(columns={tether_rename:"tethering"})
        dicPlanToDf[plan]=dicPlanToDf[plan].drop(tether_drop,axis=1)

    # ファイル保存    
    dicPlanToDf[PLAN_NAME_DOCOMO].to_csv(os.path.join(root,"current/csv/devices_rakutenD-scraped-edited.csv"))
    dicPlanToDf[PLAN_NAME_AU].to_csv(os.path.join(root,"current/csv/devices_rakutenA-scraped-edited.csv"))
    

if __name__ == '__main__':

    postprocess()
