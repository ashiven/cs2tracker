import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('output.csv', names=['Date', 'Price'])

df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S')

df.set_index('Date', inplace=True)

plt.plot(df.index, df['Price'])

plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Price over time')

plt.show()
