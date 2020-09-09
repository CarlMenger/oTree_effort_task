import time
import os
import re
import csv
import pprint
import pandas

dumps_dir_location = "D:\__OTree\DP - effort task\Z_dumps"


def search_for_dumps(dir_location, table=False, payfile=False ):
    dir_list = os.listdir(f"{dir_location}")
    file_dumps, pay_files = [], []

    for file_name in dir_list:
        try:
            file_dumps.append(re.match("(^ztree_dump_)(\d+)", file_name))
            pay_files.append(re.match("^payfile", file_name))
        except(AttributeError):
            continue

    if not file_dumps:
        print("Warning: No dump_file has been found")
    else:
        print(sorted(file_dumps)[-1])
        return sorted(file_dumps)[-1]


def search_for_payfile(dir_location):
    dir_list = os.listdir(f"{dir_location}")
    file_dumps, pay_files = [], []

    for file_name in dir_list:
        try:
            file_dumps.append(re.match("^ztree_dump_\d+", file_name))
            pay_files.append(re.match("^payfile", file_name))

        except(AttributeError): #FIXME
            print("error")

    if not file_dumps:
        print("Warning: No dump_file has been found")
    else:
        return (f"{dumps_dir_location}" + "\\" + f"{file_dumps[-1]}")

def read_table(last_file_dump):

    with open("D:\__OTree\DP - effort task\Z_dumps\ztree_dump_3") as csv_file:
        table = pandas.read_csv(csv_file, delimiter=' ')
        print(table)
        for line in table:
            print(line)



# subjects_table = open(f"D:\__OTree\DP - effort task\Z_dumps\{}", "r")
# globals_table = open(f"D:\__OTree\DP - effort task\Z_dumps\{}", "r")
# payfile = open(f"D:\__OTree\DP - effort task\Z_dumps\{}", "r")


last_table = search_for_dumps(dumps_dir_location)
#read_table(last_table)



#TODO: payfile has time mark --> use it
#TODO: need to store only one string for single last dump file so redo function to just one var
#TODO: read_tale function
#TODO separate function for load and read payfile

"""
def search_for_dumps(dir_location, table=False,payfile=False ):
    dir_list = os.listdir(f"{dir_location}")
    file_dumps, pay_files = [], []

    for file_name in dir_list:
        try:
            file_dumps.append(re.match("(^ztree_dump_)(\d+)", file_name))
            pay_files.append(re.match("^payfile", file_name))
        except(AttributeError):
            continue

    if not file_dumps:
        print("Warning: No dump_file has been found")
    else:
        return file_dumps[-1]"""