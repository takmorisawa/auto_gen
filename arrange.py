import pandas as pd

def relpace_csv_contents(in_file_path,out_file_path,keywords):
    """
    CSVファイル内のデータを部分置換する

    Prameters
    --------
    in_file_path : CSVファイルの入力パス
    out_file_path: CSVファイルの出力パス
    keyworkds : 置換内容を辞書型で記述、対象は一文字
    """
    df_replaced=pd.DataFrame()
    df=pd.read_csv(in_file_path,dtype=str)
    df=df.fillna("")

    trans=str.maketrans(keywords)

    for item in df.items():
        data=[s.translate(trans) for s in item[1]]
        #print(data)
        df_replaced[item[0]]=data

    df_replaced.index.name="id"
    df_replaced.to_csv(out_file_path)


if __name__=="__main__":

    # 全角スペース、ダブルクォーテーション、カンマ
    keywords={"　":" ","\"":"",",":""}
    relpace_csv_contents("projects/support_devices/csv/mvno_join.csv","mvno_join_arrange.csv",keywords)
