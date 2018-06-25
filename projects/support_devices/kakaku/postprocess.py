import pandas as pd
import os
import re

def postprocess():

    current_dir=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(current_dir))
    
    df=pd.read_csv(os.path.join(current_dir,"csv/devices_kakaku-scraped.csv"),index_col=0)
    df=df.fillna("")
    #print(df.dtypes)
    print(df.columns)

    df_edited=pd.DataFrame()

    carrier_list=["SIMフリー","docomo","au","SoftBank","ワイモバイル","WILLCOM","イー・モバイル","ディズニー・モバイル"]
    
    
    for idx,col in df.iterrows():

        col["ord_name"]=col["name"]
        
        # name, GB, carrier
        ex="(.+) .*(\d+GB).* *({0})".format("|".join(carrier_list))
        m=re.match(ex,col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        col["rom"]=m.groups()[1].strip() if m and col["rom"]=="" else col["rom"]
        
        # name, carrier
        ex="(.+) *({0})".format("|".join(carrier_list))
        m=re.match(ex,col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        
        # ram
        m=re.match(".*RAM (\d+GB).*",col["ram"])
        col["ram"]=m.groups()[0] if m else ""
        
        # model分離（数字とアルファベットをそれぞれ２文字以上含むか）
        m=re.match("(.+)[ ](.+)",col["name"])        
        isModel=m and len(re.findall("[\d]",m.groups()[1]))>=2 and len(re.findall("[A-Z]",m.groups()[1]))>=2
        col["name"]=m.groups()[0].strip() if isModel else col["name"]
        col["model"]=m.groups()[1].strip() if isModel else ""

        m=re.match("(.+) 格安SIMを見る>",str(col["sim_type"]))
        col["sim_type"]=m.groups()[0].strip() if m else col["sim_type"]

        # ROMサイズ
        found=False
        if idx>0 and col["rom"]!="":
            df_tmp=df_edited[[row["carrier"]==col["carrier"] and row["name"]==col["name"] and row["model"]==col["model"] for idx,row in df_edited.iterrows()]]
            if df_tmp.shape[0]>0:
                # romのデータを連結
                df_edited.at[df_tmp.index[0],"rom"]+=", {0}".format(col["rom"])
                found=True
        
        if found==False:
            df_edited=df_edited.append(col,ignore_index=True)
    
    
    # nameだけで判別できない機種のnameをmodelと再連結する
    counts=[]
    for idx1,row1 in df_edited.iterrows():
        counts.append(df_edited[[row1["carrier"]==row2["carrier"] and row1["name"]==row2["name"] for idx1,row2 in df_edited.iterrows()]].shape[0])
    
    df_tmp=df_edited[[count>1 for count in counts]]
    for idx,row in df_tmp.iterrows():
        df_edited.at[idx,"name"]=" ".join([row["name"],row["model"]])
        df_edited.at[idx,"model"]=""


    # 最終チェック
    for idx1,row1 in df_edited.iterrows():
        df_tmp=df_edited[[row1["carrier"]==row2["carrier"] and row1["name"]==row2["name"] for idx2,row2 in df_edited.iterrows()]]
        if df_tmp.shape[0]>1:
            print(col["name"],col["model"])

    #df_edited=df_edited.loc[:,["maker","name","model","ord_name","price","rank","review","comment",
    #                           "regist_date","release_date","carrier","sim","os","display","ROM","battery"]]
    
    df_edited.index.name="id"
    df_edited.to_csv(os.path.join(current_dir,"csv/devices_kakaku-scraped-edited.csv"))

if __name__ == '__main__':

    postprocess()
