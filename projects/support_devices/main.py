import sys
import os
import threading
import json
import pandas as pd
import traceback
import re

sys.path.append("../../")
import scrape
import crowl
import scrapeTable
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
import mvno.dmm.postprocess as dp
import mvno.nifmo.postprocess as np

import mvno.linemobile.genConf as genConf


# tidがここでは未定義なので注意
pipelines={
    "ymobile":[
        lambda x:crowl.crowl("mvno/{0}/crowl.config".format(tid)),
        lambda x:scrape.scrape("mvno/{0}/scrape.config".format(tid)),
        lambda x:diff.diff(
                "mvno/{0}/tmp/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/current/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/tmp".format(tid)),
        lambda x:backup.backup(
                "mvno/{0}/tmp".format(tid),
                "mvno/{0}/current".format(tid)),
        lambda x:yp.postprocess()],
    "biglobe":[
        lambda x:crowl.crowl("mvno/{0}/crowl.config".format(tid)),
        lambda x:scrape.scrape("mvno/{0}/scrape.config".format(tid)),
        lambda x:diff.diff(
                "mvno/{0}/tmp/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/current/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/tmp".format(tid)),
        lambda x:backup.backup(
                "mvno/{0}/tmp".format(tid),
                "mvno/{0}/current".format(tid)),
        lambda x:bp.postprocess()],
    "uq":[
        lambda x:crowl.crowl("mvno/{0}/crowl.config".format(tid)),
        lambda x:scrape.scrape("mvno/{0}/scrape.config".format(tid)),
        lambda x:diff.diff(
                "mvno/{0}/tmp/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/current/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/tmp".format(tid)),
        lambda x:backup.backup(
                "mvno/{0}/tmp".format(tid),
                "mvno/{0}/current".format(tid)),
        lambda x:up.postprocess()],
    "mineo":[
        lambda x:crowl.crowl("mvno/{0}/crowl.config".format(tid)),
        lambda x:scrape.scrape("mvno/{0}/scrape.config".format(tid)),
        lambda x:diff.diff(
                "mvno/{0}/tmp/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/current/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/tmp".format(tid)),
        lambda x:backup.backup(
                "mvno/{0}/tmp".format(tid),
                "mvno/{0}/current".format(tid)),
        lambda x:mp.postprocess()],
    "linemobile":[
        lambda x:crowl.crowl("mvno/{0}/crowl_mk.config".format(x)),
        lambda x:scrape.scrape("mvno/{0}/scrape_mk.config".format(x)),
        lambda x:genConf.genConf("tmp/csv/maker-scraped.csv","crowl.config"),
        lambda x:crowl.crowl("mvno/{0}/crowl.config".format(x)),
        lambda x:scrape.scrape("mvno/{0}/scrape.config".format(x)),
        lambda x:diff.diff(
                "mvno/{0}/tmp/csv/devices_{0}-scraped.csv".format(x),
                "mvno/{0}/current/csv/devices_{0}-scraped.csv".format(x),
                "mvno/{0}/tmp".format(x)),
        lambda x:backup.backup(
                "mvno/{0}/tmp".format(x),
                "mvno/{0}/current".format(x)),
        lambda x:lp.postprocess()],
    "ocn":[
        lambda x:crowl.crowl("mvno/{0}/crowl.config".format(tid)),
        lambda x:scrape.scrape("mvno/{0}/scrape.config".format(tid)),
        lambda x:diff.diff(
                "mvno/{0}/tmp/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/current/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/tmp".format(tid)),
        lambda x:backup.backup(
                "mvno/{0}/tmp".format(tid),
                "mvno/{0}/current".format(tid)),
        lambda x:op.postprocess()],
    "rakuten":[
        lambda x:crowl.crowl("mvno/{0}/crowl.config".format(tid)),
        lambda x:scrape.scrape("mvno/{0}/scrape.config".format(tid)),
        lambda x:diff.diff(
                "mvno/{0}/tmp/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/current/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/tmp".format(tid)),
        lambda x:backup.backup(
                "mvno/{0}/tmp".format(tid),
                "mvno/{0}/current".format(tid)),
        lambda x:rp.postprocess()],
    "iij":[
        lambda x:crowl.crowl("mvno/{0}/crowl.config".format(tid)),
        lambda x:scrape.scrape("mvno/{0}/scrape.config".format(tid)),
        lambda x:diff.diff(
                "mvno/{0}/tmp/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/current/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/tmp".format(tid)),
        lambda x:backup.backup(
                "mvno/{0}/tmp".format(tid),
                "mvno/{0}/current".format(tid)),
        lambda x:ip.postprocess()],
    "qt":[
        lambda x:crowl.crowl("mvno/{0}/crowl.config".format(tid)),
        lambda x:scrape.scrape("mvno/{0}/scrape.config".format(tid)),
        lambda x:scrape.scrape("mvno/{0}/scrape_mk.config".format(tid)),
        lambda x:diff.diff(
                "mvno/{0}/tmp/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/current/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/tmp".format(tid)),
        lambda x:backup.backup(
                "mvno/{0}/tmp".format(tid),
                "mvno/{0}/current".format(tid)),
        lambda x:qp.postprocess()],
    "dmm":[
        lambda x:crowl.crowl("mvno/{0}/crowl.config".format(tid)),
        lambda x:scrapeTable.scrapeTable("mvno/{0}/scrape.config".format(tid)),
        lambda x:diff.diff(
                "mvno/{0}/tmp/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/current/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/tmp".format(tid)),
        lambda x:backup.backup(
                "mvno/{0}/tmp".format(tid),
                "mvno/{0}/current".format(tid)),
        lambda x:dp.postprocess()],
    "nifmo":[
        lambda x:crowl.crowl("mvno/{0}/crowl.config".format(tid)),
        lambda x:scrapeTable.scrapeTable("mvno/{0}/scrape.config".format(tid)),
        lambda x:diff.diff(
                "mvno/{0}/tmp/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/current/csv/devices_{0}-scraped.csv".format(tid),
                "mvno/{0}/tmp".format(tid)),
        lambda x:backup.backup(
                "mvno/{0}/tmp".format(tid),
                "mvno/{0}/current".format(tid)),
        lambda x:np.postprocess()]
    }

