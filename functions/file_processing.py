import tkinter as tk
from tkinter import filedialog
import csv
import re
def change_csv_layout(original_file,video_fname):

    # Create a new CSV file
    new_file = video_fname[:-4] + '_data.csv'
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
