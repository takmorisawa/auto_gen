import pandas as pd
import os
import re

def postprocess():

    current_dir=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(current_dir))
    
    df=pd.read_csv(os.path.join(current_dir,"current/csv/devices_iij-scraped.csv"),index_col=0)
    df_edited=pd.DataFrame()
    dfA_edited=pd.DataFrame()
    
    #carrier_list=["SIMフリー","docomo","au","SoftBank","ワイモバイル","WILLCOM","イー・モバイル","ディズニー・モバイル"]
    
    for idx,col in df.iterrows():

        # name, carrier
        m=re.match("(.+)\t(.+)",col["name"])
        col["name"]=m.groups()[0] if m else col["name"]
        carrier_list=m.groups()[1].split("/") if m else []

        m=re.match("(.+) (.+版)",col["name"])
        col["name"]=m.groups()[0] if m else col["name"]
        carrier_list=m.groups()[1].split("/") if m else carrier_list

        # ※暫定対応、IIJで言うSIMフリーは定義が曖昧なため
        if len(carrier_list)==1 and carrier_list[0]=="SIMフリー版":
            carrier_list[0]=""

        # plan
        m=re.match(".+(type[ad]).+",col["plan"])
        col["plan"]=m.groups()[0] if m else col["plan"]
 
        # simの分割
        m=re.match("(.+)/(.+)",col["sim"])
        col["sim1"]=m.groups()[0].strip() if m else col["sim"]
        col["sim2"]=m.groups()[1].strip() if m else ""
        col=col.drop("sim")
        
        carrier_list = carrier_list if len(carrier_list)>0 else [col["carrier"]]
        for carrier in carrier_list:
            
            col["carrier"]=carrier
            # unlock
            m=re.match(".*SIMロックの解除が必要です.*",col["note"] if isinstance(col["note"],str) else "")
            col["unlock"]="必要" if m and carrier!="SIMフリー版" else ""                
            
            # planの振り分け
            if col["plan"]=="typed":
                df_edited=df_edited.append(col,ignore_index=True)
            else:
                dfA_edited=dfA_edited.append(col,ignore_index=True)
            
            
    df_edited.index.name="id"      
    df_edited.to_csv(os.path.join(current_dir,"current/csv/devices_iijD-scraped-edited.csv"))
    dfA_edited.index.name="id"      
    dfA_edited.to_csv(os.path.join(current_dir,"current/csv/devices_iijA-scraped-edited.csv"))
    

if __name__ == '__main__':

    postprocess()
