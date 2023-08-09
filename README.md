# Behavior Analysis

_Jinnie 2023.7_


**Pipelines**: 
+ For photometry v.s. nest states:
    
  [ana_for_folders.py](ana_for_folders.py) >> [moving_ana_sum.m](moving_ana_sum.m) >> [phot_for_folders.m](phot_for_folders.m)

  both should select the mouse folder (e.g. M101)
  
+ For photometry v.s. behavioral states:
    
  [ana_for_folders.py](ana_for_folders.py) >> [phot_vs_behav_state_for_folders.m](phot_vs_behav_state_for_folders.m)

  both should select the mouse folder (e.g. M101)

+ For a realtime check of behavioral states:

  [ana_for_folders.py](ana_for_folders.py) >> [realtimeGUI.py](realtimeGUI.py)

  For the latter script, a csv file that contains the wanted column should be selected. 
      (e.g. movement_state -- 'M101_S1_mov_state.csv', nose_a -- 'M101_S1_data.csv')
---
#### runnable Py files:

+  [realtimeGUI.py](realtimeGUI.py) 

    shows the real-time change of several parameters along with the video.
    
    *input: video file, data file [in converted format]*
****
  

+  [analysis.py](analysis.py) 

    analyzes and updates the csv data from DEEPLABCUT, also generates some plots.
    
    *input: video file, (several assignable variables)*
    
    **[Select the folder where the video and csv files are.]**
    
    **[Nest selection should be anticlockwise from the top left corner.]**

---

+  [ana_for_folders.py](ana_for_folders.py)
  
    calls [analysis.py](analysis.py) for all the videos in a folder.
    
    **[Select the folder that includes all the video folders (each of which contains a video and other corresponding files).]**

---

#### Functions called by  [analysis.py](analysis.py) in folder [functions](functions):

+  [file_processing.py](functions/file_processing.py) 

      ```py
      def change_csv_layout(original_file,video_fname):
        ...
        return new_file
      ```
    + converts the format of original  csv file.
    + The `new_file` has only one head row. Column names end with `_x`, `_y` or `_likelihood` for each bodypart.
    + The `new_file` will be saved as `video_fname_data.csv` under the same folder with the video file.
    + The original csv file won't be modified.

     ```py
     def get_frame_from_video(video_fname, frame_number=10,rand=False):
        ...
        return frame
     ```
    + return the specific `frame` of a video
    + When `rand` is True, frame_number will be a random valid value.


+  [roi_associated.py](functions/roi_associated.py) 

      ```py
      def select_points(frame,wname):  
        # frame: a frame of the video that would be the 	 
        # 			 background image of selection []
        # wname: window name [string]
        ...
        return selected_points,frame
      ```

    + displays a window for user to select points (for nest/cage/...)

    + In the GUI, 

        click left mouse button to add a point;

        press `Backspace` or `Delete` to delete the last selected point; 

        press `R` to change a random frame;
      
        press `Enter` to finish.

    ```py
    def is_in_roi(x, y, roi_arr):
      # roi_arr: coordinates of a group of points
      #          same format as the output of select_points()
      ...
      return True/False
    ```

   + returns whether the input point is in the input roi (an array of points).

   ```py
   def corrected(frame):
     ...
     # M: transfrom matrix
     return M,corrected_coor,pixel_per_cm
   ```

   + lets user select the four corners of the cage and calculates the corrected coordinate of it, along with the transform matrix `M` and `pixel_per_cm`.
   + `pixel_per_cm` only adapts to the transformed coordinates.

   ```py
   def transform(df,name,M):
     # df: dataframe
     # name: the name of the bodypart of interest
     ...
     return ndf
     # ndf: new dataframe
   ```

    + transforms column `name_x` and `name_y` using  `M` matrix
    + In other words, correct the coordinate of `name` according to the corrected cage.

   ```py
   def area_pixel(points):
     ...
     return area    # unit -- pixel^2
   ```

    + return the area of the polygon
    + (for calculating nest area percentage)



+  [trajectory_associated.py](functions/trajectory_associated.py) 

   ```py
   def masked(df,name,nest = False):
     ...
     return df
   ```

    + returns the new df with `name`'s coordinates masked if `name_likelihood` < `pcutoff` (which is assigned in [analysis.py](analysis.py))
    + if `nest` is `True`, `df['nest']` will also be masked according to same rule.

    ```py
    def plot_trajectory(df,name,bg=None,pixel_per_cm=None):
     # bg: background image of the plot  
      ...
    ```

    + plots the trajectory using the coordinates of `name` in `df`.
    + If `pixel_per_cm == True`, the unit will be cm; else will be pixel. 
    + If `bg is not None`, the plot would use this image to be background.

    ```py
    def center_of_gravity(df):
      ...
      return df
    ```

    + computes the coordinate of center of gravity and saves it in the returned `df`

      (saved as `centroid_x`, ...)

    + Outer body parts are used in the computation.

    + `centroid_likelihood` is the minimum of that of the outer body parts.

    ```py
    def calculate_transformation(frame,Dataframe):
      ...
      return pixel_per_cm,Dataframe_t,result,corrected_coor,ori_area
    ```

    + corrects the dataframe according to the selected corners



