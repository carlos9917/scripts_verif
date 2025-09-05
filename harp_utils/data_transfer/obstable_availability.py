import sqlite3
from datetime import datetime
from datetime import timedelta
import calendar
from rich.console import Console
from rich.table import Table
from rich import box
import os
import argparse
import sys

def get_table_schema(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row[1]: row[2] for row in cursor.fetchall()}

def analyze_availability(db_path, year, month):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the schema of the SYNOP table
    schema = get_table_schema(cursor, 'SYNOP')

    # Get the first and last day of the month
    _, last_day = calendar.monthrange(year, month)
    start_date = datetime(year, month, 1).timestamp()
    end_date = datetime(year, month, last_day, 23, 59, 59).timestamp()

    # Define variables to analyze (all REAL columns except lat, lon, elev)
    variables = [col for col, type in schema.items() 
                 if type == 'REAL' and col not in ['lat', 'lon', 'elev']]

    results = {}
    total_rows = cursor.execute(
        "SELECT COUNT(*) FROM SYNOP WHERE valid_dttm BETWEEN ? AND ?",
        (start_date, end_date)
    ).fetchone()[0]

    for var in variables:
        count = cursor.execute(
            f"SELECT COUNT(*) FROM SYNOP WHERE valid_dttm BETWEEN ? AND ? AND {var} IS NOT NULL",
            (start_date, end_date)
        ).fetchone()[0]
        availability = (count / total_rows) * 100 if total_rows > 0 else 0
        results[var] = availability

    conn.close()
    return results

def count_variable_availability(db_path, year, month, variable):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    _, last_day = calendar.monthrange(year, month)
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, last_day, 23, 59, 59)

    days_with_data = 0
    for day in range(1, last_day + 1):
        current_date = datetime(year, month, day)
        next_date = current_date + timedelta(days=1)
        
        count = cursor.execute(
            f"SELECT COUNT(DISTINCT date(valid_dttm, 'unixepoch')) FROM SYNOP WHERE valid_dttm BETWEEN ? AND ? AND {variable} IS NOT NULL",
            (current_date.timestamp(), next_date.timestamp())
        ).fetchone()[0]
        
        if count > 0:
            days_with_data += 1

    conn.close()
    return days_with_data, last_day

def display_variable_availability(variable, days_with_data, total_days, year, month):
    console = Console()
    table = Table(title=f"Availability of {variable} for {calendar.month_name[month]} {year}", box=box.ROUNDED)

    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", justify="right", style="magenta")

    availability_percentage = (days_with_data / total_days) * 100
    color = "green" if availability_percentage == 100 else "yellow" if availability_percentage > 80 else "red"

    table.add_row("Days with data", f"[{color}]{days_with_data}[/{color}]")
    table.add_row("Total days in month", str(total_days))
    table.add_row("Availability", f"[{color}]{availability_percentage:.2f}%[/{color}]")
    table.add_row("Month complete", "[green]Yes[/green]" if days_with_data == total_days else "[red]No[/red]")

    console.print(table)



def display_results(results, year, month):
    console = Console()
    table = Table(title=f"Data Availability for {calendar.month_name[month]} {year}", box=box.ROUNDED)

    table.add_column("Variable", style="cyan", no_wrap=True)
    table.add_column("Availability (%)", justify="right", style="magenta")

    for var, availability in results.items():
        color = "green" if availability > 90 else "yellow" if availability > 50 else "red"
        table.add_row(var, f"[{color}]{availability:.2f}%[/{color}]")

    console.print(table)

def validate_year(year):
    try:
        year = int(year)
        if 1900 <= year <= 2100:
            return year
        raise argparse.ArgumentTypeError(f"Year must be between 1900 and 2100")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid year format. Please use YYYY")

def validate_month(month):
    try:
        month = int(month)
        if 1 <= month <= 12:
            return month
        raise argparse.ArgumentTypeError(f"Month must be between 1 and 12")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid month format. Please use a number between 1 and 12")

def main(db_path):
    parser = argparse.ArgumentParser(description="Analyze data availability in SQLite database.")
    #parser.add_argument("db_path", help="Path to the SQLite database file")
    parser.add_argument("year", type=validate_year, help="Year to analyze (YYYY)")
    parser.add_argument("month", type=validate_month, help="Month to analyze (1-12)")
    parser.add_argument("--variable", "-v", help="Specific variable to analyze for daily availability")


    args = parser.parse_args()
    year = args.year
    db_path = os.path.join(DB_PATH,f"OBSTABLE_{year}.sqlite")

    #try:
    #    results = analyze_availability(db_path, args.year, args.month)
    #    display_results(results, args.year, args.month)
    #except sqlite3.Error as e:
    #    print(f"An error occurred when accessing the database: {e}", file=sys.stderr)
    #    sys.exit(1)
    #except Exception as e:
    #    print(f"An unexpected error occurred: {e}", file=sys.stderr)
    #    sys.exit(1)
    try:
        if args.variable:
            days_with_data, total_days = count_variable_availability(db_path, args.year, args.month, args.variable)
            display_variable_availability(args.variable, days_with_data, total_days, args.year, args.month)
        else:
            results = analyze_availability(db_path, args.year, args.month)
            display_results(results, args.year, args.month)
    except sqlite3.Error as e:
        print(f"An error occurred when accessing the database: {e}", file=sys.stderr)
        print(f"{db_path} missing!")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    DB_PATH="/ec/res4/scratch/nhd/verification/DMI_data/harp_v0201/OBSTABLE"
    main(DB_PATH)


#if __name__ == "__main__":
#    if len(sys.argv) == 1:
#       print("Plesse provide year and month (both integers)")
#    else:
#        year = sys.argv[1]
#    year = 1999  # Replace with the desired year
#    month = 9    # Replace with the desired month (1-12)
#    db_path = os.path.join(DB_PATH,f"OBSTABLE_{year}.sqlite")
#    print(f"Checking {db_path}")
#
#    results = analyze_availability(db_path, year, month)
#    display_results(results, year, month)
