import pandas as pd
import random


names = ["vt203_01","vt203_02","vt203_03","vt203_04","vt203_05","vt203_06","vt203_07",]
scores_r1 = [random.randrange(0, 10) for _ in range(5)]
scores_r2 = [random.randrange(0, 100) for _ in range(5)]
scores_r3 = [random.randrange(0, 1000) for _ in range(5)]

df = pd.DataFrame(list(zip(names, scores_r1, scores_r2, scores_r3)),
                  columns=["Name", "round1", "round2", "round3"], ).to_csv(
    "D:\__OTree\__DP - effort task\TestDataDumps\pandas_test.txt",  sep="\t",)

df2 = [list(a) for a in zip(names,scores_r1,scores_r2,scores_r3)]
print(df2)

input_df = pd.read_csv("D:\__OTree\__DP - effort task\TestDataDumps\pandas_test.txt", sep="\t")
print(input_df["Name"])

#[list(a) for a in zip(names,scores_r1,scores_r2,scores_r3)]