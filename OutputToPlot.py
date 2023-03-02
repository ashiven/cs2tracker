import csv
import datetime
import matplotlib.pyplot as plt
import re

def parse_row(row):
    # Extract date and price from row
    date_str, price_str = row

    # Remove currency symbol and any non-numeric characters from price string
    if row_num % 2 == 0:
        price_str = re.sub(r'[^\d\.]+', '', price_str)
    else:
        price_str = re.sub(r'[^\d\,]+', '', price_str)
        price_str = price_str.replace(',', '.')

    # Convert date and price to datetime object and float, respectively
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
    price = float(price_str)

    return date, price

filename = 'output.csv'

# Read data from CSV file
dates = []
dollars = []
euros = []
row_num = 0
with open(filename, 'r', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader) # skip header row
    for row in reader:
        row_num += 1
        date, price = parse_row(row)
        dates.append(date)
        if row_num % 2 == 0:
            euros.append(price)
        else:
            dollars.append(price)

# Plot data
fig, ax = plt.subplots()
ax.plot(dates, dollars, label='Dollars')
ax.plot(dates, euros, label='Euros')
ax.set_xlabel('Date')
ax.set_ylabel('Price')
ax.set_title('Price over Time')
fig.autofmt_xdate() # Rotate and align x-axis labels
ax.legend()
plt.show()