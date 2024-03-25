import csv


def read_csv() -> list:
    clean_data = []
    with open('uszips.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0]=='zip':
                continue
            clean_data.append(row)
    return clean_data