# pathとnameのリストを統合したい
path_list=[
        ("mvno/mineo/current/csv/devices_mineoD-scraped-edited.csv","mineo_d"),
        ("mvno/mineo/current/csv/devices_mineoA-scraped-edited.csv","mineo_a"),
        ("mvno/mineo/current/csv/devices_mineoS-scraped-edited.csv","mineo_s"),
        ("mvno/uq/current/csv/devices_uq-scraped-edited.csv","uq"),
        ("mvno/ymobile/current/csv/devices_ymobile-scraped-edited.csv","ymobile"),
        ("mvno/rakuten/current/csv/devices_rakutenD-scraped-edited.csv","rakuten_d"),
        ("mvno/rakuten/current/csv/devices_rakutenA-scraped-edited.csv","rakuten_a"),
        ("mvno/ocn/current/csv/devices_ocn-scraped-edited.csv","ocn"),
        ("mvno/iij/current/csv/devices_iijD-scraped-edited.csv","IIJmio_d"),
        ("mvno/iij/current/csv/devices_iijA-scraped-edited.csv","IIJmio_a"),
        ("mvno/linemobile/current/csv/devices_linemobileD-scraped-edited.csv","linemobile_d"),
        ("mvno/linemobile/current/csv/devices_linemobileS-scraped-edited.csv","linemobile_s"),
        ("mvno/biglobe/current/csv/devices_biglobeD-scraped-edited.csv","biglobe_d"),
        ("mvno/biglobe/current/csv/devices_biglobeA-scraped-edited.csv","biglobe_a"),
        ("mvno/qt/current/csv/devices_qtD-scraped-edited.csv","qt_d"),
        ("mvno/qt/current/csv/devices_qtA-scraped-edited.csv","qt_a"),
        ("mvno/qt/current/csv/devices_qtS-scraped-edited.csv","qt_s"),
        ("mvno/dmm/current/csv/devices_dmm-scraped-edited.csv","dmm"),
        ("mvno/nifmo/current/csv/devices_nifmo-scraped-edited.csv","nifmo")
        ]

