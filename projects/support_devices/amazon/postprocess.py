import pandas as pd
import os
import collections
import re
import numpy as np

def postprocess():

    current_dir=os.path.dirname(os.path.abspath(__file__))
    
    df=pd.read_csv(os.path.join(current_dir,"csv/amazon-scraped.csv"),index_col=0)
    df=df.fillna("")
    df_edited=pd.DataFrame()
      
    #print(makers.makers)
    
    for idx,row in df.iterrows():
        
        row["price"]=row["price"].split("\t")[0]
        row["state"]=row["state"].split("\t")[0]
        
        # 中古品でなく、かつメーカーが不明や空白でない
        if row["state"]!="中古品" and not(row["maker"] in ["不明","","ゼタコム株式会社"]):
            df_edited=df_edited.append(row,ignore_index=True)
    
    c=collections.Counter(df_edited["maker"])
    makers=[item[0] for item in c.most_common(50)]
    print(c.most_common(50))
    df_edited=df_edited[[(maker in makers) for maker in df_edited["maker"]]]
    
    df_edited=df_edited[["maker","name","price","state"]]
    df_edited.to_csv(os.path.join(current_dir,"csv/amazon-scraped-edited.csv"))


if __name__ == '__main__':

    postprocess()
