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

logging.basicConfig(level=logging.DEBUG,
                    filename="D:\\__OTree\\__DP - effort task\\TestDataDumps\\debug_log.txt",
                    format="%(asctime)s: %(message)s",
                    )


author = "Carl_Menger"

doc = """
Separate players based on real effort task into group competing against each other
"""


class Constants(BaseConstants):
    name_in_url = "StopLookingAtUrl"
    players_per_group = 2
    num_rounds = 3
    score_info = {
        "slightly_ahead": "You are slightly ahead in score compared to the other player in your group",
        "slightly_behind": "You are slightly behind in score compared to the other player in your group",
        "far_ahead": "You are slightly ahead in score compared to the other player in your group",
        "far_behind": "You are slightly behind in score compared to the other player in your group",
    }
    pc_name_list_205 = [[i, f"VT_205 - {i}"] for i in range(1, 19)]
    pc_name_list_203 = [[i, f"VT_203 - {i}"] for i in range(1, 25)]
    date_time = time.asctime(time.localtime(time.time()))
    results_page_timeout_seconds = 30
    task_stage_timeout_seconds = 35  # 30 sec game time + 5 sec prep time


class Subsession(BaseSubsession):

    # unused methods
    #def point_score_everyone(self):
    #    return [p.point_score for p in self.get_players()]

    #def show_player_matrix(self):
    #    return self.get_group_matrix()

    # Grouping set up
    def creating_session(self):
        if self.round_number == 1:
            self.group_randomly()
        else:
            self.group_like_round(1)

    def group_players_after_trial_task(self):
        # all Ts are technically grouped together, for T1, T2 it just doesnt do anything meaningful

        self.group_like_round(1)  # FIXME: is needed? shouldnt it stay the same?

        # Load and format json DF into reduced version
        if self.session.config["treatment"] > 0:
            wanted_data_columns = ["treatment", "gender", "round_1", "round_2", "winning_1", "winning_2", ]
            # FIXME: wanted_data_columns in more general location ?
            file_dir = self.session.config["file_dir"]
            df_csr = pd.read_json(f"{file_dir}\\Central_Score_Records.json")
            sub_table = df_csr[wanted_data_columns]
            # drop NAN rows
            sub_table = sub_table.dropna()
            for player in self.get_players():
                player.get_pairs_with_past_player(sub_table)# FIXME

        if self.session.config["treatment"] == 0:
            # Add winners to player.winner
            for player in self.get_players():
                player_score = player.get_player_point_score_in_rounds(2, 2)
                grouped_player_score = player.get_others_in_group()[0].player_point_score_in_rounds(2, 2)
                player.winning = self.determine_winner(player_score, grouped_player_score)


    # Create payfile.txt and Score_records.json
    def create_record_files(self):

        def create_score_records():
            timestr = time.strftime("%Y_%m_%d-%H_%M")
            file_dir = self.session.config["file_dir"]
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
                for round_pointscore in player.get_player_point_score_in_rounds(1, 3):
                    player_info[f"round_score{index_}"] = round_pointscore
                    index_ += 1
                index_ = 0
                for p_in_round in player.in_rounds(1, 3):
                    player_info[f"round_keystrokes{index_}"] = p_in_round.overall_keystroke_count
                    index_ += 1
                player_info["winning_1"] = player.in_round(2).winning
                player_info["winning_2"] = player.in_round(3).winning
                try:
                    player_info["room_name"] = player.in_round(1).participant.label[0:5]
                    player_info["pc_name"] = player.in_round(1).participant.label[6:]
                    player_info["other_room_name"] = player.get_others_in_group()[0].participant.label[0:5]
                    player_info["other_pc_name"] = player.get_others_in_group()[0].participant.label[6:]
                except(TypeError):
                    pass
                player_info["slightly_behind_to"] = player.sb_options
                player_info["slightly_ahead_to"] = player.sa_options
                df = df.append(player_info, ignore_index=True)
                player_info = {}
            #columns = ["date", "treatment", "gender", "room_name", "pc_name", "round_score_0", "round_score_1", "round_score_2",
             #          "winning_1", "winning_1",]

            # csv generation
            # if add_to_central_DB == 1, also update CSR (all sessions combined df)
            if self.session.config["add_to_central_DB"]:
                if not os.path.isfile(f"{file_dir}\\Central_Score_Records.json"):
                    df.to_json(f"{file_dir}\\Central_Score_Records.json")
                    df.to_excel(f"{file_dir}\\Central_Score_Records.xlsx", engine="xlsxwriter")
                csr = pd.read_json(f"{file_dir}\\Central_Score_Records.json")
                # TODO?: concat(keys=treatments),
                df.reset_index(inplace=True, drop=True)
                csr.reset_index(inplace=True, drop=True) #  TODO: now to check if it does not fuck up previous csr
                pd.concat([csr, df], ignore_index=True).to_json(f"{file_dir}\\Central_Score_Records.json")
                pd.concat([csr, df], ignore_index=True).to_excel(f"{file_dir}\\Central_Score_Records.xlsx", engine="xlsxwriter")

            # Always create session records
            df.to_excel(f"{file_dir}\\score_records__T{treatment}__{timestr}.xlsx", engine='xlsxwriter')

        # User friendly excel and txt for payment administration
        def create_payfile():
            timestr = time.strftime("%Y_%m_%d-%H_%M")
            file_dir = self.session.config["file_dir"]
            # FIXME: is payments ok ?
            payments = [player.get_player_endowment() for player in self.get_players()]
            winning = [player.winning for player in self.get_players()]
            pc_names = [player.participant.label for player in self.get_players()]
            try:
                payfile_data = dict(pc_name=pc_names,
                                    payment=payments,
                                    has_won=winning,)
            except(TypeError):
                pc_names = [pc for pc in range(len(pc_names))]
                payfile_data = dict(pc_name=pc_names,
                                    payment=payments,
                                    has_won=winning,)
            # txt generation
            pd.DataFrame(payfile_data).to_csv(f"{file_dir}\\payfile_{timestr}.txt", sep="\t")
            pd.DataFrame(payfile_data).to_excel(f"{file_dir}\\payfile_{timestr}.xlsx", engine='xlsxwriter')

        # Last round call
        if self.session.config["treatment"] == 0:
            [group.calculate_points_wins_payments_t0() for group in self.get_groups()]
        else:
            [player.calculate_winner_t1_t2() for player in self.get_players()]

        create_score_records()
        create_payfile()

    def determine_winner(self, player1_points, player2_points):
        if player1_points > player2_points:
            return [1.0, 0.0]
        elif player1_points < player2_points:
            return [0.0, 1.0]
        else:
            return [0.5, 0.5]


