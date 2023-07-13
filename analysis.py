# Global variable----------------------------------------------------#
global freq, pcutoff,pixel_per_cm,real_width,real_length,bodyparts
freq = 10  # frame per sec
pcutoff = 0.9
real_width = 11.5  # inch
real_length = 7
bodyparts = ['nose','leftear','rightear','headstage','leftbody1','leftbody2','leftbody3','leftbody4',
                 'leftbody5','rightbody1','rightbody2','rightbody3','rightbody4','rightbody5','centerbody1',
                 'centerbody2','centerbody3','centerbody4','centerbody5','tailbase','tailtip',
                 'tail1','tail2','tail3']
# -------------------------------------------------------------------#
import traceback
import os.path
import os
from tkinter.filedialog import askopenfilename, askdirectory

import matplotlib.pyplot as plt
from scipy.io import loadmat
from sklearn.mixture import GaussianMixture

from functions.file_processing import *
from functions.trajectory_associated import *
from functions.laser_a_cluster import *
from functions.nest_analysis import *
from functions.kinetics import *

import pickle

def plot_likelihood(Dataframe,fig_name):
    fig, axes = plt.subplots(4, 6, figsize=(12, 8))

    for i, bodypart in enumerate(bodyparts):
        row = i // 6
        col = i % 6
        axes[row, col].hist(Dataframe[bodypart + '_likelihood'], bins=200, edgecolor='black')
        axes[row, col].set_title(bodypart)

    plt.tight_layout()
    plt.savefig(fig_name)
    plt.show()



# 🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥MAIN🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥 #
# ------------------------------------------BEGINS------------------------------------------ #
# -------------------------------------------HERE------------------------------------------- #
#
#

