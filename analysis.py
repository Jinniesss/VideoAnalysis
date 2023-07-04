import os.path
from functions.trajectory_associated import *
import matplotlib.pyplot as plt
from functions.file_processing import *


# Global variable----------------------------------------------------#
global freq, pcutoff,pixel_per_cm
freq = 10  # frame per sec
pcutoff = 0.8
# -------------------------------------------------------------------#


def gen_nest(df,name,nest):
    nest = [(int(x),int(y)) for x,y in nest]
    nest = np.array(nest)
    df['nest'] = [0] * len(df)
    # print(len(nest))
    # # nest = nest.reshape(len(nest),1,2).astype(np.int64)
    # print(nest)
    # print(type(nest))

    for i in range(len(df)):
        x = int(df[name+'_x'][i])
        y = int(df[name+'_y'][i])
        if is_in_roi(x,y,nest):
            df['nest'][i]= 1
    return df

def nest_ana(Dataframe,name,pixel_per_cm,window=3,show=True):
    Dataframe = masked(Dataframe,name,nest=True)
    # 1: stay time
    fig, axs = plt.subplots(1, 3, figsize=(12,5))
    nest_state = Dataframe['nest']
    in_nest_frame_num = nest_state.value_counts().get(1, 0)
    out_nest_frame_num = nest_state.value_counts().get(0, 0)
    # Set the names for each bar
    names = ['In Nest', 'Out of Nest']
    counts = [in_nest_frame_num/10, out_nest_frame_num/10]
    # Create the histogram

    axs[0].pie(counts, labels=names, autopct='%1.1f%%')
    axs[0].set_title('Duration of Stay')
    axs[1].bar(names, counts, width=0.5)
    # axs[1].set_xlabel('Nest State')
    axs[1].set_ylabel('Duration of Stay(sec)')
    plt.subplots_adjust(wspace=1)


    # 2: moving rate in each state
    v_in_nest_frame_num = 0     # valid frame number
    v_out_nest_frame_num = 0
    in_nest_distance = 0
    out_nest_distance = 0
    # Identify the groups based on the change in values of column 'nest'
    groups = (Dataframe['nest'].diff() != 0).cumsum()

    # Group the DataFrame based on the identified groups
    grouped_df = Dataframe.groupby(groups)

    for group_num, group_data in grouped_df:
        cur_nest_state=group_data['nest'][group_data.index[0]]
        if np.isnan(cur_nest_state):
            continue

        df = group_data.copy()
        df = df.rolling(window=window).mean()
        df = df.dropna()
        df['distance'] = np.linalg.norm(df[[name+'_x', name+'_y']].diff(), axis=1)
        df = df.dropna()

        if cur_nest_state == 1:
            in_nest_distance += sum(df['distance'])
            v_in_nest_frame_num += len(df)
        elif cur_nest_state == 0:
            out_nest_distance += sum(df['distance'])
            v_out_nest_frame_num += len(df)
        else:
            print('error:')
            print(group_data['nest'])

    moving_rate_in = in_nest_distance/v_in_nest_frame_num/pixel_per_cm*freq      # cm per sec
    moving_rate_out = out_nest_distance/v_out_nest_frame_num/pixel_per_cm*freq

    axs[2].plot([0, 1], [moving_rate_in, moving_rate_out], '-', lw=2,color = 'gray')
    axs[2].bar(0, moving_rate_in, color='blue', alpha=0.3,width=0.5)
    axs[2].bar(1, moving_rate_out, color='red', alpha=0.3,width=0.5)
    axs[2].scatter(np.zeros_like(moving_rate_in), moving_rate_in, color='blue', label='In-Nest')
    axs[2].scatter(np.ones_like(moving_rate_out), moving_rate_out, color='red', label='Out-of-Nest')
    axs[2].set_ylabel('Moving Rate (cm/s)')
    axs[2].set_xticks([0, 1])
    axs[2].set_xticklabels(['In Nest', 'Out of Nest'])
    # axs[2].set_ylim(0,1.3*moving_rate_out)

    if show == False:
        plt.clf()
        plt.close()
    else:
        plt.show()

    return moving_rate_out


