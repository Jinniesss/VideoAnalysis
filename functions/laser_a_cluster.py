import os.path
from scipy.io import loadmat
from sklearn.mixture import GaussianMixture

from analysis import freq
from functions.file_processing import *
from functions.trajectory_associated import *

import pickle


def fit_gmm(Dataframe, name, n_components=2):
    df = Dataframe.copy()
    df = df.dropna()
    data = abs(df[name])
    data = data[~np.isnan(data)]
    data = data[data != 0]
    data = np.log10(data.values.reshape(-1, 1))

    # Fit GMM with n components
    gmm = GaussianMixture(n_components=n_components)
    gmm.fit(data)

    # Generate data for plotting the PDF
    x = np.linspace(min(data), max(data), 1000).reshape(-1, 1)
    pdf = np.exp(gmm.score_samples(x))

    # Draw vertical dashed lines at the means
    means = gmm.means_.flatten()
    for mean in means:
        plt.axvline(mean, color='g', linestyle='--')

    # Plot the data and PDF
    plt.hist(data, bins=500, density=True, alpha=0.5, label='Data')
    plt.plot(x, pdf, color='red', linestyle='--', label='PDF')
    plt.xlabel('log10(Acceleration)')
    plt.ylabel('Density')
    plt.title('GMM (' + str(n_components) + ' components)')
    plt.legend()
    plt.show()

    # Print the fitting results
    print('GMM Means:', gmm.means_.flatten())
    print('GMM Covariances:', gmm.covariances_.flatten())
    print('GMM Weights:', gmm.weights_)
    print('------------------------------------------------')

# not used
def set_a_cluster(Dataframe, name, a1_max, a2_min):
    if a1_max > a2_min:
        print('Wrong value of thresholds: ', a1_max, ', ', a2_min)
        return
    Dataframe[name + '_a_c'] = 0
    Dataframe[name + '_a_c'] = np.where(abs(Dataframe[name + '_a']) < a1_max, 1,
                                        np.where(abs(Dataframe[name + '_a']) > a2_min, 2, 0))

    print('1st cluster: ', Dataframe[name + '_a_c'].value_counts()[1])
    print('2nd cluster: ', Dataframe[name + '_a_c'].value_counts()[2])
    print('No cluster: ', Dataframe[name + '_a_c'].value_counts()[0])

    return Dataframe


