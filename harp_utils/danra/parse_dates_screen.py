from rich.console import Console
from datetime import datetime
from calendar import monthrange
import os
import sys
from datetime import datetime, timedelta

dates_file = "dates_month.txt"
# Sample list of dates in %Y%m%d format
if not os.path.isfile(dates_file):
    print(f"{dates_file} not available")
    sys.exit(1)

with open(dates_file,"r") as f:
    dates = f.readlines()
date_strings=[str(d.rstrip()) for d in dates]
# get month and year
year=int(date_strings[0][0:4])
month=int(date_strings[0][5:7])
ndays = monthrange(year,month)[1]
complete = 100*len(date_strings)/ndays

# Convert date strings to datetime objects
if any(":" in i for i in date_strings):
    date_strings = [d[0:10] for d in date_strings]
    dates = [datetime.strptime(date, "%Y-%m-%d") for date in date_strings]
else:
    dates = [datetime.strptime(date, "%Y-%m-%d") for date in date_strings]
# Create a list of values for the y-axis (for example, you can use index)
values = range(len(dates))

# Initialize Rich Console
console = Console()

# Define a function to generate the bar representation
def generate_bar(value):
    return "|" + "#" * value + " "

# Redirect output to a file
#with open("date_column.txt", "w") as f:
# Print the date column and write it to the file
#for date, value in zip(dates, values):
#    console.print(f"{date.strftime('%Y-%m-%d')}: {generate_bar(value)}", style="bold green") #, file=f)
last_date=dates[-1]
value=len(dates)
console.print(f"Last date {last_date.strftime('%Y-%m-%d')}: {generate_bar(value)} {complete} % complete", style="bold green") #, file=f)

start_date = datetime(year, month, 1)
expected_dates = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(ndays)]
if len(dates) != ndays:
    #f.write(date.strftime('%Y-%m-%d') + '\n')
    diff = list(set(expected_dates)^set(date_strings))
    diff.sort()
    print(f"Missing: {diff}")

