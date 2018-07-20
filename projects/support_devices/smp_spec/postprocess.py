import pandas as pd
import os
import re

def postprocess():

    current_dir=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(current_dir))
    
    df=pd.read_csv(os.path.join(current_dir,"csv/smp_spec-scraped.csv"),index_col=0)
    df_edited=pd.DataFrame()
    
    print(df.columns)

    for idx,col in df.iterrows():
         
        m=re.match("(.+)\t(.+)\t.*",col["製品名_製品名"])
        col["maker"]=m.groups()[0].strip() if m else ""
        col["name"]=m.groups()[1].strip() if m else ""
        
        col=col.drop("チェックをいれてクリック_チェックをいれてクリック")
        col=col.drop("チェックをいれてクリック_チェックをいれてクリック.1")
        col=col.drop("製品名_製品名")
        df_edited=df_edited.append(col,ignore_index=True)

    df_edited.to_csv(os.path.join(current_dir,"csv/smp_spec-scraped-edited.csv"))


if __name__ == '__main__':

    postprocess()
