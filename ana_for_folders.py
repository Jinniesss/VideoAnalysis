import os.path
import os
import pickle
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter import Tk
import matplotlib.pyplot as plt
import numpy as np
import analysis
from analysis import freq

if __name__ == '__main__':


    # ALWAYS SELECT THE FOLDER THAT CONTAINS FOLDERS (EACH OF WHICH INCLUDES A VIDEO)...
    # (always true here (file selection
    if True:
        root = Tk()
        root.withdraw()
        folder_path = askdirectory()
        if folder_path == '':
            print('User exited.')
            quit()

        # Get a list of all directories (folders) in the specified folder
        folder_list = [folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]
        n = len(folder_list)
        if len(folder_list)==0:
            print('Check your selection.')
            quit()

    # TURN ON THE FUNCTION OF INTEREST BELOW BY SETTING IT 'TRUE':

    # Patch process of raw data -------------------------------------#
    if True:
        for i,folder in enumerate(folder_list):
            analysis.main(folder_path+'/'+folder)
            print('Folder '+folder+' Done! (',i+1,'/',n,')')
            print('------------------------------------------------')
    # ---------------------------------------------------------------#

    # Acceleration of cluster 1 after laser -------------------------#
    if False:
        c1=[]
        x = np.arange(-1, 5, 1 / freq)

        for i, folder in enumerate(folder_list):
            if folder == 'M192_S1':
                continue
            vfolder_path = os.path.join(folder_path,folder)
            c1_path = os.path.join(vfolder_path,folder + '_cluster1.pickle')
            if not os.path.exists(c1_path):
                print(c1_path,'not found')
                quit()
            else:
                with open(c1_path, 'rb') as file:
                    cur_c1 = pickle.load(file)
                print(folder,':',len(cur_c1))

            plt.plot(x, np.mean(np.array(cur_c1), axis=0), color='red',alpha=0.4)
            c1.append(np.mean(np.array(cur_c1), axis=0))

        # print('All:',len(c1))
        # print(len(c1))
        plt.axvline(x=0, color='black', linestyle='--')
        plt.plot(x, np.mean(np.array(c1), axis=0), color='black')
        plt.xlabel('Time(sec)')
        plt.ylabel('Acceleration(g)')
        plt.title('Cluster 1: ' + str(len(c1)))
        # plt.ylim([0, max(np.mean(np.array(c1), axis=0))])
        plt.show()
    # ---------------------------------------------------------------#

    # All Acceleration after laser ----------------------------------#
    if False:
        c1=[]
        x = np.arange(-1, 5, 1 / freq)

        for i, folder in enumerate(folder_list):
            if folder == 'M192_S1':
                continue
            vfolder_path = os.path.join(folder_path,folder)
            c1_path = os.path.join(vfolder_path,folder + '_cluster_all.pickle')
            if not os.path.exists(c1_path):
                print(c1_path,'not found')
                quit()
            else:
                with open(c1_path, 'rb') as file:
                    cur_c1 = pickle.load(file)
                print(folder,':',len(cur_c1))

            plt.plot(x, np.mean(np.array(cur_c1), axis=0), color='red',alpha=0.4)
            c1.append(np.mean(np.array(cur_c1), axis=0))

        # print('All:',len(c1))
        # print(len(c1))
        plt.axvline(x=0, color='black', linestyle='--')
        plt.plot(x, np.mean(np.array(c1), axis=0), color='black')
        plt.xlabel('Time(sec)')
        plt.ylabel('Acceleration(g)')
        plt.title('All: ' + str(len(c1)))
        # plt.ylim([0, max(np.mean(np.array(c1), axis=0))])
        plt.show()
    # ---------------------------------------------------------------#


