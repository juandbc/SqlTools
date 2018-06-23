#!/usr/bin/python3.6
# Python module for parsing JSON file to SQL operation like INSERT or UPDATE
# Version 1.0
import json
import argparse

array_columns = []  # Array to store the columns name

# parent parser
parent_parser = argparse.ArgumentParser(add_help=False)
parent_parser.add_argument("-t", dest="table-name", type=str,
                           help="table name in the database, if you omitted this argument, you must wrap the array "
                                "with the table name in the json format")
parent_parser.add_argument("source-file", type=str, help="path of the JSON file")
parent_parser.add_argument("destination-file", type=str, help="path of the SQL file to be generated")

parser = argparse.ArgumentParser(description="""This script generate a SQL INSERT/UPDATE script file from a JSON file 
                                                and should be executed using Python 3 or later. 
                                                JSON file encoding must be UTF-8 and text cell must be quoted. 
                                                The JSON should be in the following format: {table_name: [
                                                {column_name: value,column_name: value},
                                                {column_name: value,column_name: value}, ... ]}""",
                                 parents=[parent_parser])
parser.add_argument("-o", dest="option", choices=["insert", "update"], type=str, required=True,
                    help="the type of statement that will be generated")
parser.add_argument("-id", type=str, help="identifier column name for the update statement")
parser.add_argument("--version", action="version", version="%(prog)s 1.0")
args = vars(parser.parse_args())


def parse_json_file(file_path):
    """
    Read and parse the file
    :param str file_path: file's path
    :return List[list[str]]: array of records
    """
    print("Parsing JSON file")
    f = open(file_path, mode="r", encoding="UTF-8")

    global table_name
    global array_columns
    list_values = []  # Create a list to store values
    json_object = json.load(f)

    if table_name is None:
        table_name = list(json_object.keys())[0]

    array_columns = list(json_object[table_name][0].keys())  # Get the columns names

    for j in json_object[table_name]:
        list_values.append(list(j.values()))

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
        lines.append(insert_string + ",".join(r) + ");\n")  # Join the values to INSERT statement and append to the list

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
        line += ",".join(temp_values) + "WHERE " + id_row + " = " + r[id_row_index] + ";\n"
        lines.append(line)
    # end for
    f.writelines(lines)
    f.close()
    print(str(len(lines)) + " was written in " + output_file_name)


option = args["option"]
table_name = args["table-name"]
input_file_name = args["source-file"]
output_file_name = args["destination-file"]
id_row_name = args["id"]

if id_row_name is None and option == "update":
    print("You need to pass a id row name argument")
    exit()

if table_name is not None:
    print("Table name: " + table_name)

print("input filename: " + input_file_name)
print("output filename: " + output_file_name)

if id_row_name is not None:
    print("id row: " + id_row_name)

if option == "insert":
    print("You pass SQL INSERT option")

    data = parse_json_file(input_file_name)
    generate_sql_insert_file(data)
elif option == "update":
    print("You pass SQL UPDATE option")

    data = parse_json_file(input_file_name)
    generate_sql_update_file(id_row_name, data)

print("Done.")
