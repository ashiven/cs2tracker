import csv
import matplotlib.pyplot as plt

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