import cv2
import numpy as np

def polygon_area(points):
    # Create a numpy array of the points in the format expected by cv2.contourArea()
    points_np = np.array(points, dtype=np.int32)

    # Reshape the points array to have shape (number_of_points, 1, 2)
    points_np = points_np.reshape((-1, 1, 2))

    # Calculate the area using cv2.contourArea()
    area = cv2.contourArea(points_np)

    return abs(area)

# Example usage:
# Define the polygon vertices as (x, y) coordinates
polygon_points = [(0, 0), (4, 0), (4, 3), (0, 3)]

# Calculate the area of the polygon
area = polygon_area(polygon_points)

print("Area of the polygon:", area)