def kinetics(Dataframe, name, window=3,show=True):
    df = Dataframe.copy()
    df = df.rolling(window=window,center=True).mean()
    # df.loc[df[name + '_likelihood'] < 0.8, name + '_x'] = np.nan
    # nan_count = df[name+'_x'].isna().rolling(window=window,center=True).sum()

    # 1: Calculate velocity and acceleration
    Dataframe[name + '_v'] = np.linalg.norm(df[[name + '_x', name + '_y']].diff().shift(-1), axis=1)    # pixel per frame
    Dataframe[name + '_v'] = Dataframe[name + '_v'] * freq / pixel_per_cm  # cm per sec
    Dataframe[name + '_a'] = Dataframe[name + '_v'].diff() * freq /100/9.8 # g


    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    data = Dataframe[name + '_v'].dropna()
    axes[0].hist(data, bins=np.logspace(np.log10(min(data)), np.log10(max(data)), num=1000),
                 histtype='step', edgecolor='black', linewidth=1.2)
    axes[0].set_xscale('log')
    axes[0].set_xlabel('velocity(cm/s)')

    data = abs(Dataframe[name+'_a'].dropna())
    # axes[1].hist(data, bins=np.logspace(np.log10(min(data)), np.log10(max(data)), num=3000),
    #             histtype='step', edgecolor='black', linewidth=1.2)
    axes[1].hist(data, bins=np.logspace(np.log10(10**(-7)), np.log10(1), num=1000),
                histtype='step', edgecolor='black', linewidth=1.2)
    axes[1].set_xscale('log')
    axes[1].set_xlabel('acceleration(g)')
    fig.suptitle('window size='+str(window))

    return Dataframe


def test_window_for_nest(Dataframe,name,pixel_per_cm):
    rate = []
    for i in range(1,101):
        print('Calculating -- ',i,'/100...')
        rate.append(nest_ana(Dataframe,name,pixel_per_cm,window=i,show=False))
    plt.clf()
    plt.plot(range(1,101),rate,'-o')
    plt.show()



#
# 🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥MAIN🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥 #
# ------------------------------------------BEGINS------------------------------------------ #
# -------------------------------------------HERE------------------------------------------- #
#
#

if __name__ == '__main__':

    # File selection-----------------------------------------------------#
    root = tk.Tk()
    root.withdraw()
    video_fname = filedialog.askopenfilename(title="Select Video File")
    if video_fname is None:
        quit()
    csv_fname = new_file = video_fname[:-4] + '_data.csv'

    if not os.path.exists(csv_fname):
        csv_fname = filedialog.askopenfilename(title="Select CSV File")
        csv_fname = change_csv_layout(csv_fname,video_fname)
    # -------------------------------------------------------------------#

    # Initiation---------------------------------------------------------#
    Dataframe = pd.read_csv(csv_fname)
    video = cv2.VideoCapture(video_fname)
    ret, frame = video.read()
    nest = True
    re_gen_nest = False
    name = 'centroid'
    # -------------------------------------------------------------------#

    # Calculate the centroid---------------------------------------------#
    if 'centroid_x' not in Dataframe.columns:
        print('Updating csv file.. [NEW: center of gravity]')
        Dataframe = center_of_gravity(Dataframe)
        Dataframe.to_csv(csv_fname, index=False)
        print('[DONE: center of gravity]')
    # -------------------------------------------------------------------#

    # Calculate the nest state (in/out -- 1/0)--------------------------#
    if nest is True and (re_gen_nest is True or 'nest' not in Dataframe.columns):
        print('Updating csv file.. [NEW: nest state]')
        nest = select_points(frame,'select nest (press ENTER to finish)')
        Dataframe = gen_nest(Dataframe,name,nest[0])
        Dataframe.to_csv(csv_fname, index=False)
        print('[DONE: nest state]')
    # -------------------------------------------------------------------#


    # Set the unit (and plot trajectory)
    pixel_per_cm,Dataframe = gen_trajectory(frame,Dataframe,name,show_image=True)
    print(pixel_per_cm)
    Dataframe.to_csv(csv_fname, index=False)
    # pixel_per_cm = 4.957619820730872    # just for testing


    # Nest analysis (movement v.s. nest state)
    # nest_ana(Dataframe,name,pixel_per_cm,window=4)
    # # test_window_for_nest(Dataframe,name,pixel_per_cm)

    # Kinetics

    kinetics(Dataframe,'tailbase',window=3)

    # Dataframe.to_csv(csv_fname,index=False)
    plt.show()


