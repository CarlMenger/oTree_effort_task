import pandas as pd
import random
import sys


names = ["vt203_1", "vt203_2", "vt203_03", "vt203_04", "vt203_05", "vt203_06", "vt203_07", ]
scores_r1 = [random.randrange(0, 10) for _ in range(5)]
scores_r2 = [random.randrange(0, 100) for _ in range(5)]
scores_r3 = [random.randrange(0, 1000) for _ in range(5)]

df = pd.DataFrame(list(zip(names, *[scores_r1, scores_r2, scores_r3])),
                  columns=["Name", "round1", "round2", "round3"], ).to_csv(
    "D:\__OTree\__DP - effort task\TestDataDumps\pandas_test.txt", sep="\t", )

df2 = [list(a) for a in zip(names, scores_r1, scores_r2, scores_r3)]
#print(df2)

input_df = pd.read_csv("D:\__OTree\__DP - effort task\TestDataDumps\pandas_test.txt", sep="\t")
#print(input_df["Name"])

# [list(a) for a in zip(names,scores_r1,scores_r2,scores_r3)]

pc_name_list_205 = [[i, f"VT_205 - {i}"] for i in range(1, 19)]
pc_name_list_203 = [[i, f"VT_205 - {i}"] for i in range(1, 25)]
#print([f"VT_203 - {i}" for i in range(1, 25)] + [f"VT_205 - {i}" for i in range(1, 19)])


#print(pc_name_205)
pc_name = random.sample(pc_name_list_203 + pc_name_list_205, 1)[0][1]
print(pc_name)
print(type(pc_name))