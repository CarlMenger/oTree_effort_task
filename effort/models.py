from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)
import pandas as pd
import logging
import time
import os
import random
import csv

logging.basicConfig(level=logging.DEBUG,
                    filename="D:\\__OTree\\__DP - effort task\\TestDataDumps\\debug_log.txt",
                    format="%(asctime)s: %(message)s",
                    )

author = "Carl_Menger"

doc = """
Separate players based on real effort task and gender into groups competing against each other
"""


class Constants(BaseConstants):
    name_in_url = "StopLookingAtUrl"
    players_per_group = 2
    num_rounds = 3
    all_score_positions = {
        "slightly_ahead_to": "You are slightly ahead in score compared to your opponent",
        "slightly_behind_to": "You are slightly behind in score compared to your opponent",
        "far_ahead": "You are far ahead in score compared to your opponent",
        "far_behind": "You are far behind in score compared to your opponent",
        "equal_position": "You have the same score as your opponent",
        "T0": ""  # Placeholder for T0 so it doesnt raise error
    }
    pc_name_list_205 = [[i, f"VT_205 - {i}"] for i in range(1, 19)]
    pc_name_list_203 = [[i, f"VT_203 - {i}"] for i in range(1, 25)]
    date_time = time.asctime(time.localtime(time.time()))
    results_page_timeout_seconds = 30
    task_stage_timeout_seconds = 35  # 30 sec game time + 5 sec prep time
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(BASE_DIR, "effort", "data")


