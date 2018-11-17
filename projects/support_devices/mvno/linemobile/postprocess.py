import pandas as pd
import os
import re

def postprocess():

    current_dir=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(current_dir))
    
    df=pd.read_csv(os.path.join(current_dir,"current/csv/devices_linemobile-scraped.csv"),index_col=0)
    df=df.fillna("")
    df=df.rename(columns={"sim":"sim1"})
    dfD_edited=pd.DataFrame()
    dfS_edited=pd.DataFrame()
    
    dic_mark={
            "ExOk":"◯",
            "ExNg":"×"}
    
    for idx,col in df.iterrows():

        col["data"]=dic_mark[col["data"]]
        col["call"]=dic_mark[col["call"]]
        col["tethering"]=dic_mark[col["tethering"]]
    
        m=re.match(".*SIMロック解除が必要です。.*",col["note"])
        col["unlock"]="必要" if m else ""
        
        m=re.match("(.+) (.+版)",col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        col["carrier"]=m.groups()[1].strip() if m else ""
        
        m=re.match("(.+)/(.+)",col["sim1"])
        col["sim1"]=m.groups()[0] if m else col["sim1"]
        col["sim2"]=m.groups()[1] if m else ""
        
        # iPhone, iPad model
        m=re.match("(i.+) (A\d{4})",col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        col["model"]=m.groups()[1].strip() if m else ""
    
        if col["plan"]=="ドコモ回線":
            dfD_edited=dfD_edited.append(col,ignore_index=True)
        if col["plan"]=="ソフトバンク回線":
            dfS_edited=dfS_edited.append(col,ignore_index=True)
            
    dfD_edited.index.name="id"
    dfD_edited.to_csv(os.path.join(current_dir,"current/csv/devices_linemobileD-scraped-edited.csv"))
    dfS_edited.index.name="id"
    dfS_edited.to_csv(os.path.join(current_dir,"current/csv/devices_linemobileS-scraped-edited.csv"))
    

if __name__ == '__main__':

    postprocess()
