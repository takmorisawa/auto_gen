import pandas as pd
import os
import re

def postprocess():

    current_dir=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(current_dir))
    
    df=pd.read_csv(os.path.join(current_dir,"csv/devices_linemobile-scraped.csv"),index_col=0)
    df_edited=pd.DataFrame()
    #print(df.columns)
    
    dic_mark={
            "md38SAccoIcoCircle":"◯",
            "md38SAccoIcoCrose":"×"}
    
    dic_type={
            "md38TabCntWrap FnDevicePhone FnTabCont FnTabContactive":"スマートフォン",
            "md38TabCntWrap FnDeviceTablet FnTabCont":"タブレット"
            }
    
    for idx,col in df.iterrows():

        col["ord_name"]=col["name"]
        col["data"]=dic_mark[col["data"]]
        col["call"]=dic_mark[col["call"]]
        col["tethering"]=dic_mark[col["tethering"]]
    
        col["device_type"]=dic_type[col["device_type"]]
    
        m=re.match("(.+)（SIMロック解除が必要）",col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        col["unlock"]="必要" if m else ""
        
        m=re.match("(.+) (.+版)",col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        col["carrier"]=m.groups()[1].strip() if m else ""
    
        m=re.match("(.+)[\(（](.+)[\)）]",col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        col["model"]=m.groups()[1].strip() if m else ""
        
        m=re.match("(.+)/(.+)",col["sim1"])
        col["sim1"]=m.groups()[0].strip() if m else col["sim1"]
        col["sim2"]=m.groups()[1].strip() if m else ""
        
        # iPhone, iPad model
        m=re.match("(i.+) (A\d{4})",col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        col["model"]=m.groups()[1].strip() if m else col["model"]
    
        df_edited=df_edited.append(col,ignore_index=True)
    
    # カラムの並び替え
    #df_edited=df_edited.loc[:,["org_id","maker","carrier","name","model","org_name",
    #             "device_type","sim","3G/LTE","tethering","os","note"]]
    
    df_edited.index.name="id"
    df_edited.to_csv(os.path.join(current_dir,"csv/devices_linemobile-scraped-edited.csv"))
    

if __name__ == '__main__':

    postprocess()
