# Behavior Analysis

Files with main function:

+  [realtimeGUI.py](realtimeGUI.py) 

  shows the real time change of several parameters along with the video.

  *input: video file, data file [in converted format]*

+  [analysis.py](analysis.py) 

  analyzes and updates the csv data from DEEPLABCUT, also generates some plots of interest

  *input: video file, (several assignable variables)*

---

Functions called by  [analysis.py](analysis.py) in folder [functions](functions):

+  [file_processing.py](functions/file_processing.py) 

  ```py
  def change_csv_layout(original_file,video_fname)
    ...
    return new_file
  ```

  + converts the format of original  csv file.
  + The `new_file` has only one head row. Column names end with `_x`, `_y` or `_likelihood` for each bodypart.
  + The `new_file` will be saved as `video_fname_data.csv` under the same folder with the video file.
  + The original csv file won't be modified.

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

    press `Backspace` to delete the last selected point;

    press `Enter` to finish.

  

  ```py
  def is_in_roi(x, y, roi_arr):
    # roi_arr: coordinates of a group of points
    #          same format as the output of select_points()
  	...
  	return True/False
  ```

  + returns whether the input point is in the input roi.

  

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

  

  ```python
  def center_of_gravity(df):
  	...
    return df
  ```

  + computes the coordinate of center of gravity and saves it in the returned `df`

    (saved as `centroid_x`, ...)

  + Outer body parts are used in the computation.

  + `centroid_likelihood` is the minimum of that of the outer body parts.

  

  ```py
  def gen_trajectory(frame,Dataframe,name,show_image=True):
    ...
    return pixel_per_cm,Dataframe_t
  ```

  + calls functions `corrected`, `transform`, and `plot_trajectory`
  + The main function only needs to call this.