class Subsession(BaseSubsession):

    dir_path = models.StringField(initial=Constants.path)

    # Grouping set up
    def creating_session(self):
        if self.round_number == 1:
            self.group_randomly()
        else:
            self.group_like_round(1)

    def determine_winner(self, player1_points, player2_points):
        if player1_points > player2_points:
            return [1.0, 0.0]
        elif player1_points < player2_points:
            return [0.0, 1.0]
        else:
            return [0.5, 0.5]

    def group_players_after_trial_task(self):
        # all Ts are technically grouped together, for T1, T2 it just doesnt do anything

        self.group_like_round(1)

        # Load and format json DF into reduced version
        if self.session.config["treatment"] > 0:
            wanted_data_columns = ["treatment", "gender", "round_score_1", "round_score_2", "winning_1", "winning_2", ]
            # FIXME: wanted_data_columns in more general location ?
            file_dir = Constants.path
            df_csr = pd.read_json(f"{file_dir}\\Central_Score_Records.json")
            sub_table = df_csr[wanted_data_columns]
            # drop NAN rows
            sub_table = sub_table.dropna()
            for player in self.get_players():
                player.get_pairs_after_trial_task_for_t1_t2(sub_table)  # FIXME

        if self.session.config["treatment"] == 0:
            # Add winners to player.winner for first round
            for group in self.get_groups():
                p1 = group.get_players()[0]
                p2 = group.get_players()[1]
                first_player_score_r2 = p1.get_player_point_score_in_rounds(1, 1)[0]
                second_player_score_r2 = p2.get_player_point_score_in_rounds(1, 1)[0]
                results = self.determine_winner(first_player_score_r2, second_player_score_r2)
                p1.winning = results[0]
                p2.winning = results[1]

    def create_record_files(self):
        """ 1) create_score_records: make actual .csv and .js data set in app data folder
            2)
            """

        def create_score_records():
            timestr = time.strftime("%Y_%m_%d-%H_%M")
            file_dir = Constants.path
            treatment = self.session.config["treatment"]

            # data lists # TODO more relaible version, where order of lines of code is not deteriminal to
            # TODO  --> use pd.insert(pos,[data])
            player_info = {}
            df = pd.DataFrame()
            for player in self.get_players():
                index_ = 0
                player_info["date"] = timestr
                player_info["treatment"] = treatment
                player_info["gender"] = player.in_round(1).gender
                for round_pointscore in player.get_player_point_score_in_rounds(0, 2):
                    player_info[f"round_score_{index_}"] = round_pointscore
                    index_ += 1
                index_ = 0
                for p_in_round in player.in_rounds(1, 3):
                    player_info[f"round_keystrokes_{index_}"] = p_in_round.overall_keystroke_count
                    index_ += 1
                player_info["winning_1"] = player.in_round(2).winning
                player_info["winning_2"] = player.in_round(3).winning
                try:
                    player_info["room_name"] = player.in_round(1).participant.label[0:5]
                    player_info["pc_name"] = player.in_round(1).participant.label[6:]
                    player_info["other_room_name"] = player.get_others_in_group()[0].participant.label[0:5]
                    player_info["other_pc_name"] = player.get_others_in_group()[0].participant.label[6:]
                except TypeError:
                    pass
                player_info["slightly_behind_to"] = player.in_round(2).sb_options
                player_info["slightly_ahead_to"] = player.in_round(2).sa_options
                player_info["index_of_paired_past_player"] = player.in_round(2).index_of_paired_past_player
                player_info["score_position"] = player.in_round(2).score_position
                df = df.append(player_info, ignore_index=True)
                player_info = {}

            # csv generation
            # if add_to_central_DB == 1, also update CSR (all sessions combined df)
            if self.session.config["add_to_central_DB"] == 1:
                if not os.path.isfile(f"{file_dir}\\Central_Score_Records.json"):
                    df.to_json(f"{file_dir}\\Central_Score_Records.json")
                    df.to_excel(f"{file_dir}\\Central_Score_Records.xlsx", engine="xlsxwriter")
                else:
                    csr = pd.read_json(f"{file_dir}\\Central_Score_Records.json")
                    # TODO?: concat(keys=treatments),
                    df.reset_index(inplace=True, drop=True)
                    csr.reset_index(inplace=True, drop=True)  # TODO: now to check if it does not fuck up previous csr
                    pd.concat([csr, df], ignore_index=True).to_json(f"{file_dir}\\Central_Score_Records.json")
                    pd.concat([csr, df], ignore_index=True).to_excel(f"{file_dir}\\Central_Score_Records.xlsx",
                                                                     engine="xlsxwriter")

            # Always create session records
            df.to_excel(f"{file_dir}\\score_records__T{treatment}__{timestr}.xlsx", engine='xlsxwriter')

        # User friendly excel and for payment administration in offline mode
        def create_payfile():  # TODO: Outside offline mode this is redundant and might require reworking
            timestr = time.strftime("%Y_%m_%d-%H_%M")
            file_dir = Constants.path
            payments = [player.get_player_endowment() for player in self.get_players()]
            winning = [player.winning for player in self.get_players()]
            pc_names = [player.participant.label for player in self.get_players()]
            try:
                payfile_data = dict(pc_name=pc_names,
                                    payment=payments,
                                    has_won=winning, )
            except TypeError:
                pc_names = [pc for pc in range(len(pc_names))]
                payfile_data = dict(pc_name=pc_names,
                                    payment=payments,
                                    has_won=winning, )
            # zTree style pay file generation
            #pd.DataFrame(payfile_data).to_csv(f"{file_dir}\\payfile_{timestr}.txt", sep="\t")
            pd.DataFrame(payfile_data).to_excel(f"{file_dir}\\payfile_{timestr}.xlsx", engine='xlsxwriter')

        # Last round call for winning_1, winning_2, total_points
        if self.session.config["treatment"] == 0:
            [group.calculate_points_wins_payments_t0() for group in self.get_groups()]
        else:
            [player.calculate_winner_t1_t2_for_rounds(1, 2) for player in self.get_players()]

        # In last round call to create dataframes and payfile
        create_score_records()
        if self.session.config["generate_payfile"]:
            create_payfile()


