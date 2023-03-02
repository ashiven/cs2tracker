import pandas as pd
import matplotlib.pyplot as plt

# Load data from CSV file
df = pd.read_csv('output.csv', names=['Date', 'Price'])

# Convert Date column to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S')

# Set Date column as index
df.set_index('Date', inplace=True)

# Plot price over time
plt.plot(df.index, df['Price'])

# Add labels and title
plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Price over time')

# Show plot
plt.show()
