import itertools
import csv


def remove_duplicates(filename):
    file = open(filename)
    table = csv.reader(file)

    rows = []

    for row in table:
        rows.append(row)

    # Remove Duplicates
    rows.sort()
    rows = list(rows for rows, _ in itertools.groupby(rows))

    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def get_list_csv(filename):
    file = open(filename, 'r')
    table = csv.reader(file)

    rows = []

    for row in table:
        rows.append(row)
    return rows
