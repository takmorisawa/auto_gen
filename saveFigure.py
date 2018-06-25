import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

def saveFigure(score_list,title,save_path):
    
    fig,ax1=plt.subplots(figsize=(5,3))
    
    n,bins,patches=ax1.hist(score_list,bins=np.arange(0.0,1.1,0.1),alpha=0.7,label="Frequency")
    ax1.set_ylabel("Frequency")
    ax1.set_xlabel("Score")
    ax1.set_xlim(0,1)
    
    ax2=ax1.twinx()
    y2=(np.add.accumulate(n[::-1])/n.sum())[::-1]
    x2=np.convolve(bins,np.ones(2)/2,mode="same")[1:]
    lines=ax2.plot(x2,y2,ls="--",color="r",marker="o",label="Cumulative ratio")
    ax2.grid(visible=False)
    ax2.set_ylabel("Cumulative ratio")
    ax2.set_ylim(0,1.1)
    
    fig.legend(loc=(0.15,0.60))
    plt.title(title)
    
    plt.savefig(save_path)