def execute_unit(tid,pipeline,results):

    for f in pipeline:
        try:
            results[tid]=f(tid)
        except Exception as e:
            results[tid]=False
            print("■■■ except ■■■:{0},{1}".format(e,tid))
            #traceback.print_exc() # トレースバック
        finally:
            #各ステージの処理でFalseを返したら以降のパイプラン処理をキャンセルする
            if results[tid]==False:
                return False
           
    return True # 全プロセス正常終了

if __name__=="__main__":

    root=os.path.dirname(os.path.abspath(__file__))
    
    # ■■■単体処理■■■
    results={}
    t_list=[]
    
    # 個別に実行する場合は必ず変数tidを定義すること
    #tid="ymobile"
    #execute_unit(tid,pipelines[tid],results)
    
    for tid,pipeline in pipelines.items():
        #execute_unit(tid,pipeline,results)
        
        ## マルチスレッドの場合
        #t_list.append(threading.Thread(target=execute_unit,args=[tid,pipeline,results]))
        #t_list[-1].start()
        pass
        
    #for t in t_list:
    #    t.join()
    
    print(results)

    # ■■■複合処理■■■
        
    # マスターDB
    df_master=pd.read_csv("kakaku/csv/devices_kakaku-scraped-edited.csv",index_col=0)
    # mvnoDBのリスト
    df_list=[pd.read_csv(file_path[0],index_col=0).fillna("") for file_path in path_list]

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
    with open("dic/dic_maker.json","r",encoding="utf-8") as f:
        match.dic_maker=json.load(f)
        
    # 新規項目を確認
    for column, dic in zip(
            ["carrier","maker","tethering","sim","unlock","device_type"],
            [match.dic_carrier,match.dic_maker,match.dic_tether,match.dic_sim,match.dic_unlock,match.dic_type]):
        print("\n{0}初登場：".format(column))
        item_set=match.get_set(df_list,column)
        match.get_new(dic,item_set)
        
    # 表記揺れ解消
    for df,name in zip(df_list,[item[1] for item in path_list]):
        print("replacing device type...{0}".format(name))
        if "device_type" in df.columns:
            df["device_type"]=[match.get_first(t,match.dic_type) for t in df["device_type"]]
        else:
            df["device_type"]=""
        
    # 保存
    for df,name in zip(df_list,[item[1] for item in path_list]):
        df.to_csv(os.path.join(root,"csv/mvno/devices_{0}.csv").format(name))

    # 更新日時を出力
    date_info={}
    for csv_path,name in path_list:
        date_dir=os.path.dirname(csv_path)
        date_dir=os.path.join(os.path.dirname(date_dir),"html")
        for file_name in [x for x in os.listdir(date_dir) if len(x)==8 and re.match("\d{8}",x)]:
            date_info[name]=file_name
    with open("csv/update_info.json","w") as f:
        json.dump(date_info,f,indent=4,ensure_ascii=False)

    #for df,name in zip(df_list,name_list):
    #    print(name)
    #    print(df.columns)
 
    #print(df_list[0].head())
       
    # マッチング
    #match.match_to_dflist(df_master,df_list,name_list,"csv/")
    
    # 連結
    match.joinMVNO(df_list,[item[1] for item in path_list],"csv/mvno_join.csv")

    # 辞書作成
    #dic=match.get_dict(df_list[4],df_list,"device_type")
    