class Group(BaseGroup):
    def calculate_points_wins_payments_t0(self):
        # Load up players in this group
        p1, p2 = self.get_players()

        # Load point scores of players
        p1_points = p1.get_player_point_score_in_rounds(2, 3)
        p2_points = p2.get_player_point_score_in_rounds(2, 3)

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
    score_position = models.StringField()
    # DEBUG ONLY
    Ts_score_difference = models.IntegerField()

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

    # list of points in paying rounds x to y
    def get_player_point_score_in_rounds(self, first_round, last_round):
        return [in_paying_rounds.point_score for in_paying_rounds in
                self.in_rounds(first_round, last_round)]

    def get_player_endowment(self):
        return self.player_total_points * self.session.config["conversion_rate"] + self.session.config[
            "participation_fee"] + int(self.session.config["winning_bonus"] * self.winning)

    # Set index_of_paired_past_player, score_position and if possible sb_options + sa_options vars
    def get_pairs_with_past_player(self, sub_table, treatment=1):
        print(sub_table)

        def pair_with_random_past_player(sub_table, results_dict):
            excluded_indexed = results_dict["slightly_behind_to"] + results_dict["slightly_ahead_to"]
            full_list = sub_table.index.tolist()
            for index in excluded_indexed:
                full_list.remove(index)
            opponent_index = random.sample(full_list, 1)[0]
            self.index_of_paired_past_player = opponent_index
            # Opponents score higher than mine FB (SB & SA should be excluded)
            if sub_table.loc[opponent_index]["round_1"] > self.get_player_point_score_in_rounds(2, 2):

                self.score_position = "far_behind"
            else:
                self.score_position = "far_ahead"

        # Main body of function
        spread = int(self.session.config["pairing_filter_margin"])
        my_score = (self.get_player_point_score_in_rounds(2, 2))[0]
        results_dict = dict(slightly_behind_to=[],
                            slightly_ahead_to=[],)

        sub_table = sub_table[sub_table["treatment"] == (self.session.config["treatment"] - 1)]
        print(f"Before: {sub_table}")
        sub_table = sub_table[sub_table["gender"] == self.in_round(1).gender]
        print(f"After: {sub_table}")


        # SB filtering #
        filtered_table = sub_table[sub_table["round_1"] > my_score]
        filtered_table = filtered_table[filtered_table["round_1"] <= my_score + spread]
        if self.session.config["treatment"] == 2:
            filtered_table = filtered_table[filtered_table["winning_1"] == 1]
        # at least one match in SB
        if len(filtered_table.index):
            results_dict["slightly_behind_to"] = filtered_table.index.tolist()

            # SA filtering #
            filtered_table = sub_table[sub_table["round_1"] < my_score]
            filtered_table = filtered_table[filtered_table["round_1"] >= my_score + spread]
            if self.session.config["treatment"] == 2:
                filtered_table = filtered_table[filtered_table["winning_1"] == 0]
            if len(filtered_table.index):
                results_dict["slightly_ahead_to"] = filtered_table.index.tolist()
                # Save results to player attributes
                self.score_position = random.sample(results_dict.keys(), 1)[0]
                self.index_of_paired_past_player = random.sample(results_dict[self.score_position], 1)[0]
                self.sb_options = str(results_dict["slightly_behind_to"])[1:-1]
                self.sa_options = str(results_dict["slightly_ahead_to"])[1:-1]

            else:
                pair_with_random_past_player(sub_table, results_dict)
        else:
            pair_with_random_past_player(sub_table, results_dict)

        if "ahead" in self.score_position:
            self.winning = 1
        else:
            self.winning = 0
        # Add point of paired player to self.attributes
        self.paired_past_player_round_1_points = sub_table.loc[self.index_of_paired_past_player]["round_1"]
        self.paired_past_player_round_2_points = sub_table.loc[self.index_of_paired_past_player]["round_2"]

    # being called only in last round
    def calculate_winner_t1_t2(self):
        my_points = self.get_player_point_score_in_rounds(3, 3)[0]
        past_player_points = self.in_round(2).paired_past_player_round_2_points
        print(my_points, past_player_points)
        self.winning = self.subsession.determine_winner(my_points, past_player_points)[0]




