import pandas as pd
import os
import re

def postprocess():

    root=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(root))
    
    df=pd.read_csv(os.path.join(root,"current/csv/devices_qt-scraped.csv"),index_col=0)
    df=df.fillna("")
    
    dfD_edited=pd.DataFrame()
    dfA_edited=pd.DataFrame()
    dfS_edited=pd.DataFrame()
    
    df_mk=pd.read_csv(os.path.join(root,"current/csv/devices_qtmk-scraped.csv"),index_col=0)
    
    for idx,col in df.iterrows():

        col["name"]=col["name"].replace("\n","")
        
        #device smp mk015 dv0068
        m=re.match(".+ (.+) (mk\d+).+",col["type_maker"])
        if m:
            col["device_type"]=m.groups()[0].strip()
            key=m.groups()[1].strip()
            col["maker"]=df_mk[[mkrow["plan"]==col["plan"] and mkrow["key"]==key for mkidx,mkrow in df_mk.iterrows()]].iat[0,2].strip()
        
        if col["device_type"]=="oth":
            m=re.match("(.+)\t(.+)",col["name"])
            col["device_type"]=m.groups()[0].strip() if m else col["device_type"]
            col["name"]=m.groups()[1].strip() if m else col["name"]
            
        m=re.match("(.+)\t(.+版)",col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        col["carrier"]=m.groups()[1].strip() if m else ""
        
        m=re.match("(.+)\t(.+)",col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        col["model"]=m.groups()[1].strip() if m else ""
        
        col["name"]=col["name"].replace("\t","")
        
        if col["plan"]=="Sタイプ": dfS_edited=dfS_edited.append(col,ignore_index=True)
        if col["plan"]=="Dタイプ": dfD_edited=dfD_edited.append(col,ignore_index=True)
        if col["plan"]=="Aタイプ": dfA_edited=dfA_edited.append(col,ignore_index=True)
    
    dfD_edited.index.name="id"
    dfD_edited.to_csv(os.path.join(root,"current/csv/devices_qtD-scraped-edited.csv"))
    dfA_edited.index.name="id"
    dfA_edited.to_csv(os.path.join(root,"current/csv/devices_qtA-scraped-edited.csv"))
    dfS_edited.index.name="id"
    dfS_edited.to_csv(os.path.join(root,"current/csv/devices_qtS-scraped-edited.csv"))
    

if __name__ == '__main__':

    postprocess()
