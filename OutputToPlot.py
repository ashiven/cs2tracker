import csv
import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

def parse_row(row):
    date_str, price_str = row
    price = float(price_str[:-1])
    return date_str, price

filename = 'output.csv'

# Read data from CSV file
dates = []
dollars = []
euros = []
row_num = 0
with open(filename, 'r', newline='', encoding = 'utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        row_num += 1
        date, price = parse_row(row)
        if row_num % 2 == 0:
            euros.append(price)
        else:
            dollars.append(price)
            dates.append(date)

datesp = []

for date_str in dates:
    date = datetime.datetime.strptime(date_str[:-9], '%Y-%m-%d')
    datesp.append(date)

# Plot data
fig, ax = plt.subplots()
ax.plot(datesp, dollars, label='Dollars')
ax.plot(datesp, euros, label='Euros')
ax.set_xlabel('Date')
ax.set_ylabel('Price')
ax.set_title('Price over Time')
ax.legend()

# Format x-axis to only show day, month, and year
date_form = DateFormatter("%d-%m-%Y")
ax.xaxis.set_major_formatter(date_form)
fig.autofmt_xdate() # Rotate and align x-axis labels

plt.show()