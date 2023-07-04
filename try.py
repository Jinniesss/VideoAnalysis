import sys
import numpy as np
import pandas as pd
import cv2
from PyQt6.QtWidgets import *
from PyQt6.QtMultimedia import *
from PyQt6.QtMultimediaWidgets import *
from PyQt6.QtCore import *
import seaborn as sns


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
def masked(df,name,pcutoff):
    prob = df[[name + '_likelihood']].values.squeeze()
    mask = prob < pcutoff
    df[name+'_x'] = np.ma.array(
        df[[name + "_x"]].values.squeeze(),
        mask=mask,
    )
    df[name+'_y'] = np.ma.array(
        df[[name + "_y"]].values.squeeze(),
        mask=mask,
    )
    return df

def trajectory(df,name):
    fig = plt.figure()
    fig.dpi = 300

    df = masked(df,name,0.7)
    x = df[name+'_x']
    y = df[name+'_y']

    plt.plot(x, y,linewidth = 0.7, color='red')

    # fancy but slow one:
    # l = len(df)
    # for i in range(l-2):
    #     plt.plot(x[i:i+2], y[i:i+2], color='red', alpha=0.2)

    plt.show()

def a_logplot(data):
    data = abs(data)
    # sns.kdeplot(data, fill=True)
    data = data[data != 0]
    plt.hist(data, bins=np.logspace(np.log10(min(data)), np.log10(max(data)), num=1000),
             histtype='step', edgecolor='black', linewidth=1.2)
    plt.xscale('log')

def cal_kin(Dataframe,name):
    df = Dataframe.copy()
    x = df[name + '_x']
    y = df[name + '_y']
    freq = 10  # frame/sec
    x_diff = np.diff(x)
    y_diff = np.diff(y)
    dis_diff = [np.linalg.norm([x_diff[i], y_diff[i]]) for i in range(len(x_diff))]     # pixel/frame
    v = dis_diff * freq  # pixel/sec

    a = np.diff(v)

    return v,a

def center_of_gravity(df):
    outer_bodyparts=['leftear','nose','rightear','rightbody1','rightbody2','rightside','rightbody4','rightbody5',
                    'tailbase','leftbody5','leftbody4','leftside','leftbody2','leftbody1']
    df['centroid_x'] = [0] * len(df)
    df['centroid_y'] = [0] * len(df)
    for t in range(len(df)):
        A = 0
        for i in range(len(outer_bodyparts)-1):
            # A += x[i] * y[i + 1] - x[i + 1] * y[i]
            bodypart = outer_bodyparts[i]
            bodypart_n = outer_bodyparts[i+1]
            x = df[bodypart+'_x'][t]
            y = df[bodypart+'_y'][t]
            xn = df[bodypart_n+'_x'][t]
            yn = df[bodypart_n+'_y'][t]
            A += x*yn-xn*y

            df['centroid_x'][t] += (x + xn) * (x * yn - xn * y)
            df['centroid_y'][t] += (y + yn) * (x * yn - xn * y)
            # centroid_x += (x[i] + x[i + 1]) * (x[i] * y[i + 1] - x[i + 1] * y[i])
            # centroid_y += (y[i] + y[i + 1]) * (x[i] * y[i + 1] - x[i + 1] * y[i])
    return df


# video_fname = '/Users/jinnie/Desktop/lab/behavior analysis/PD-Mice-Behavior-Analysis/test/Lindsay_TDT_FP-221104-095302_M105_M106-221104-162128_Cam1DLC_resnet50_Video_behaviorApr5shuffle1_100000_labeled.mp4'
# Dataframe = pd.read_csv('/Users/jinnie/Desktop/lab/behavior analysis/PD-Mice-Behavior-Analysis/short_video_kinematics(3h).csv')
# video = cv2.VideoCapture(video_fname)
# ret, frame = video.read()
# corners, marked_frame = select_corners(frame)
# cv2.imshow('Image',marked_frame)
# cv2.waitKey(0)  # Wait for any key press
# cv2.destroyAllWindows()
# Dataframe = center_of_gravity(Dataframe)
# justtry(Dataframe)

# fig = plt.figure()
# v,a = cal_kin(Dataframe,'centerbody')
# a_logplot(a)
# plt.show()
# trajectory(Dataframe,'centerbody')
