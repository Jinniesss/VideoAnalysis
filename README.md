# Behavior Analysis

Files with main function:

+  [realtimeGUI.py](realtimeGUI.py) 

  shows the real time change of several parameters along with the video.

  *input: video file, data file [in converted format]*

+  [analysis.py](analysis.py) 

  analyzes and updates the csv data from DEEPLABCUT, also generates some plots of interest

  *input: video file, (several assignable variables)*

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

  + 