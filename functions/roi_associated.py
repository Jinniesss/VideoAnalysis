import pickle

import numpy as np
import pandas as pd
import cv2
import math

import scipy

from functions.file_processing import get_frame_from_video

def select_points(frame,wname,dataname=None,is_video=False,v_fname=None,frame_number=10):
    print('Waiting for points selection: '+wname+' ...')
    # Global variables to store the selected points
    selected_points = []
    current_point = 0
    if is_video is True:
        frame = get_frame_from_video(v_fname,frame_number=frame_number)
    # Mouse callback functions
    def add_point(event, x, y, flags, param):
        nonlocal selected_points, current_point

        if event == cv2.EVENT_LBUTTONDOWN:
            frame_c = frame.copy()
            # Save the selected point
            selected_points.append((x, y))
            current_point += 1

            cv2.circle(frame_c, (x, y), 5, (0, 0, 255), -1)
            cv2.drawContours(frame_c,[np.array(selected_points)],0,(0, 0, 255),2)
            cv2.imshow(wname, frame_c)

    def del_point():
        nonlocal selected_points, current_point
        frame_c = frame.copy()
        selected_points.pop()
        if current_point == 0:
            cv2.imshow(wname, frame_c)
            return
        current_point -= 1
        if current_point == 0:
            cv2.imshow(wname, frame_c)
            return

        cv2.circle(frame_c, selected_points[current_point-1], 5, (0, 0, 255), -1)
        cv2.drawContours(frame_c, [np.array(selected_points)], 0, (0, 0, 255), 2)
        cv2.imshow(wname, frame_c)

    def save_nest_img():
        nonlocal selected_points, current_point
        frame_c = frame.copy()
        cv2.drawContours(frame_c, [np.array(selected_points)], 0, (0, 0, 255), 2)
        cv2.imwrite(dataname+'_nest.jpg', frame_c)

    def rand_frame():
        nonlocal selected_points,current_point,frame
        frame = get_frame_from_video(v_fname,rand=True)
        frame_c = frame.copy()
        if current_point != 0:
            cv2.circle(frame_c, selected_points[current_point - 1], 5, (0, 0, 255), -1)
            cv2.drawContours(frame_c, [np.array(selected_points)], 0, (0, 0, 255), 2)
        cv2.imshow(wname, frame_c)

    # Create a window to display the image
    cv2.namedWindow(wname)

    # Register the mouse callback function
    cv2.setMouseCallback(wname, add_point)

    # Display the image
    cv2.imshow(wname, frame)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # press 'Enter' key to finish
            print('Selection finished.')
            cv2.destroyAllWindows()
            if dataname is not None:
                save_nest_img()
            break
        elif key == 127 or key == 8:  # press 'Backspace' or 'Delete' key to delete last point
            if current_point > 0:
                del_point()
        elif key == 114 and is_video is True:   # press 'r' to display another random frame
            rand_frame()

    return selected_points,frame

def transform(df,name,M):
    points = df[[name+'_x', name+'_y']].values.astype(np.float32)
    transformed_points = cv2.perspectiveTransform(points.reshape(-1, 1, 2), M)
    df_temp = pd.DataFrame({name+ '_x': transformed_points[:, 0, 0], name+'_y': transformed_points[:, 0, 1]})
    ndf=df
    ndf[name + '_x'] = df_temp[name + '_x']
    ndf[name + '_y'] = df_temp[name + '_y']

    return ndf

def is_in_roi(x, y, roi_arr):
    # print(type(roi_arr))
    # print(type((x,y)))
    if cv2.pointPolygonTest(roi_arr, (x,y), False) >= 0:
        return True
    else:
        return False

def corrected(frame):


    corners, marked_frame = select_points(frame,'select corners (press ENTER to finish)')
    ori_area = area_pixel(corners)
    corners = np.array(corners, dtype=np.float32)
    from analysis import real_width,real_length
    real_width = real_width/0.39370  # cm
    real_length = real_length/0.39370    # cm

    w1 = (corners[3][0] - corners[0][0]) ** 2 + (corners[3][1] - corners[0][1]) ** 2
    w2 = (corners[2][0] - corners[1][0]) ** 2 + (corners[2][1] - corners[1][1]) ** 2
    width = (math.sqrt(w1)+math.sqrt(w2))/2   # width in pixel
    # width = corners[3][0]-corners[0][0]
    pixel_per_cm = width / real_width
    length = int(pixel_per_cm * real_length)
    width = int(width)
    corrected_coor = np.float32(
        [[-width / 2, -length / 2], [-width / 2, length / 2], [width / 2, length / 2], [width / 2, -length / 2]])
    image_w = frame.shape[1]
    image_h = frame.shape[0]
    corrected_coor += np.float32([image_w / 2, image_h / 2])

    M = cv2.getPerspectiveTransform(corners, corrected_coor)
    return M,corrected_coor,pixel_per_cm,ori_area

def area_pixel(points):
    points_np = np.array(points, dtype=np.int32)
    points_np = points_np.reshape((-1, 1, 2))
    area = cv2.contourArea(points_np)  # unit -- pixel^2

    return area