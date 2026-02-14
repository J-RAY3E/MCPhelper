import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
file_path = 'variant_4.csv'
data = pd.read_csv(file_path)

# Calculate statistics
max_value = data['Value'].max()
min_value = data['Value'].min()
mean_value = data['Value'].mean()

# Plot histogram
plt.hist(data['Value'], bins=10)
plt.title('Histogram of Variant 4 Data')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.show()