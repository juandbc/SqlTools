#!/usr/bin/python3
# Python module for parsing CSV file to SQL operation like INSERT or UPDATE
# Version 1.0
import sys
import argparse

array_columns = []  # Array to store the columns name

# parent parser
parent_parser = argparse.ArgumentParser(add_help=False)
parent_parser.add_argument("table-name", type=str, default="TABLE_NAME", help="table name")
parent_parser.add_argument("data-separator", type=str, default=",",
                           help="character using as data separator in the CSV file")
parent_parser.add_argument("quoting-character", type=str, default="'",
                           help="character using to quoting in the CSV file")
parent_parser.add_argument("files-path", type=str, nargs=2, metavar=["source-file", "destination-file"],
                           help="files path. First, path of the CSV file then, path of the SQL file to be generated.")

parser = argparse.ArgumentParser(description="Generate a SQL INSERT/UPDATE script file from a CSV file .",
                                 parents=[parent_parser])
parser.add_argument("-o", dest="option", choices=["insert", "update"], type=str, required=True,
                    help="the type of statement that will be generated")
parser.add_argument("-id", type=str, help="identifier column name for the update statement")
parser.add_argument("--version", action="version", version="%(prog)s 1.0")
args = vars(parser.parse_args())


def parse_csv_file(file_path):
    """
    Read and parse the file
    :param str file_path: file's path
    :return List[list[str]]: array of records
    """
    print("Parsing CSV file")
    f = open(file_path, "r")

    global array_columns
    list_values = []  # Create a list to store values

    sw = True
    for line in f:  # Loop over lines in CSV file
        if sw:
            # Read the first line of values and remove quoting character for the array_columns
            array_columns = line.replace(quoting_character, "").rstrip("\n").split(data_separator)
            sw = False
        else:
            values = line.rstrip("\n").split(data_separator)
            list_values.append(values)
    # end for
    f.close()

    return list_values


def set_data_format(array_values):
    """
    Check and set the corresponding format for each value
    :param list[list[str]] array_values: list of values
    :return: list[list[str]]: array formatted
    """
    formatted_data = []

    for d in array_values:
        values = []
        for v in d:
            # Try to transform a text to int, if an exception occurs, treat it as an alphanumeric text
            try:
                v = int(v)
                v = str(v)
            except ValueError:
                if not v:
                    v = "''"
                elif type(v) is str:
                    if v.startswith("\""):  # If starts with " replace it with '
                        v = "'" + v[1:-1] + "'"
                    elif not v.startswith("'"):
                        v = "'" + v + "'"

            values.append(v)
        formatted_data.append(values)
    # end for
    return formatted_data


def generate_sql_insert_file(array_data):
    """
    Generate a SQL INSERT script file from array
    :param list[list[str]] array_data:
    """
    print("Generating SQL file")

    f = open(output_file_name, "w")  # open the file
    lines = []

    insert_string = "INSERT INTO " + table_name + " (" + ",".join(array_columns) + ") VALUES ("

    values = set_data_format(array_data)  # Apply format to the values

    for r in values:
        lines.append(insert_string + ",".join(r) + ")\n")  # Join the values to INSERT statement and append to the list

    f.writelines(lines)
    f.close()
    print(str(len(lines)) + " was written in " + output_file_name)


def generate_sql_update_file(id_row, array_data):
    """
    Generate a SQL UPDATE script file from array
    :param str id_row: identifier row's name
    :param list[list[str]] array_data: array of record
    """
    print("Generating SQL file")

    f = open(output_file_name, "w")  # open the file
    values = set_data_format(array_data)  # Apply format to the values
    update_string = "UPDATE " + table_name + " SET "
    lines = []
    id_row_index = array_columns.index(id_row)
    for r in values:
        line = update_string
        temp_values = []  # temporal array to store the columns and their values
        for v in r:
            if r.index(v) == id_row_index:  # exclude the id row from the columns to update
                pass
            else:
                temp_values.append(array_columns[r.index(v)] + " = " + v)
        # end for
        line += ",".join(temp_values) + "WHERE " + id_row + " = " + r[id_row_index] + ")\n"
        lines.append(line)
    # end for
    f.writelines(lines)
    f.close()
    print(str(len(lines)) + " was written in " + output_file_name)


option = args["option"]
table_name = args["table-name"]
data_separator = args["data-separator"]
quoting_character = args["quoting-character"]
input_file_name = args["files-path"][0]
output_file_name = args["files-path"][1]
id_row_name = args["id"]

print("Table name: " + table_name)
print("Data separator: " + data_separator)
print("Quoting character: " + quoting_character)
print("ifn: " + input_file_name)
print("ofn: " + output_file_name)
if id_row_name is not None:
    print("id row: " + id_row_name)

if option == "insert":
    print("You pass SQL INSERT option")

    data = parse_csv_file(input_file_name)
    generate_sql_insert_file(data)
elif option == "update":
    print("You pass SQL UPDATE option")

    data = parse_csv_file(input_file_name)
    generate_sql_update_file(id_row_name, data)

print("Done.")
