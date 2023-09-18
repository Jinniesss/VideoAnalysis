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
    print('Current folder is [',os.path.basename(folder_path),'].')
    avi_files = []
    video_fname=''
    for file in os.listdir(folder_path):
        if file.endswith(".avi") or file.endswith(".mp4"):
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
    frame = get_frame_from_video(video_fname)
    frame = get_frame_from_video(video_fname)
    nest = True           # Whether is a selectable nest in the video or not
    mov_nest = False
    gen_centroid = False
    show_nest_ana = True
    flag_write = False
    re_gen_nest = False
    re_gen_va = False
    va_img = False
    re_transform = False
    laser = True
    name4traj = 'centerbody3'
    name4kin = ['leftear', 'rightear','centerbody3','nose','headstage','centerbody2','centerbody4']
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
            print('Calculating.. [NEW: center of gravity]')
            Dataframe = center_of_gravity(Dataframe)
            flag_write = True
            print('[DONE: center of gravity]')
        # -------------------------------------------------------------------#

        # Calculate the nest state (in/out -- 1/0)---------------------------#
        if re_gen_nest is True or not os.path.exists(dataname + '_nest_points_corrected.pickle'):
            nest = select_points(None,'select nest (press ENTER to finish)',dataname=dataname,is_video=True,v_fname=video_fname)
            print('Calculating.. [NEW: nest state]')
            Dataframe = gen_nest(Dataframe,name4traj,nest[0])
            # with open(dataname + '_nest_points.pickle', 'wb') as file:
            #     pickle.dump(nest[0], file)
            flag_write = True
            print('[DONE: nest state]')
        # -------------------------------------------------------------------#

        # Set the unit and transform the dataframe---------------------------#
        # !!! Remember only to transform once!!!
        Dataframe_o = Dataframe.copy()
        frame_t = None
        ori_area = 0
        if (mov_nest is True and os.path.exists(dataname+'_movin_nest.png'))\
                or not os.path.exists(dataname + '_pixel_per_cm.pickle') \
                or not os.path.exists(dataname + '_transformed_frame.pickle')\
                or not os.path.exists(dataname + '_nest_points_corrected.pickle'):
            pixel_per_cm, Dataframe,frame_t,corrected_nest,ori_area = calculate_transformation(frame, Dataframe)
            print(pixel_per_cm,'pixels per cm')
            with open(dataname + '_nest_points_corrected.pickle','wb') as file:
                pickle.dump(corrected_nest,file)
            with open(dataname + '_pixel_per_cm.pickle', 'wb') as file:
                pickle.dump(pixel_per_cm, file)
            with open(dataname + '_transformed_frame.pickle', 'wb') as file:
                pickle.dump(frame_t, file)
            flag_write = True
        else:
            with open(dataname + '_pixel_per_cm.pickle', 'rb') as file:
                pixel_per_cm = pickle.load(file)
            with open(dataname + '_transformed_frame.pickle', 'rb') as file:
                frame_t = pickle.load(file)
        # Save the area of nest
        if True or not os.path.exists(dataname + '_nest_area.mat'):
            with open(dataname + '_nest_points_corrected.pickle', 'rb') as file:
                nest_points = pickle.load(file)
            area_of(nest_points,pixel_per_cm,dataname)
        # -------------------------------------------------------------------#

        # Sample sizes of moving nest---------------------------------------#
        if mov_nest is True and os.path.exists(dataname+'_movin_nest.png'):
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))-1
            area_perc = []
            x = [0.,0.25,0.5, 0.75,1.]
            for i in range(0,5):
                print('Select for moving nest ',i,'/4')
                nest = select_points(None,'select nest (press ENTER to finish)',dataname=dataname,is_video=True,v_fname=video_fname,
                                     frame_number=int(total_frames/4*i))
                area_perc.append(area_pixel(nest[0])/ori_area)
            plt.plot(x,area_perc,'o')
            plt.plot(x, area_perc, '-')
            plt.ylabel('percentage')
            plt.savefig(dataname + '_movin_nest.png')
            plt.show()



        # Kinetics-----------------------------------------------------------#
        # Calculate the velocity and acceleration  (v in [cm/s]; a in [g])
        va_img_fname = dataname+'_va_plots'
        for name in name4kin:
            if re_gen_va or name+'_v' not in Dataframe.columns:
                print('Calculating.. [NEW: velocity & acceleration of ' + name+ ']')
                Dataframe = cal_v_a(Dataframe,name,pixel_per_cm,window=11)
                flag_write = True
                print('[DONE: velocity & acceleration of ' + name+ ']')
            if va_img is True:
                if not os.path.exists(va_img_fname):
                    os.mkdir(va_img_fname)
                show_v_a(Dataframe,name,va_img_fname)

        # Nest kinetics analysis (movement v.s. nest state)
        if not os.path.exists(dataname+'_Moving_ana.mat') or not os.path.exists(dataname+'_nest_ana.png'):
            print('Running nest analysis...')
            nest_ana(Dataframe,name4traj,pixel_per_cm,dataname,window=4)
            print('[DONE: nest analysis]')
        # # test_window_for_nest(Dataframe,name,pixel_per_cm)
        # -------------------------------------------------------------------#

        # Calculate variance of trajectory
        for name in name4kin:
            if name+'_var' not in Dataframe.columns:
                print('Calculating.. [NEW: variance of trajectory of ' + name+ ']')
                Dataframe = cal_var_traj(Dataframe,name,pixel_per_cm,window=11)
                flag_write = True
                print('[DONE: variance of trajectory of ' + name+ ']')


        # Plot the trajectory------------------------------------------------#
        if not os.path.exists(dataname+'_trajectory.png'):
            # plot_trajectory(Dataframe_o, name, bg=frame)
            plot_trajectory(Dataframe, name4traj, bg=frame_t, dataname=dataname)
        # -------------------------------------------------------------------#

        # Cluster according to acceleration
        if laser is True:
            laser_a_cluster(Dataframe,'nose',dataname,re_gen_plots=True)


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