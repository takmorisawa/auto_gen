import json
import pandas as pd
import difflib
#import saveFigure
import re

dic_carrier={}
dic_maker={}
dic_tether={}
dic_unlock={}
dic_sim={}
dic_type={}
dic_maker={}

def get_first(val,dic):
    return next(filter(lambda x:val in x[1], dic.items()), ("",""))[0]


def get_set(df_list,column):

    item_list=[]
    for df in [df for df in df_list if column in df.columns]:
        item_list.extend([t for t in df[column]])
    item_set=set(item_list)

    return item_set


def get_dict(df_master,df_list,column):

    master_set=get_set([df_master],column)
    dic={x:[] for x in master_set}

    item_set=get_set(df_list,column)
    for item in item_set:
        score_list=[[master,difflib.SequenceMatcher(None,item.upper(),master.upper()).ratio()] for master in master_set]
        best_match=max(score_list,key=lambda x:x[1])
        dic[best_match[0]].append(item)

    with open("dic_{0}.json".format(column),"w") as f:
        json.dump(dic,f,indent=4,ensure_ascii=False)

    return dic

def get_new(dic,item_list):

    dic_list=[]
    for vals in dic.values():
        dic_list.extend(vals)

    new_list=[item for item in item_list if not(item in dic_list)]
    print(new_list)


def conv_name(name):
    name=name.upper()
    name=name.replace(" ","")
    return name.replace("　","")


def get_best_match(target,target_model,df_master):

    # マスターのイテレート
    score_list=[]
    for idx,col in df_master.iterrows():

        # マッチング用に名前を変換
        target=conv_name(target)
        master=conv_name(col["name"])
        master_model=col["model"] if isinstance(col["model"],str) else ""

        # 類似度を算出
        scores=[]
        scores.append(difflib.SequenceMatcher(None,target,master).ratio()) # 名前のみ
        scores.append(difflib.SequenceMatcher(None,target+target_model,master+master_model).ratio()) # 名前とモデルの組み合わせ
        if col["maker"].upper() in master:
            master=master.replace(col["maker"].upper(),"").strip() # メーカー名を削除
            scores.append(difflib.SequenceMatcher(None,target,master).ratio()) # 名前のみ
            scores.append(difflib.SequenceMatcher(None,target+target_model,master+master_model).ratio()) # 名前とモデルの組み合わせ

        score_list.append([idx,max(scores)]) # 最大スコアを記録

    return max(score_list,key=lambda x:x[1]) if len(score_list)>0 else None


def cross_check():
    pass
    #check=False
    #cross_match=get_best_match(kk_name,df_mi[df_mi.carrier==mi_carrier])
    #check=mi_id==cross_match[0]


def match(df_master,df_target,file_path,error_path):

    print("matching...{0}".format(file_path))

    # カラムを作成する
    df_matched=pd.DataFrame()
    df_matched["name"]=pd.Series([],dtype="object")
    df_matched["model"]=pd.Series([],dtype="object")
    df_matched["carrier"]=pd.Series([],dtype="object")
    df_matched["master_id"]=pd.Series([],dtype="int32")
    df_matched["master_name"]=pd.Series([],dtype="object")
    df_matched["master_model"]=pd.Series([],dtype="object")
    df_matched["score"]=pd.Series([],dtype="float32")
    df_matched["match_names"]=pd.Series([],dtype="object")

    # エラー出力用データフレーム
    df_error=pd.DataFrame()

    # マッチング相手のイテレート
    for idx,row in df_target.iterrows():

        # 辞書からキャリア名称を取得
        carrier=next(filter(lambda x:row["carrier"] in x[1], dic_carrier.items()), ("",""))[0]
        # 辞書からメーカー名を取得
        maker=next(filter(lambda x:row["maker"] in x[1], dic_maker.items()), ("",""))[0]

        # キャリアとメーカーでフィルタ（空欄の場合はフィルタなし）
        df_tmp=df_master[df_master.carrier==carrier] if carrier!="" else df_master
        df_tmp=df_tmp[df_tmp.maker==maker] if maker!="" else df_tmp

        # ベストマッチを取得（id, score）
        target_model=row["model"] if "model" in row.index and isinstance(row["model"],str) else ""
        best_match=get_best_match(row["name"],target_model,df_tmp)

        if best_match:

            master_model=df_tmp.at[best_match[0],"model"] if isinstance(df_tmp.at[best_match[0],"model"],str) else ""

            series=pd.Series(
                [
                    row["name"],
                    target_model,
                    row["carrier"],
                    best_match[0],
                    df_tmp.at[best_match[0],"name"],
                    df_tmp.at[best_match[0],"model"],
                    best_match[1],
                    "{0}-{1}".format(conv_name(row["name"]),conv_name(df_tmp.at[best_match[0],"name"])+master_model)
                ],
                index=["name","model","carrier","master_id","master_name","master_model","score","match_names"])

            df_matched=df_matched.append(series,ignore_index=True)

        # マッチング失敗
        else:
            df_error=df_error.append(pd.Series([row["carrier"],row["maker"],row["name"]],index=["carrier","maker","name"]),ignore_index=True)
            #print("not found:{0},{1},{2}".format(row["carrier"],row["maker"],row["name"]))

    df_matched=df_matched.sort_values(by=["score"],ascending=False)
    df_matched.to_csv(file_path)
    df_error.to_csv(error_path)

    return df_matched