def laser_a_cluster(Dataframe, name, dataname, re_gen_plots=False):
    fit_gmm(Dataframe, name + '_a', n_components=3)

    a1cluster_p = dataname + '_a1_max.pickle'
    a2cluster_p = dataname + '_a2_min.pickle'
    a1_max = a2_min = None

    if not os.path.exists(dataname + '_cluster1.pickle') \
            or not os.path.exists(dataname + '_laser_a_cluster1.png') \
            or re_gen_plots is True:
        # Load laser file
        laser_fname = dataname + '.mat'
        if os.path.exists(dataname[:-7]+'laser.mat'):
            laser_fname = dataname[:-7]+'laser.mat'
        elif not os.path.exists(laser_fname):
            print('Waiting for laser file selection...')
            laser_fname = askopenfilename(filetypes=[("MATLAB Files", "*.mat")])
        mat_data = loadmat(laser_fname)
        try:
            laser = mat_data['laser']
        except:
            print('Current laser file is randomly generated')
            laser = mat_data['laser_r']
        laser_frame = np.round(laser[:, 0] * 10 + 0.05 * 10 / 2).astype(int)  # 0.05 -- duration time
        # laser_frame_cluster = Dataframe[name + '_a_c'][laser_frame].values
        # print(laser_frame_cluster)
        pre = []
        # print(laser_frame)
        for i, cur_frame in enumerate(laser_frame):
            x = np.arange(-1, 5, 1 / freq)
            pre.append(abs(Dataframe[name + '_a'][cur_frame - 10:cur_frame]).mean())

        log_pre = np.log10(pre)
        plt.hist(log_pre, bins=200, density=True, alpha=0.5)
        plt.title('log distribution of photometry during the 10s before laser')
        plt.show()
        c_all = []
        c1 = []
        c2 = []
        x = np.arange(-1, 5, 1 / freq)

        if os.path.exists(a1cluster_p):
            with open(a1cluster_p, 'rb') as file:
                a1_max = pickle.load(file)
            with open(a2cluster_p, 'rb') as file:
                a2_min = pickle.load(file)
            print(np.log10(a1_max), np.log10(a2_min))
        else:
            print('The code is still stupid so please manually set the thresholds..')
            a1_max = 10 ** float(input("Set the left threshold (max value for cluster 1): "))
            a2_min = 10 ** float(input("Set the right threshold (min value for cluster 2): "))
            # Dataframe = set_a_cluster(Dataframe,name,a1_max,a2_min)
            with open(a1cluster_p, 'wb') as file:
                pickle.dump(a1_max, file)
            with open(a2cluster_p, 'wb') as file:
                pickle.dump(a2_min, file)

        # plot for all
        for i, pre_m in enumerate(pre):
            cur_frame = laser_frame[i]
            li = abs(Dataframe[name + '_a'][cur_frame - 10:cur_frame + 50])
            if li.isna().any() or len(li)!=60:
                continue
            c_all.append(li)

        plt.axvline(x=0, color='grey', linestyle='--')
        plt.axvline(x=0.5, color='grey', linestyle='--')
        if c_all:
            plt.plot(x, np.mean(np.array(c_all), axis=0), color='black', label='all')
            ste_all = np.std(np.array(c_all), axis=0) / np.sqrt(len(c_all))
            plt.fill_between(x, np.mean(np.array(c_all) - ste_all, axis=0), np.mean(np.array(c_all) + ste_all, axis=0),
                             color='gray', alpha=0.3)

        plt.xlabel('Time(sec)')
        plt.ylabel('Acceleration(g)')
        # plt.title('All: ' + str(len(c_all)))
        # plt.ylim([0, 1.3*np.max(np.mean(np.array(c_all),axis=0))])
        # plt.savefig(dataname + '_laser_a_cluster_all.png')
        # plt.show()

        # plot for cluster 1
        for i, pre_m in enumerate(pre):
            cur_frame = laser_frame[i]
            if pre_m < a1_max:
                li = abs(Dataframe[name + '_a'][cur_frame - 10:cur_frame + 50])
                if li.isna().any():
                    continue
                li = li.tolist()
                c1.append(li)
                # plt.plot(x, li, color='red', alpha=0.3)

        # plt.axvline(x=0, color='black', linestyle='--')
        if len(c1) != 0:
            plt.plot(x, np.mean(np.array(c1), axis=0), color='red', label='cluster 1')
            ste_a1 = np.std(np.array(c1), axis=0) / np.sqrt(len(c1))
            plt.fill_between(x, np.mean(np.array(c1) - ste_a1, axis=0), np.mean(np.array(c1) + ste_a1, axis=0),
                             color='red', alpha=0.2)
        # plt.xlabel('Time(sec)')
        # plt.ylabel('Acceleration(g)')
        # plt.title('Cluster 1: ' + str(len(c1)))
        # plt.ylim([0, 1.3*np.max(np.mean(np.array(c1),axis=0))])
        # plt.savefig(dataname + '_laser_a_cluster1.png')
        # plt.show()

        # plot for cluster 2
        for i, pre_m in enumerate(pre):
            cur_frame = laser_frame[i]
            if pre_m > a2_min:
                li = abs(Dataframe[name + '_a'][cur_frame - 10:cur_frame + 50])
                if li.isna().any():
                    continue
                li = li.tolist()
                c2.append(li)
                # plt.plot(x, li, color='blue', alpha=0.3)

        if len(c2) != 0:
            plt.plot(x, np.mean(np.array(c2), axis=0), color='blue', label='cluster 2')
            ste_a2 = np.std(np.array(c2), axis=0) / np.sqrt(len(c2))
            plt.fill_between(x, np.mean(np.array(c2) - ste_a2, axis=0), np.mean(np.array(c2) + ste_a2, axis=0),
                             color='blue', alpha=0.2)

        # plt.axvline(x=0, color='black', linestyle='--')

        # plt.xlabel('Time(sec)')
        # plt.ylabel('Acceleration(g)')
        # plt.title('Cluster 2: ' + str(len(c2)))
        # plt.savefig(dataname + '_laser_a_cluster2.png')
        plt.savefig(dataname + '_laser_a.png')
        plt.legend()
        plt.show()

        print('Cluster 1: ', len(c1))
        print('Cluster 2: ', len(c2))
        print('All: ', len(c_all))

        with open(dataname + '_cluster1.pickle', 'wb') as file:
            pickle.dump(c1, file)
        with open(dataname + '_cluster2.pickle', 'wb') as file:
            pickle.dump(c2, file)
        with open(dataname + '_cluster_all.pickle', 'wb') as file:
            pickle.dump(c_all, file)
