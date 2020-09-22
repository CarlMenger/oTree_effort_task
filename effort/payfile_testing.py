import pandas as pd
import random
import os



names = ["vt203_1", "vt203_2", "vt203_03", "vt203_04", "vt203_05", ]
scores_r1 = [random.randrange(0, 10) for _ in range(5)]
scores_r2 = [random.randrange(0, 100) for _ in range(5)]
scores_r3 = [random.randrange(0, 1000) for _ in range(5)]

def create_df():
    names = ["vt203_1", "vt203_2", "vt203_3", "vt203_4", "vt203_5", ]
    scores_r1 = [random.randrange(0, 10) for _ in range(5)]
    scores_r2 = [random.randrange(0, 100) for _ in range(5)]
    scores_r3 = [random.randrange(0, 1000) for _ in range(5)]
    test_df = pd.DataFrame()
    test_df["names"] = names
    test_df["scores_round_1"] = scores_r1
    test_df["scores_round_2"] = scores_r2
    test_df["scores_round_3"] = scores_r3

    test_data = [list(a) for a in zip(names, scores_r1, scores_r2, scores_r3)]
    [test_df.append(row) for row in test_data]
    return test_df

df = pd.DataFrame(list(zip(names, *[scores_r1, scores_r2, scores_r3])),
                  columns=["Name", "round1", "round2", "round3"], ).to_csv(
    "D:\__OTree\__DP - effort task\TestDataDumps\pd_test.txt", sep="\t", )

df2 = [list(a) for a in zip(names, scores_r1, scores_r2, scores_r3)]

input_df = pd.read_csv("D:\\__OTree\\__DP - effort task\\TestDataDumps\\pd_test.txt")

# [list(a) for a in zip(names,scores_r1,scores_r2,scores_r3)]

pc_name_list_205 = [[i, f"VT_205 - {i}"] for i in range(1, 19)]
pc_name_list_203 = [[i, f"VT_205 - {i}"] for i in range(1, 25)]
#print([f"VT_203 - {i}" for i in range(1, 25)] + [f"VT_205 - {i}" for i in range(1, 19)])

#############################################################################################

dfs = []
for i in range(3):
    dfs.append(create_df())

#header_df = pd.DataFrame(columns=["names", "scores_round_1", "scores_round_2", "scores_round_3"])
header_df = pd.DataFrame()
dfs.append(header_df)
header_df = pd.concat(dfs)

x = 0
for df in dfs:
    x = +1
    df.to_csv(f"D:\\__OTree\\__DP - effort task\\TestDataDumps\\pd_test_{x}.txt", sep="\t")
header_df.to_csv("D:\\__OTree\\__DP - effort task\\TestDataDumps\\pd_test.txt", sep="\t")



def edit_files():
    print(os.getcwd())
    path = "D:\\__OTree\\__DP - effort task\\TestDataDumps\\score_records__T0__2020_09_22-18_03.json"
    opened_file = pd.read_json("D:\\__OTree\\__DP - effort task\\TestDataDumps\\score_records__T0__2020_09_22-18_03.json")
    #opened_file = opened_file.sort_values(by=["gender", "round_1"])
    print(opened_file.to_string())

edit_files()