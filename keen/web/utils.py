import csv


def row_reader(f):
    # we cannot use file as source since there migt be CSV files with weired
    # end-of-line marks
    for row in f:
        row = row.strip()
        print repr(row)
        yield row


def csv_reader(f):
    """Generate sequence of rows from CSV file striping whitespace from each value
    """
    reader = csv.reader(f)
    for row in reader:
        yield map(str.strip, row)

