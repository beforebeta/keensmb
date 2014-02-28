import csv


def csv_reader(f):
    """Generate sequence of rows from CSV file striping whitespace from each value
    """
    reader = csv.reader(f)
    for row in reader:
        yield map(str.strip, row)

