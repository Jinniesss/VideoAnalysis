import matplotlib.pyplot as plt
import numpy as np

# Create a plot
plt.axvline(x=1, color='blue', linestyle='--', label='x=1')
plt.axvline(x=2, color='red', linestyle='--', label='x=2')

# Fill the area between the vertical lines
plt.fill_betweenx([0, 1], 1, 2, color='green', alpha=0.3, label='area between x=1 and x=2')

# Add labels, title, and legend
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Fill Area Between Vertical Lines')
plt.legend()

# Show the plot
plt.show()
