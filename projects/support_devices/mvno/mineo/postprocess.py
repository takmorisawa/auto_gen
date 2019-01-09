import pandas as pd
import os
import re

def postprocess():

    PLAN_NAME_DOCOMO=""
    PLAN_NAME_AU=""
    PLAN_NAME_SOFTBANK=""

    current_dir=os.path.dirname(os.path.abspath(__file__))
    print("processing...{0}".format(current_dir))

    df=pd.read_csv(os.path.join(current_dir,"current/csv/devices_mineo-scraped.csv"),index_col=0)
    df_edited=pd.DataFrame()
    dfA_edited=pd.DataFrame()
    dfS_edited=pd.DataFrame()

    for idx,col in df.iterrows():

        # キャリア情報からモデル名称を分離
        m=re.match("(.+)（(.+)）",col["carrier"])
        col["carrier"]=m.groups()[0].strip() if m else col["carrier"]
        col["model"]=m.groups()[1].strip() if m else ""

        # planの振り分け
        if col["plan"]=="Dプラン":
            df_edited=df_edited.append(col,ignore_index=True)
        elif col["plan"]=="Aプラン":
            dfA_edited=dfA_edited.append(col,ignore_index=True)
        elif col["plan"]=="Sプラン":
            dfS_edited=dfS_edited.append(col,ignore_index=True)

    df_edited.index.name="id"
    df_edited.to_csv(os.path.join(current_dir,"current/csv/devices_mineoD-scraped-edited.csv"))
    dfA_edited.index.name="id"
    dfA_edited.to_csv(os.path.join(current_dir,"current/csv/devices_mineoA-scraped-edited.csv"))
    dfS_edited.index.name="id"
    dfS_edited.to_csv(os.path.join(current_dir,"current/csv/devices_mineoS-scraped-edited.csv"))

if __name__ == '__main__':

    postprocess()