+ [kinetics.py](functions%2Fkinetics.py)
  ```py
  def cal_v_a(Dataframe, name,pixel_per_cm, window=11,show=True):
    ...
    return Dataframe
  ```
  + calculates `name_v` and `name_a` and plot the distribution
  + One of the slowest parts. (to be improved)

  ```py
  def show_v_a(Dataframe, name,foldername):
    ...
    return Dataframe
  ```
  + only shows the distribution of `name_v` and `name_a` 
   (when they have been calculated).

  ```py
  def cal_var_traj(Dataframe, name,pixel_per_cm, window=11,show=True):
    ...
    return Dataframe
  ```
  + calculates the `name_var`
  + One of the slowest parts. (to be improved)


+ [nest_analysis.py](functions%2Fnest_analysis.py)
  ```py
  def gen_nest(df, name, nest):
    ...
    return df
  ```
  + calculates the column `nest` (0/1)

  ```py
  def nest_ana(Dataframe, name, pixel_per_cm, dataname, window=3, show=True):
    ...
    return moving_rate_out
  ```
  + calculates the time and moving distance in/out of nest,
  saves them in `dataname_Moving_ana.mat`, and plots the result.

  ```py
  def test_window_for_nest(Dataframe, name, pixel_per_cm):
    ...
    return
  ```
  + plots the v and a with different window sizes.
  + Only for test.

  ```py
  def area_of(points,pixel_per_cm,dataname,save=True):
    ...
    if save is True:
      nest_area = {'nest_area': area}
      scipy.io.savemat(dataname + '_nest_area.mat',nest_area)
      print('Area of Nest saved.')
    else:
      return area   # unit -- cm^2
  ```
  + calculates the area of a polygon.


+ [laser_a_cluster.py](functions%2Flaser_a_cluster.py)
  ```py
  def fit_gmm(Dataframe, name, n_components=2):
    ...
    print('GMM Means:', gmm.means_.flatten())
    print('GMM Covariances:', gmm.covariances_.flatten())
    print('GMM Weights:', gmm.weights_)
    print('------------------------------------------------')
  ```
  + fits the distribution of `log(name_a)` with GMM and shows the result.

  ```py
  def laser_a_cluster(Dataframe, name, dataname, re_gen_plots=False):
    ...
  ```
  + calls `fit_gmm`, gets user input, calculates the acceleration cluster, 
  plots the result and saves everything to pickle files..
---
#### .m files
+ [clustering.m](clustering.m)

    should be run under the video folder (e.g. M111_S1).
    
    Creates a table `name_mov_state.csv` containing columns
    `movement_state`, `sleep_state`, `bp_movement_state` for each bodypart, 
    and `nest`.

+ [moving_ana_sum.m](moving_ana_sum.m)

    should be run under the mouse folder (e.g. M111).
    
    `name_Moving_ana.mat` and `name_nest_area.mat` are needed for each video.
    
    Creates `name_moving_ana_summary.mat` that includes the area of nest, 
    and moving time/rate in/out of nest.

+ [photometry_nest.m](photometry_nest.m)

    should be run under the video folder (e.g. M111_S1).
    
    Creates `name_phot_ana.mat` and plots.

+ [phot_for_folders.m](phot_for_folders.m)

    should be run under the mouse folder (e.g. M111).

    Calls [phot_vs_behav_state.m](phot_vs_behav_state.m).

    Creates `name_phot_ana_summary.mat` and plots.

+ [phot_vs_behav_state.m](phot_vs_behav_state.m)

    should be run under the video folder (e.g. M111_S1).
    
    Calls [clustering.m](clustering.m).
    
    Creates `name_phot_vs_beh.mat` and plots.

+ [phot_vs_behav_state_for_folders.m](phot_vs_behav_state_for_folders.m)

    should be run under the mouse folder (e.g. M111).
    
    Calls [phot_vs_behav_state.m](phot_vs_behav_state.m).
    
    Creates `name_phot_beh_summary.mat` and plots.

+ [ran_laser.m](ran_laser.m)

    should be run under the same folder where `laser.m` is.
    
    Creates a random set of laser time `laser_r.m`.
