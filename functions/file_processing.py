import tkinter as tk
from tkinter.filedialog import askopenfilename
import csv
import cv2
import random
import re
def change_csv_layout(original_file,dataname):
    # Create a new CSV file
    new_file = dataname + '_data.csv'
    print('Converting the layout of csv file...')
    with open(original_file, 'r') as csv_file:
        reader = csv.reader(csv_file)
        # Skip the first row
        next(reader)

        # Combine the second and third rows
        row_2 = next(reader)
        row_3 = next(reader)
        combined_row = [x + '_' + y for x, y in zip(row_2, row_3)]

        with open(new_file, 'w', newline='') as new_csv_file:
            writer = csv.writer(new_csv_file)
            # Write the combined row to the new CSV file
            writer.writerow(combined_row[1:])

            # Write the remaining rows to the new CSV file
            for row in reader:
                writer.writerow(row[1:])

    print('New csv file saved. [file name: ',new_file,']')
    return new_file

def get_frame_from_video(video_fname, frame_number=10,rand=False):
    video_capture = cv2.VideoCapture(video_fname)
    # Get the total number of frames in the video
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_number == -1:
        frame_number = total_frames-1

    if frame_number < 0 or frame_number >= total_frames:
        raise ValueError("Invalid frame number. Must be between 0 and {}".format(total_frames - 1))

    if rand is True:
        frame_number = int(random.uniform(0,total_frames-1))
        print('Frame: ', frame_number, '/', total_frames)

    # Set the position to the specified frame number
    video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    # Read the frame at the specified position
    ret, frame = video_capture.read()

    # Release the video capture object
    video_capture.release()

    if not ret:
        raise ValueError("Unable to read the frame from the video.")

    return frame