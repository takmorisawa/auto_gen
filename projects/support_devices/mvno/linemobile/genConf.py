import pandas as pd
import os

str1="""{
    "starting_urls":[
"""
str2="""
        ],
    "nextpage_xpath":"",
    "target_xpath":"",
    "ending_url":"",
    "render_js":1,
    "save_dir":"projects/support_devices/mvno/linemobile/tmp/html",
    "morebutton_xpath":"//p[contains(@class,'FnMoreList')]"
}
"""

def genConf(config_file_path,out_file_path):
    
    root=os.path.dirname(os.path.abspath(__file__))
    
    df=pd.read_csv(os.path.join(root,config_file_path),index_col=0)
    
    url_list=["        \"https://mobile.line.me/support/device/search/?supplier={0}\"".format(maker) for maker in df["maker"]]
    print(url_list)

    with open(os.path.join(root,out_file_path),"w") as f:
        f.write(str1)
        f.write(",\n".join(url_list))
        f.write(str2)
        

if __name__ == '__main__':

    genConf("tmp/csv/maker-scraped.csv","crowl.config")
