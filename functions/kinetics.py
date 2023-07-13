import matplotlib.pyplot as plt
import numpy as np

from analysis import pcutoff, freq


def cal_v_a(Dataframe, name,pixel_per_cm, window=11,show=True):
    # Keep window an ODD number to make acceleration accurate
    df = Dataframe.copy()
    df.loc[df[name + '_likelihood'] < pcutoff, [name + '_x', name + '_y']] = np.nan

    Dataframe[name+'_x_win'] = df[name+'_x'].rolling(window, min_periods=1, center=True).apply(lambda x: np.mean(x.dropna()))
    Dataframe[name+'_y_win'] = df[name+'_y'].rolling(window, min_periods=1, center=True).apply(lambda x: np.mean(x.dropna()))

    # 1: Calculate velocity and acceleration
    Dataframe[name + '_v'] = np.linalg.norm(df[[name + '_x', name + '_y']].diff().shift(-1), axis=1)    # pixel per frame
    Dataframe[name + '_v'] = Dataframe[name + '_v'] * freq / pixel_per_cm  # cm per sec

    # 1.5: Discard the ridiculous points
    # [to be completed]
    # Dataframe[name + '_v'] = np.where(Dataframe[name + '_v']>)

    Dataframe[name + '_a'] = Dataframe[name + '_v'].diff() * freq /100/9.8 # g

    # 2: Plot the distribution
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    data = Dataframe[name + '_v'].dropna()
    axes[0].hist(data, bins=np.logspace(np.log10(min(data)), np.log10(max(data)), num=1000),
                 histtype='step', edgecolor='black', linewidth=1.2)
    axes[0].set_xscale('log')
    axes[0].set_xlabel('velocity(cm/s)')

    data = abs(Dataframe[name+'_a'].dropna())
    axes[1].hist(data, bins=np.logspace(np.log10(min(data)), np.log10(max(data)), num=3000),
                histtype='step', edgecolor='black', linewidth=1.2)
    axes[1].set_xscale('log')
    axes[1].set_xlabel('acceleration(g)')
    fig.suptitle('window size='+str(window))

    if show == False:
        plt.clf()
        plt.close()
    else:
        plt.show()

    return Dataframe


def cal_var_traj(Dataframe, name,pixel_per_cm, window=11,show=True):
    dfc = Dataframe.copy()
    dfc.loc[dfc[name + '_likelihood'] < pcutoff, [name + '_x_win', name + '_y_win']] = np.nan
    df = dfc[[name+'_x_win',name+'_y_win']].copy()/pixel_per_cm
    Dataframe[name+'_var']=[np.nan]*len(Dataframe)
    rolling_df = df.rolling(window,min_periods=1,center=True)
    for i, win in enumerate(rolling_df):
        if win.isnull().any().any():
            continue
        Dataframe[name+'_var'][i] = np.var(win.apply(lambda x: np.linalg.norm(x.values - np.mean(x.values, axis=0)), axis=1))


    return Dataframe