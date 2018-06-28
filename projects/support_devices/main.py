import sys
import os
import threading
import json
import pandas as pd

sys.path.append("../../")
import scrape
import crowl
import diff
import match
import backup

import mvno.ymobile.postprocess as yp
import mvno.biglobe.postprocess as bp
import mvno.uq.postprocess as up
import mvno.mineo.postprocess as mp
import mvno.linemobile.postprocess as lp
import mvno.ocn.postprocess as op
import mvno.rakuten.postprocess as rp
import mvno.iij.postprocess as ip
import mvno.qt.postprocess as qp


pipelines={
    "ymobile":[
        lambda x:scrape.scrape("mvno/{0}/scrape.config".format(tid)),
        lambda x:yp.postprocess()],
    "biglobe":[
        lambda x:scrape.scrape("{0}/scrape.config".format(tid)),
        lambda x:bp.postprocess()],
    "uq":[
        lambda x:scrape.scrape("{0}/scrape.config".format(tid)),
        lambda x:up.postprocess()],
    "mineo":[
        lambda x:scrape.scrape("{0}/scrape.config".format(tid)),
        lambda x:mp.postprocess()],
    "linemobile":[
        lambda x:scrape.scrape("{0}/scrape.config".format(tid)),
        lambda x:lp.postprocess()],
    "ocn":[
        lambda x:scrape.scrape("{0}/scrape.config".format(tid)),
        lambda x:op.postprocess()],
    "rakuten":[
        lambda x:scrape.scrape("{0}/scrape.config".format(tid)),
        lambda x:rp.postprocess()],
    "iij":[
        lambda x:scrape.scrape("{0}/scrape.config".format(tid)),
        lambda x:ip.postprocess()],
    "qt":[
        lambda x:scrape.scrape("{0}/scrape.config".format(tid)),
        lambda x:scrape.scrape("{0}/scrape_mk.config".format(tid)),
        lambda x:qp.postprocess()]
}

def execute_unit(tid,pipeline,results):

    for f in pipeline:
    #try:
        results[tid]=f(tid)
    #except:
    #    results[tid]=False
    #    print("except:{0},{1}".format(tid,f))
    #    traceback.print_exc() # トレースバック
    #finally:
        #各ステージの処理でFalseを返したら以降のパイプラン処理をキャンセルする
        if results[tid]==False:
            return False
           
    return True # 全プロセス正常終了

def test():
    return True

if __name__=="__main__":

    root=os.path.dirname(os.path.abspath(__file__))
    
    pipelines_test={
        "ymobile":[
            lambda x:crowl.crowl("mvno/{0}/crowl.config".format(tid)),
            lambda x:scrape.scrape("mvno/{0}/scrape.config".format(tid)),
            lambda x:diff.diff(
                    "projects/support_devices/mvno/{0}/tmp/csv/devices_{0}-scraped.csv".format(tid),
                    "projects/support_devices/mvno/{0}/current/csv/devices_{0}-scraped.csv".format(tid),
                    "projects/support_devices/mvno/{0}/tmp".format(tid)),
            lambda x:backup.backup(
                    "projects/support_devices/mvno/{0}/tmp".format(tid),
                    "projects/support_devices/mvno/{0}/current".format(tid)),
            lambda x:yp.postprocess()]
        }
    
    # 単体処理をマルチスレッドで実行
    results={}
    t_list=[]
    for tid,pipeline in pipelines_test.items():
        t_list.append(threading.Thread(target=execute_unit,args=[tid,pipeline,results]))
        t_list[-1].start()
        pass
        
    for t in t_list:
        t.join()
    
    print(results)
    
    # 複合処理
        
    df_master=pd.read_csv("kakaku/csv/devices_kakaku-scraped-edited.csv",index_col=0) 
    df_list=[pd.read_csv(file_path,index_col=0).fillna("") for file_path in 
             [
                "mvno/mineo/csv/devices_mineoD-scraped-edited.csv",
                "mvno/mineo/csv/devices_mineoA-scraped-edited.csv",
                "mvno/uq/csv/devices_uq-scraped-edited.csv",
                "mvno/ymobile/current/csv/devices_ymobile-scraped-edited.csv",
                "mvno/rakuten/csv/devices_rakuten-scraped-edited.csv",
                "mvno/ocn/csv/devices_ocn-scraped-edited.csv",
                "mvno/iij/csv/devices_iijD-scraped-edited.csv",
                "mvno/iij/csv/devices_iijA-scraped-edited.csv",
                "mvno/linemobile/csv/devices_linemobile-scraped-edited.csv",
                "mvno/biglobe/csv/devices_biglobeD-scraped-edited.csv",
                "mvno/biglobe/csv/devices_biglobeA-scraped-edited.csv",
                "mvno/qt/csv/devices_qtD-scraped-edited.csv",
                "mvno/qt/csv/devices_qtA-scraped-edited.csv",
                "mvno/qt/csv/devices_qtS-scraped-edited.csv",
                "mvno/dmm/csv/devices_dmm-scraped-edited.csv",
                "mvno/nifmo/csv/devices_nifmo-scraped-edited.csv"
            ]]
    name_list=["mineo_d","mineo_a","uq","ymobile","rakuten","ocn","IIJmio_d","IIJmio_a","linemobile",
               "biglobe_d","biglobe_a","qt_d","qt_a","qt_s","dmm","nifmo"]

    # 辞書を入力
    with open("dic/dic_carrier.json","r",encoding="utf-8") as f:
        match.dic_carrier=json.load(f)   
    with open("dic/dic_maker.json","r",encoding="utf-8") as f:
        match.dic_maker=json.load(f)    
    with open("dic/dic_tethering.json","r",encoding="utf-8") as f:
        match.dic_tether=json.load(f)
    with open("dic/dic_unlock.json","r",encoding="utf-8") as f:
        match.dic_unlock=json.load(f)
    with open("dic/dic_sim.json","r",encoding="utf-8") as f:
        match.dic_sim=json.load(f)
    with open("dic/dic_type.json","r",encoding="utf-8") as f:
        match.dic_type=json.load(f)
        
    # 新規項目を確認
    for column, dic in zip(
            ["carrier","maker","tethering","sim","unlock","device_type"],
            [match.dic_carrier,match.dic_maker,match.dic_tether,match.dic_sim,match.dic_unlock,match.dic_type]):
        print("\n{0}初登場：".format(column))
        item_set=match.get_set(df_list[0:3],column)
        match.get_new(dic,item_set)
        
    # 表記揺れ解消
    for df in df_list:
        df["device_type"]=[match.get_first(t,match.dic_type) for t in df["device_type"]]
        
    # 保存
    for df,name in zip(df_list,name_list):
        df.to_csv(os.path.join(root,"csv/mvno/devices_{0}.csv").format(name))

    #for df,name in zip(df_list,name_list):
    #    print(name)
    #    print(df.columns)
 
    #print(df_list[0].head())
       
    # マッチング
    #match.match_to_dflist(df_master,df_list,name_list,"csv/")
    
    # 連結
    match.joinMVNO(df_list,name_list,"csv/mvno_join.csv")

    # 辞書作成
    #dic=match.get_dict(df_list[4],df_list,"device_type")
    