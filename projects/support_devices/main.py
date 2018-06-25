import sys
import os
import threading
import json
import pandas as pd

sys.path.append("../../")
import scrape
import match

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
        lambda x:scrape.scrape("{0}/scrape.config".format(tid)),
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
        try:
            results[tid]=f(tid)
        except:
            results[tid]=False
            print("except:{0},{1}".format(tid,f))
            traceback.print_exc() # トレースバック
        finally:
            if results[tid]==False:
                return
           
    return True # 全プロセス正常終了

if __name__=="__main__":

    # 単体処理をマルチスレッドで実行
    results={}
    t_list=[]
    for tid,pipeline in pipelines.items():
        #t_list.append(threading.Thread(target=execute_unit,args=[tid,pipeline,results]))
        #t_list[-1].start()
        pass
        
    for t in t_list:
        t.join()
    
    
    # 複合処理
    with open("dic/dic_carrier.json","r",encoding="utf-8") as f:
        match.carrier_dict=json.load(f)   
    with open("dic/dic_maker.json","r",encoding="utf-8") as f:
        match.maker_dict=json.load(f)    
    with open("dic/dic_tethering.json","r",encoding="utf-8") as f:
        match.tether_dict=json.load(f)
    with open("dic/dic_unlock.json","r",encoding="utf-8") as f:
        match.unlock_dict=json.load(f)
    with open("dic/dic_sim.json","r",encoding="utf-8") as f:
        match.sim_dict=json.load(f)
        
    df_master=pd.read_csv("kakaku/csv/devices_kakaku-scraped-edited.csv",index_col=0) 
    df_list=[pd.read_csv(file_path,index_col=0).fillna("") for file_path in 
             [
                "mvno/mineo/csv/devices_mineoD-scraped-edited.csv",
                "mvno/mineo/csv/devices_mineoA-scraped-edited.csv",
                "mvno/uq/csv/devices_uq-scraped-edited.csv",
                "mvno/ymobile/csv/devices_ymobile-scraped-edited.csv",
                "mvno/rakuten/csv/devices_rakuten-scraped-edited.csv",
                "mvno/ocn/csv/devices_ocn-scraped-edited.csv",
                "mvno/iij/csv/devices_iijD-scraped-edited.csv",
                "mvno/iij/csv/devices_iijA-scraped-edited.csv",
                "mvno/linemobile/csv/devices_linemobile-scraped-edited.csv",
                "mvno/biglobe/csv/devices_biglobeD-scraped-edited.csv",
                "mvno/biglobe/csv/devices_biglobeA-scraped-edited.csv",
                "mvno/qt/csv/devices_qtD-scraped-edited.csv",
                "mvno/qt/csv/devices_qtA-scraped-edited.csv",
                "mvno/qt/csv/devices_qtS-scraped-edited.csv"
            ]]
    name_list=["mineo_d","mineo_a","uq","ymobile","rakuten","ocn","IIJmio_d","IIJmio_a","linemobile","biglobe_d","biglobe_a","qt_d","qt_a","qt_s"]

    for df,name in zip(df_list,name_list):
        print(name)
        print(df.columns)
 
    #print(df_list[0].head())
       
    # マッチング
    #match.match_to_dflist(df_master,df_list,name_list,"csv/")
    
    # 連結
    match.joinMVNO(df_list,name_list,"csv/mvno_join.csv")

    # 新規項目を確認
    print("\ncarirer初登場：")
    item_set=match.get_set(df_list,"carrier")
    match.get_new(match.carrier_dict,item_set)
    print(item_set)
    print("\nmaker初登場：")
    item_set=match.get_set(df_list,"maker")
    match.get_new(match.maker_dict,item_set)
    print("\ntethering初登場：")
    item_set=match.get_set(df_list,"tethering")
    match.get_new(match.tether_dict,item_set)
    print("\sim初登場")
    item_set=match.get_set(df_list,"sim")
    match.get_new(match.sim_dict,item_set)
    
    # 辞書作成
    dic=match.get_dict(df_list[0],df_list,"sim1")
    