class Group(BaseGroup):

    def calculate_points_wins_payments_t0(self):
        # Load up players in this group
        p1, p2 = self.get_players()

        # Load point scores of players
        p1_points = p1.get_player_point_score_in_rounds(1, 2)
        p2_points = p2.get_player_point_score_in_rounds(1, 2)

        # Write down total points to player attribute
        p1.player_total_points = sum(p1_points)
        p2.player_total_points = sum(p2_points)

        # Find out who won/lost
        if self.session.config["treatment"] == 0:
            # feeds both last round points
            results = self.subsession.determine_winner(sum(p1_points), sum(p2_points))
        else:
            # feeds only last round points
            results = self.subsession.determine_winner(p1_points[1], p2_points[1])

        # Write down wins/loses/stalemates
        p1.winning = results[0]
        p2.winning = results[1]

        # Write down payments to player attribute # FIXME: rounding up to 5 kč ?
        p1.player_payment = int(p1.get_player_endowment())
        p2.player_payment = int(p2.get_player_endowment())


class Player(BasePlayer):

    label = models.StringField()  # REWRITE ME
    pc_name = models.IntegerField()  # REWRITE ME
    # Questionnaires vars
    winning = models.PositiveIntegerField(initial=0.0)
    gender = models.IntegerField(widget=widgets.RadioSelect,
                                 choices=[
                                     [0, "male"],
                                     [1, "female"],
                                 ]
                                 )

    room_name = models.IntegerField(choices=[
        [203, " VT 203 "],
        [205, " VT 205 "]
    ]
    )
    # Task stage vars
    point_score = models.PositiveIntegerField(initial=0)
    player_total_points = models.IntegerField(initial=0)
    player_payment = models.IntegerField(initial=0)
    overall_keystroke_count = models.IntegerField()
    # T1 T2 vars
    index_of_paired_past_player = models.IntegerField()
    paired_past_player_round_1_points = models.IntegerField()
    paired_past_player_round_2_points = models.IntegerField()
    sb_options = models.StringField()
    sa_options = models.StringField()
    score_position = models.StringField(initial="T0")
    # DEBUG ONLY
    """    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(BASE_DIR, "effort", "data")
    Ts_score_difference = models.IntegerField()
    dir_path = models.StringField(initial=path)"""

    def pc_name_choices(self):
        if self.room_name == 205:
            return Constants.pc_name_list_205
        elif self.room_name == 203:
            return Constants.pc_name_list_203
        else:
            return ["error"]

    def player_point_score(self):
        return self.point_score

    def participant_label(self):
        return self.participant.label

    # list of points in paying rounds x to y, + 1 to keep pythonic indexing for rounds
    def get_player_point_score_in_rounds(self, first_round, last_round):
        return [in_paying_rounds.point_score for in_paying_rounds in
                self.in_rounds(first_round + 1, last_round + 1)]

    def get_player_endowment(self):
        return self.player_total_points * self.session.config["conversion_rate"] + self.session.config[
            "participation_fee"] + int(self.session.config["winning_bonus"] * self.winning)

    def get_pairs_after_trial_task_for_t1_t2(self, sub_table, treatment=1):
        """ Set index_of_paired_past_player, score_position and if possible sb_options + sa_options vars
            Called after trial task """

        def pair_with_random_past_player(sub_table, position_options, disallowed_indexes):
            index_all = sub_table.index.tolist()
            all_disallowed_indexes = disallowed_indexes + list(position_options.values())
            flat_list = [item for sublist in all_disallowed_indexes for item in sublist]
            index_clean = [index for index in index_all if index not in flat_list]  # FIXME: assert for empty list?
            opponent_index = random.sample(index_clean, 1)[0]
            self.index_of_paired_past_player = opponent_index
            #print(f"{self.participant_label()} says: I was randomly matched")

        def find_score_position(sub_table):
            disallowed_indexes = []
            position_options = {"slightly_behind_to": [],
                                "slightly_ahead_to": [],
                                }
            sub_table = sub_table[sub_table["treatment"] == (self.session.config["treatment"] - 1)]
            sub_table = sub_table[sub_table["gender"] == self.in_round(1).gender]

            # SB filtering #
            filtered_table = sub_table[sub_table["round_score_1"] > my_score]
            filtered_table = filtered_table[filtered_table["round_score_1"] <= my_score + spread]
            disallowed_indexes.append(filtered_table.index.tolist())  # store options that cant be randomly chosen
            if self.session.config["treatment"] == 2:
                filtered_table = filtered_table[filtered_table["winning_1"] == 1]
            #print(f"This is sub_table SB -treatment -gender -point_interval -winning: {filtered_table}")
            if len(filtered_table.index.tolist()):  # at least one match in SB
                position_options["slightly_behind_to"] = filtered_table.index.tolist()
                self.sb_options = str(filtered_table.index.tolist())[1:-1]
                #print(f"{self.participant_label()} says: I found SB position")

            # SA filtering #
            filtered_table = sub_table[sub_table["round_score_1"] < my_score]
            filtered_table = filtered_table[filtered_table["round_score_1"] >= my_score - spread]
            disallowed_indexes.append(filtered_table.index.tolist())  # store options that cant be randomly chosen
            if self.session.config["treatment"] == 2:
                filtered_table = filtered_table[filtered_table["winning_1"] == 0]
            #print(f"This is sub_table SA -treatment -gender -point_interval -winning: {filtered_table}")

            if len(filtered_table.index.tolist()):  # at least one match in SA
                position_options["slightly_ahead_to"] = filtered_table.index.tolist()
                self.sa_options = str(filtered_table.index.tolist())[1:-1]
                #print(f"{self.participant_label()} says: I found SA position")

            if len(position_options["slightly_behind_to"]) > 0 and len(position_options["slightly_ahead_to"]) > 0:
                # Save results to player attributes
                self.score_position = str(random.sample(position_options.keys(), 1)[0])
                self.index_of_paired_past_player = int(random.sample(position_options[self.score_position], 1)[0])
                #print(f"{self.participant_label()} says: I found SB and SA position {self.index_of_paired_past_player}")

            else:
                pair_with_random_past_player(sub_table, position_options, disallowed_indexes)

        # Main body of function
        spread = int(self.session.config["pairing_filter_margin"])
        my_score = (self.get_player_point_score_in_rounds(1, 1))[0]
        find_score_position(sub_table)
        pp_r1 = sub_table.loc[self.index_of_paired_past_player]["round_score_1"]
        pp_r2 = sub_table.loc[self.index_of_paired_past_player]["round_score_2"]

        # Add points of paired player to self.attributes and winning_1 to records
        self.paired_past_player_round_1_points = pp_r1
        self.paired_past_player_round_2_points = pp_r2
        self.calculate_winner_t1_t2_for_rounds(1, 1)

        if not self.score_position or self.score_position == "T0":
            # FIXME: after testing delete error parts and simplify
            if pp_r1 > my_score:
                if pp_r1 <= (my_score + spread):
                    self.score_position = "error1"
                else:
                    self.score_position = "far_behind"
            elif pp_r1 < my_score:
                if pp_r1 >= (my_score - spread):
                    self.score_position = "error2"
                else:
                    self.score_position = "far_ahead"
            else:
                self.score_position = "equal_position"

    def calculate_winner_t1_t2_for_rounds(self, round_1, round_2):
        """Calculate winner in non-trial rounds for T1 and T2 only"""
        my_points = sum(self.get_player_point_score_in_rounds(round_1, round_2))
        self.player_total_points = my_points
        assert (0 < round_1 < 3), "Function calculate_winner_t1_t2_for_rounds received false argument #1 "
        assert (0 < round_2 < 3 and round_1 <= round_2), \
            "Function calculate_winner_t1_t2_for_rounds received false argument #2 or #1 > #2"
        past_player_points = self.in_round(2).paired_past_player_round_1_points + \
                             self.in_round(2).paired_past_player_round_2_points * (round_2 - round_1)
        self.winning = self.subsession.determine_winner(my_points, past_player_points)[0]

