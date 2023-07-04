import tkinter as tk
from tkinter import filedialog
import scipy.io
import pandas as pd
import numpy as np

# Create the main window
window = tk.Tk()
window.withdraw()  # Hide the main window

# Prompt the user to select a MATLAB data file
file_path = filedialog.askopenfilename(filetypes=[('MATLAB Data Files', '*.mat')])

# Load the selected MATLAB data file
mat_data = scipy.io.loadmat(file_path)

# Access and process the loaded data as needed
# ...

# Print the loaded variables
# print(mat_data)

# Close the main window
window.destroy()

# Reshape the data to make it 2D
reshaped_data = np.reshape(mat_data, (-1, 1))

# Create a DataFrame from the reshaped data
df = pd.DataFrame(reshaped_data, columns=['your_column_name'])

# Save the DataFrame as a CSV file
df.to_csv(file_path[:-3] + 'csv', index=False)