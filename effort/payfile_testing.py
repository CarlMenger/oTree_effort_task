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

wanted_data_columns = ["treatment", "gender", "round_1", "round_2", "winning_1", "winning_2", ]
path = "D:\\__OTree\\__DP - effort task\\TestDataDumps\\Central_Score_Records.json"
opened_file = pd.read_json(path)


def get_zipped_data():
    data_dict = {}
    for column in wanted_data_columns:
        data_dict[column] = opened_file[column].tolist()
    # out {'treatment': [0, 0, ...., 0, 0, 0, 1, 1, 1, 1, 1, 1], 'gender': [0, 1.. 1, 1], ...
    zipped_data = list(zip(*data_dict.values()))
    # out [(0, 0, 91, 109, 0, 0), (0, 1, 100, 78, 0, 0), (0, 1, 91, 115, 0, 0), (0, 0, 117, 120, 0, 0), ...
    return zipped_data


class PastPlayer:
    def __init__(self, id):
        self.id = id
        self.treatment = 0
        self.gender = 0
        self.round_1 = 0
        self.round_2 = 0
        self.winning_1 = 0
        self.winning_2 = 0

    def __str__(self):
        print(
            f"id: {self.id}\n"
            f"treatment: {self.treatment}\n"
            f"gender: {self.gender}\n"
            f"round_1: {self.round_1}\n"
            f"round_2: {self.round_2}\n"
            f"winning_1: {self.winning_1}\n"
            f"winning_2: {self.winning_2}\n")


def create_past_players(zipped_data):
    n_players = len(opened_file)
    all_past_players = []
    for id in range(n_players):
        attributes = zipped_data[id]
        past_player = PastPlayer(id + 1)
        past_player.treatment = attributes[0]
        past_player.gender = attributes[1]
        past_player.round_1 = attributes[2]
        past_player.round_2 = attributes[3]
        past_player.winning_1 = attributes[4]
        past_player.winning_2 = attributes[5]
        all_past_players.append(past_player)
        attributes = ()
    return all_past_players


# zipped_data = get_zipped_data()
# print(len(zipped_data))
# all_past_players = create_past_players(zipped_data)
# print(all_past_players[0].__str__())


def data_handling():
    data_dict = {}
    for column in wanted_data_columns:
        data_dict[column] = opened_file[column].tolist()
    # out {'treatment': [0, 0, ...., 0, 0, 0, 1, 1, 1, 1, 1, 1], 'gender': [0, 1.. 1, 1], ...
    zipped_data = list(zip(*data_dict.values()))
    # out [(0, 0, 91, 109, 0, 0), (0, 1, 100, 78, 0, 0), (0, 1, 91, 115, 0, 0), (0, 0, 117, 120, 0, 0), ...
    data_dict = {}
    for player in enumerate(zipped_data):
        data_dict[f"past_player_{player[0]}"] = player[1]

    return data_dict


past_players = data_handling()


def create_subtable():
    results_dict = {}
    my_score = 90
    sub_table = opened_file[wanted_data_columns]
    # print(sub_table.to_string())
    sub_table = sub_table[sub_table["treatment"] == 1 - 1]
    sub_table = sub_table[sub_table["gender"] == 0]
    # SB & SA filtering
    filtered_table = sub_table[sub_table["round_1"] > my_score]
    filtered_table = filtered_table[filtered_table["round_1"] <= my_score + 3]
    # at least one match
    if len(filtered_table.index):
        results_dict["slightly_behind_to"] = filtered_table.index.tolist()
        print(results_dict["slightly_behind_to"])
        filtered_table = sub_table[sub_table["round_1"] < my_score]
        filtered_table = filtered_table[filtered_table["round_1"] >= my_score + 3]
        if len(filtered_table.index):
            results_dict["slightly_ahead_to"] = filtered_table.index.tolist()
            #self.score_position = random.sample(results_dict.keys(), 1)[0]
            #self.index_of_paired_past_player = random.sample(results_dict[self.score_position], 1)[0]

    else:
        print("call random pairing function")

    # print(filtered_table)
    print(f"filtered_table lenght: {((len(filtered_table.index)))}")
    print(filtered_table)

    print(f"sample index lenght: {(int(len(sub_table.index)))}")




sub_table = opened_file[wanted_data_columns]
print(sub_table.to_string())

