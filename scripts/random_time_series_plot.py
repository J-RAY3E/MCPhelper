import matplotlib.pyplot as plt
import numpy as np

# Generate random time series data
time_series = np.random.randn(100)

# Plot the time series
plt.plot(time_series)
plt.title('Random Time Series Plot')
plt.xlabel('Time')
plt.ylabel('Value')
plt.show()
