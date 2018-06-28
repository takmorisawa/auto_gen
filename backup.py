import os
import shutil
import datetime
import re

def backup(src_path,dst_path):
    
    print("backup...{0}".format(dst_path))
    
    MAX_BACKUP_SIZE=5
    current_dir=os.path.dirname(os.path.abspath(__file__))
    
    src_path=os.path.join(current_dir,src_path)
    dst_path=os.path.join(current_dir,dst_path)
    dst_root=os.path.dirname(dst_path)
    tmp_dir=os.path.join(dst_root,"_tmp")
    
    # カレントフォルダーを仮バックアップとしてリネーム
    try:
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        if os.path.exists(dst_path):
            shutil.move(dst_path,tmp_dir)
    except:
        return False
    
    # 作業用フォルダをカレントフォルダとしてリネーム
    try:
        if os.path.exists(dst_path):
            shutil.rmtree(dst_path)
        shutil.copytree(src_path,dst_path)
    except:
        #ロールバック（仮バックアップフォルダをカレントフォルダに戻す）
        if os.path.exists(tmp_dir):
            shutil.move(tmp_dir,dst_path)
        return False
    
    # バックアップ作成
    try:
        # 仮バックアップフォルダをバックアップとしてリネーム
        bk_name=datetime.datetime.today().strftime("%Y%m%d-%H%M-%S") # バックアップフォルダの名前
        shutil.move(tmp_dir,os.path.join(dst_root,bk_name))
        
        # バックアップフォルダの一覧を取得して件数をチェック
        dir_list=[x for x in os.listdir(dst_root) if re.match("\d{8}-\d{4}-\d{2}",x)]
        dir_list.sort(reverse=True) # 新しい順にソート
        rm_list=dir_list[MAX_BACKUP_SIZE:] if len(dir_list)>MAX_BACKUP_SIZE else [] # インデックス５番以降を削除
        
        # 条件を超えたフォルダを削除
        for rm in rm_list:
            shutil.rmtree(os.path.join(dst_root,rm))
    except:
        # 警告のみ
        pass
    
    return True # 正常終了

if __name__=="__main__":
    
    backup("test/work","test/current")
    