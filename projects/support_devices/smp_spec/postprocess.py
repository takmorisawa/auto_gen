import pandas as pd
import os
import re

def postprocess():

    current_dir=os.path.dirname(os.path.abspath(__file__))
    
    df=pd.read_csv(os.path.join(current_dir,"csv/smp_spec-scraped.csv"),index_col=0)
    df_edited=pd.DataFrame()

    org_columns=['チェックをいれてクリック_チェックをいれてクリック', 'チェックをいれてクリック_チェックをいれてクリック.1', '製品名_製品名',
       '満足度_満足度', 'クチコミ_クチコミ', '基本仕様_キャリア', '基本仕様_販売時期', '基本仕様_OS種類',
       '基本仕様_最大待受時間', '基本仕様_CPU', '基本仕様_CPUコア数', '基本仕様_内蔵メモリ', '基本仕様_インターフェース',
       '基本仕様_外部メモリタイプ', '基本仕様_外部メモリ最大容量', '基本仕様_バッテリー容量', '基本仕様_幅x高さx厚み',
       '基本仕様_重量', '画面性能_画面サイズ', '画面性能_画面解像度', '画面性能_パネル種類', 'ネットワーク_データ通信サービス',
       'ネットワーク_下り最大データ通信速度', 'ネットワーク_Bluetooth', 'ネットワーク_赤外線通信機能',
       'ネットワーク_テザリング対応', 'ネットワーク_NFC対応', 'ネットワーク_LTE対応', 'ネットワーク_無線LAN規格',
       'カメラ_背面カメラ画素数', 'カメラ_前面カメラ画素数', 'カメラ_手ブレ補正', 'カメラ_撮影用フラッシュ',
       'その他_4K撮影対応', 'その他_耐水・防水機能', 'その他_HDMI端子', 'その他_フルセグ', 'その他_ワンセグ',
       'その他_GPS機能', 'その他_MHL対応', 'その他_ハイレゾ', 'その他_おサイフケータイ/FeliCa',
       'その他_キャリア割引対象端末', 'その他_認証機能', 'SIMカード_デュアルSIM',
       'SIMカード_デュアルSIMデュアルスタンバイ(DSDS)', 'SIMカード_SIM情報', 'カラー_カラー', '発売日_発売日',
       '登録日_登録日','kakaku_id']
    new_columns=['drop1', 'drop2', 'name',
       'cs', 'review', 'carrier', 'season', 'os',
       'standby', 'cpu', 'cpu_core', 'rom_ram', 'interface',
       'extra_memory', 'extra_memsize', 'battery', 'size',
       'weight', 'screen', 'resolution', 'panel', 'comm',
       'download', 'bluetooth', 'ingrared',
       'tethering', 'nfc', 'lte', 'wifi',
       'rear_cam', 'front_cam', 'stabilizer', 'flash',
       '4k_video', 'protection', 'hdmi', 'full_seg', 'one_seg',
       'gps', 'mhl', 'high_res', 'e_money',
       'discount', 'auth', 'dual_sim',
       'dsds', 'sim', 'color', 'release',
       'regist','kakaku_id']
    
    dic_columns={org:_new for org,_new in zip(org_columns,new_columns)}

    df=df.rename(columns=dic_columns)
    
    for idx,col in df.iterrows():
         
        # nameからmakerを分離
        m=re.match("(.+)\t(.+)\t.*",col["name"])
        col["maker"]=m.groups()[0].strip() if m else ""
        col["name"]=m.groups()[1].strip() if m else ""
        
        # name1からcarrierを削除
        m=re.match("(.+) {0}".format(col["carrier"]),col["name"]) 
        col["name"]=m.groups()[0].strip() if m else col["name"]
        
        # nameからGBを削除
        m=re.match("(.+) \d+GB",col["name"])
        col["name"]=m.groups()[0].strip() if m else col["name"]
        
        # ROM RAM
        m=re.match("ROM：*(.+)RAM：*(.+)",col["rom_ram"])
        col["rom"]=m.groups()[0].strip() if m else col["rom_ram"]
        col["ram"]=m.groups()[1].strip() if m else ""
        m=re.match("ROM：*(.+)",col["rom"])
        col["rom"]=col["rom"].strip("/")
        col["ram"]=col["ram"].strip("/")
        
        # drop
        col=col.drop("drop1")
        col=col.drop("drop2")
        
        # タブをスラッシュに置換
        for idx,val in col.iteritems():
            col[idx]=col[idx].replace("\t","/")
        
        df_edited=df_edited.append(col,ignore_index=True)

    # カラムの並び替え
    df_edited=df_edited[["maker"]+new_columns[2:len(new_columns)]+["rom","ram"]]
    
    # drop
    df_edited=df_edited.drop("rom_ram",axis=1)
    
    df_edited.to_csv(os.path.join(current_dir,"csv/smp_spec-scraped-edited.csv"))


if __name__ == '__main__':

    postprocess()
