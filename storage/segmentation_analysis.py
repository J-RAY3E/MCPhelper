import pandas as pd

# Read the CSV file
data = pd.read_csv('variant_4.csv')

# Calculate statistics
max_value = data['Value'].max()
min_value = data['Value'].min()
mean_value = data['Value'].mean()

# Print the statistics
print(f'Max: {max_value}')
print(f'Min: {min_value}')
print(f'Mean: {mean_value}')