def main(folder_path=None):

    # File selection-----------------------------------------------------#
    if folder_path is None:
        root = tk.Tk()
        root.withdraw()
        folder_path = askdirectory()
    if len(folder_path) == 0:
        print('User Exited.')
        quit()
    print('Current folder is',os.path.basename(folder_path))
    avi_files = []
    video_fname=''
    for file in os.listdir(folder_path):
        if file.endswith(".avi"):
            avi_files.append(file)
    if len(avi_files) == 1:
        video_fname = folder_path + '/' + avi_files[0]
    elif len(avi_files) == 0:
        print('Video file not found in current folder.')
        return
    else:
        print('Error when loading video file:',avi_files)
        return

    dataname = folder_path + '/' + os.path.basename(folder_path)

    csv_fname = dataname + '_data.csv'

    if not os.path.exists(csv_fname):
        print(csv_fname)
        csv_files = []
        for file in os.listdir(folder_path):
            if file.endswith(".csv"):
                csv_files.append(file)
        if len(csv_files) == 1:
            csv_fname = folder_path + '/' + csv_files[0]
        else:
            print('Error when loading csv file:', csv_files)
            quit()
        csv_fname = change_csv_layout(csv_fname,dataname)
    # -------------------------------------------------------------------#

    # Initiation---------------------------------------------------------#
    print('Initiating...')
    Dataframe = pd.read_csv(csv_fname)
    video = cv2.VideoCapture(video_fname)
    ret, frame = video.read()
    nest = True           # Whether is a selectable nest in the video or not
    gen_centroid = False
    show_nest_ana = True
    flag_write = False
    re_gen_nest = False
    re_gen_va = False
    re_transform = False
    laser = False
    name = 'centerbody3'
    # -------------------------------------------------------------------#
    try:
        # Generate likelihood plot-------------------------------------------#
        li_fname = dataname + '_likelihood.png'
        if not os.path.exists(li_fname):
            print('Plotting likelihood of all bodyparts...')
            plot_likelihood(Dataframe,li_fname)
            print('[DONE: plot saved]')
        # -------------------------------------------------------------------#

        # Calculate the centroid---------------------------------------------#
        if gen_centroid and 'centroid_x' not in Dataframe.columns:
            print('Updating csv file.. [NEW: center of gravity]')
            Dataframe = center_of_gravity(Dataframe)
            flag_write = True
            print('[DONE: center of gravity]')
        # -------------------------------------------------------------------#

        # Calculate the nest state (in/out -- 1/0)---------------------------#
        if nest is True and \
                (re_gen_nest is True or 'nest' not in Dataframe.columns):
            print('Updating csv file.. [NEW: nest state]')
            nest = select_points(frame,'select nest (press ENTER to finish)',dataname=dataname)
            Dataframe = gen_nest(Dataframe,name,nest[0])
            flag_write = True
            print('[DONE: nest state]')
        # -------------------------------------------------------------------#

        # Set the unit and transform the dataframe---------------------------#
        # !!! Remember only to transform once!!!
        Dataframe_o = Dataframe.copy()
        frame_t = None
        if not os.path.exists(dataname + '_pixel_per_cm.pickle') \
                or not os.path.exists(dataname + '_transformed_frame.pickle'):
            pixel_per_cm, Dataframe,frame_t = calculate_transformation(frame, Dataframe)
            print(pixel_per_cm,'pixels per cm')
            with open(dataname + '_pixel_per_cm.pickle', 'wb') as file:
                pickle.dump(pixel_per_cm, file)
            flag_write = True
            # pixel_per_cm = 8.73537061995475    # just for testing
            with open(dataname + '_transformed_frame.pickle', 'wb') as file:
                pickle.dump(frame_t, file)
            flag_write = True
        else:
            with open(dataname + '_pixel_per_cm.pickle', 'rb') as file:
                pixel_per_cm = pickle.load(file)
            with open(dataname + '_transformed_frame.pickle', 'rb') as file:
                frame_t = pickle.load(file)

        # -------------------------------------------------------------------#

        # Kinetics-----------------------------------------------------------#
        # Calculate the velocity and acceleration  (v in [cm/s]; a in [g])
        if re_gen_va or name+'_v' not in Dataframe.columns:
            print('Updating csv file.. [NEW: velocity & acceleration of ' + name+ ']')
            Dataframe = cal_v_a(Dataframe,name,pixel_per_cm,window=11)
            flag_write = True
            print('[DONE: velocity & acceleration of ' + name+ ']')

        # Nest kinetics analysis (movement v.s. nest state)
        if True or not os.path.exists(dataname+'_Moving_ana.mat') or not os.path.exists(dataname+'_nest_ana.png'):
            print('Running nest analysis...')
            nest_ana(Dataframe,name,pixel_per_cm,dataname,window=4)
            print('[DONE: nest analysis]')
        # # test_window_for_nest(Dataframe,name,pixel_per_cm)
        # -------------------------------------------------------------------#

        # Calculate variance of trajectory
        if False:
        # if name+'_var' not in Dataframe.columns:
            print('Updating csv file.. [NEW: variance of trajectory of ' + name+ ']')
            Dataframe = cal_var_traj(Dataframe,name,pixel_per_cm,window=11)
            flag_write = True
            print('[DONE: variance of trajectory of ' + name+ ']')


        # Plot the trajectory------------------------------------------------#
        # plot_trajectory(Dataframe_o, name, bg=frame)
        plot_trajectory(Dataframe, name, bg=frame_t, dataname=dataname)
        # -------------------------------------------------------------------#

        # Cluster according to acceleration
        if laser is True:
            laser_a_cluster(Dataframe,name,dataname,re_gen_plots=True)


        if flag_write:
            print("Writing to new csv file...")
            Dataframe.to_csv(csv_fname,index=False)
            print('Saved: ',csv_fname)

    except:
        traceback.print_exc()
        if flag_write:
            print("Errors occurred. But writing to new csv file anyway...")
            Dataframe.to_csv(csv_fname,index=False)
            print('Saved: ',csv_fname)



if __name__ == '__main__':
    main()