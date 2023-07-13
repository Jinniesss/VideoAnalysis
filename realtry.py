import scipy.io

# Variables to save
var1 = [1, 2, 3, 4, 5]
var2 = {'name': 'John', 'age': 25}
var3 = 10

# Create a dictionary to store variables
data = {'a': var1, 'var2': var2, 'var3': var3}

# Save variables to a MATLAB file
scipy.io.savemat('variables.mat', data)
