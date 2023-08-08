from analysis import freq
from functions.roi_associated import *
import matplotlib.pyplot as plt
import numpy as np
import scipy.io

from functions.trajectory_associated import masked


def gen_nest(df, name, nest):
    nest = [(int(x), int(y)) for x, y in nest]
    nest = np.array(nest)
    df['nest'] = [0] * len(df)
    # print(len(nest))
    # # nest = nest.reshape(len(nest),1,2).astype(np.int64)
    # print(nest)
    # print(type(nest))

    for i in range(len(df)):
        try:
            x = int(df[name + '_x'][i])
            y = int(df[name + '_y'][i])
        except ValueError:
            continue
        if is_in_roi(x, y, nest):
            df['nest'][i] = 1
    return df


def nest_ana(Dataframe, name, pixel_per_cm, dataname, window=3, show=True):
    Dataframe = masked(Dataframe, name, nest=True)
    # 1: stay time
    fig, axs = plt.subplots(1, 3, figsize=(12, 5))
    nest_state = Dataframe['nest']
    in_nest_frame_num = nest_state.value_counts().get(1, 0)
    out_nest_frame_num = nest_state.value_counts().get(0, 0)
    # Set the names for each bar
    names = ['In Nest', 'Out of Nest']
    counts = [in_nest_frame_num / 10, out_nest_frame_num / 10]
    # Create the histogram

    axs[0].pie(counts, labels=names, autopct='%1.1f%%')
    axs[0].set_title('Duration of Stay')
    axs[1].bar(names, counts, width=0.5)
    # axs[1].set_xlabel('Nest State')
    axs[1].set_ylabel('Duration of Stay(sec)')
    plt.subplots_adjust(wspace=1)

    # 2: moving rate in each state
    v_in_nest_frame_num = 0  # valid frame number
    v_out_nest_frame_num = 0
    in_nest_distance = 0
    out_nest_distance = 0

    columns = ['nest',name+'_x',name+'_y',name+'_likelihood']
    new_Df = Dataframe[columns].copy()
    # Identify the groups based on the change in values of column 'nest'
    groups = (new_Df['nest'].diff() != 0).cumsum()

    # Group the DataFrame based on the identified groups
    grouped_df = new_Df.groupby(groups)

    for group_num, group_data in grouped_df:
        cur_nest_state = group_data['nest'][group_data.index[0]]
        if np.isnan(cur_nest_state):
            continue

        df = group_data.copy()
        df = df.rolling(window=window).mean()
        df = df.dropna()
        df['distance'] = np.linalg.norm(df[[name + '_x', name + '_y']].diff(), axis=1)
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
    moving_rate_in = in_nest_distance / v_in_nest_frame_num / pixel_per_cm * freq  # cm per sec
    moving_rate_out = out_nest_distance / v_out_nest_frame_num / pixel_per_cm * freq

    axs[2].plot([0, 1], [moving_rate_in, moving_rate_out], '-', lw=2, color='gray')
    axs[2].bar(0, moving_rate_in, color='blue', alpha=0.3, width=0.5)
    axs[2].bar(1, moving_rate_out, color='red', alpha=0.3, width=0.5)

    axs[2].scatter(np.zeros_like(moving_rate_in), moving_rate_in, color='blue', label='In-Nest')
    axs[2].scatter(np.ones_like(moving_rate_out), moving_rate_out, color='red', label='Out-of-Nest')
    axs[2].set_ylabel('Moving Rate (cm/s)')
    axs[2].set_xticks([0, 1])
    axs[2].set_xticklabels(['In Nest', 'Out of Nest'])
    # axs[2].set_ylim(0,1.3*moving_rate_out)
    plt.savefig(dataname + '_nest_ana.png')

    # save to mat file:
    nest_result = {'time_in_nest': v_in_nest_frame_num / freq,
                   'time_out_of_nest': v_out_nest_frame_num / freq,
                   'distance_in_nest': in_nest_distance / pixel_per_cm,
                   'distance_out_of_nest': out_nest_distance / pixel_per_cm}

    scipy.io.savemat(dataname + '_Moving_ana.mat', nest_result)

    if show == False:
        plt.clf()
        plt.close()
    else:
        plt.show()

    return moving_rate_out


def test_window_for_nest(Dataframe, name, pixel_per_cm):
    rate = []
    for i in range(1, 101):
        print('Calculating -- ', i, '/100...')
        rate.append(nest_ana(Dataframe, name, pixel_per_cm, window=i, show=False))
    plt.clf()
    plt.plot(range(1, 101), rate, '-o')
    plt.show()


def area_of(points,pixel_per_cm,dataname,save=True):
    points_np = np.array(points, dtype=np.int32)
    points_np = points_np.reshape((-1, 1, 2))
    area = cv2.contourArea(points_np)    # unit -- pixel^2
    area = area/pixel_per_cm/pixel_per_cm
    if save is True:
        nest_area = {'nest_area': area}
        scipy.io.savemat(dataname + '_nest_area.mat',nest_area)
        print('Area of Nest saved.')
    else:
        return area