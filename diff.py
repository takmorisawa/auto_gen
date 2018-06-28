import difflib
import os

def diff(filepath1,filepath2,outdir):
    
    print("diff...{0}".format(outdir))
    
    root=os.path.dirname(os.path.abspath(__file__))
    
    filepath1=os.path.join(root,filepath1)
    filepath2=os.path.join(root,filepath2)
    outdir=os.path.join(root,outdir)
    
    with open(filepath1,"r",encoding="utf-8") as f:
        text1=[row for row in f]
        
    with open(filepath2,"r",encoding="utf-8") as f:
        text2=[row for row in f]
        
    d=difflib.HtmlDiff()
    html=d.make_table(text1,text2)
    
    with open(os.path.join(outdir,"diff.html"),"w") as f:
        f.write(html)
        
    return text1!=text2
        
if __name__=="__main__":
    
    ret=diff("projects/support_devices/mvno/ymobile/csv/devices_ymobile-scraped.csv",
         "projects/support_devices/mvno/ymobile/tmp/csv/devices_ymobile-scraped.csv",
         "projects/support_devices/mvno/ymobile")
    
    print("diff done",ret)