def match_to_dflist(df_master,df_list,name_list,out_dir):

    # カラムを作成
    df_itg=df_master.loc[:,["maker","carrier","model","name","price","release","size","sim_type","cpu","cpu_core","rom","ram","wait_time","battery"]]
    for name in name_list:
        df_itg["{0}_name".format(name)]=pd.Series(["-" for x in df_master.index],dtype="object")
        df_itg["{0}_tethering".format(name)]=pd.Series(["-" for x in df_master.index],dtype="object")
        df_itg["{0}_sim_lock".format(name)]=pd.Series(["-" for x in df_master.index],dtype="object")

    for name in name_list:
        df_itg["{0}_carrier".format(name)]=pd.Series(["" for _ in df_master.index],dtype="object")
        df_itg["{0}_score".format(name)]=pd.Series([0 for _ in df_master.index],dtype="float32")


    # mvnoリストのイテレート
    for (df,df_name) in zip(df_list,name_list):

        # マッチング
        df_matched=match(df_master,df,
             out_dir+"matching_{0}_to_kakaku.csv".format(df_name),
             out_dir+"error_{0}_to_kakaku.csv".format(df_name))
        # グラフ出力
        #saveFigure.saveFigure(df_matched["score"],"matching-{0}".format(df_name),out_dir+"report-{0}.png".format(df_name))

        # mvnoマッチング結果のイテレート
        for index,row in df_matched[df_matched.master_id>=0].iterrows():

            master_id=row["master_id"]
            ex_score=df_itg.at[master_id,"{0}_score".format(df_name)]

            # 既に登録されていデータのスコア確認
            model=row["model"] if isinstance(row["model"],str) else ""
            if row["score"]>ex_score:

                #df_itg.at[master_id,"{0}_id".format(df_name)]=index
                df_itg.at[master_id,"{0}_name".format(df_name)]=" ".join([row["name"],model])
                df_itg.at[master_id,"{0}_score".format(df_name)]=row["score"]
                df_itg.at[master_id,"{0}_sim_lock".format(df_name)]=df.at[index,"unlock"] if "unlock" in df.columns else "-"
                df_itg.at[master_id,"{0}_tethering".format(df_name)]=df.at[index,"tethering"] if "tethering" in df.columns else "-"
                df_itg.at[master_id,"{0}_carrier".format(df_name)]=row["carrier"]

            # 他にスコアの高いデータあり
            else:
                print("low score (than {2}):{0},{1}".format(row["name"],model,
                      df_itg.at[master_id,"{0}_name".format(df_name)]))

    df_itg=df_itg.round(2)
    df_itg=df_itg.sort_values(by=["maker","carrier","name"])
    df_itg.to_csv(out_dir+"matching_integrate.csv")


def joinMVNO(df_list,name_list,file_path):

    # 結合するためのデータフレームを準備する
    join_list=[]
    for df,mvno in zip(df_list,name_list):

        df=df.copy()
        df["mvno"]=mvno

        if not("model" in df.columns):
            df["model"]=""

        # nameからmodelを分離
        for idx,row in df.iterrows():
            if row["model"]=="":
                m=re.match("(.+) (.+)",row["name"])
                isModel=m and len(re.findall("[\d]",m.groups()[1]))>=2 and len(re.findall("[A-Z]",m.groups()[1]))>=2
                row["name"]=m.groups()[0].strip() if isModel else row["name"]
                row["model"]=m.groups()[1].strip() if isModel else row["model"]

        # 辞書を使用して表記揺を解消
        for column,dic in zip(
                ["device_type","tethering","carrier","unlock","sim","maker"],
                [dic_type,dic_tether,dic_carrier,dic_unlock,dic_sim,dic_maker]):
            df[column]=[get_first(x,dic) for x in df[column]] if column in df.columns else ""

        # sim1とsim2を結合（辞書を使用して表記揺れを解消）
        if "sim1" in df.columns and "sim2" in df.columns:
            df["sim"]=["/".join([get_first(row["sim1"],dic_sim),get_first(row["sim2"],dic_sim)]) if row["sim2"]!="" else get_first(row["sim1"],dic_sim) for idx,row in df.iterrows()]

        df=df.rename(columns={"device_type":"type"})
        join_list.append(df.loc[:,["mvno","type","maker","name","model","sim","carrier","tethering","unlock"]])

    df_join=pd.concat(join_list) # 結合
    df_join.to_csv(file_path,index=False) # 書き出し


if __name__ == '__main__':

  pass
