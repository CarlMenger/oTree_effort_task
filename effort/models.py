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
import pprint

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


class Subsession(BaseSubsession):

    # unused methods
    #def point_score_everyone(self):
    #    return [p.point_score for p in self.get_players()]

    #def show_player_matrix(self):
    #    return self.get_group_matrix()

    # Grouping set up
    def creating_session(self):
        # Shuffle players randomly at the start
        self.group_randomly()

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
            for player in self.get_players():
                player.get_pairs_with_past_player(sub_table)# FIXME

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
                player_info["room_name"] = player.in_round(1).room_name
                player_info["pc_name"] = player.in_round(1).pc_name
                for round in player.get_player_point_score_in_rounds(1, 3):
                    player_info[f"round_{index_}"] = round
                    index_ += 1
                index_ = 0
                player_info["gender"] = player.in_round(1).gender
                player_info["winning_1"] = player.in_round(1).winning
                player_info["winning_2"] = player.in_round(2).winning
                player_info["other_room_name"] = player.get_others_in_group()[0].in_round(1).room_name
                player_info["other_pc_name"] = player.get_others_in_group()[0].in_round(1).pc_name
                df = df.append(player_info, ignore_index=True)
                player_info = {}
            columns = ["date", "treatment", "gender", "room_name", "pc_name", "round_0", "round_1", "round_2",
                       "winning_1", "winning_1",]

            # csv generation
            # if add_to_central_DB == 1, also update CSR (all sessions combined df)
            if self.session.config["add_to_central_DB"]:
                if not os.path.isfile(f"{file_dir}\\Central_Score_Records.json"):
                    df.to_json(f"{file_dir}\\Central_Score_Records.json")
                csr = pd.read_json(f"{file_dir}\\Central_Score_Records.json")
                # TODO?: concat(keys=treatments),
                df.reset_index(inplace=True, drop=True)
                csr.reset_index(inplace=True, drop=True) # TODO: now to check if it does not fuck up previous csr
                pd.concat([csr, df], ignore_index=True).to_json(f"{file_dir}\\Central_Score_Records.json")

            # Always create session records
            df.to_json(f"{file_dir}\\score_records__T{treatment}__{timestr}.json")

        def create_payfile():
            timestr = time.strftime("%Y_%m_%d-%H_%M")
            file_dir = self.session.config["file_dir"]
            # FIXME: is payments ok ?
            payments = [player.get_player_endowment() for player in self.get_players()]
            room_name = [player.room_name for player in self.get_players()]
            winning = [player.winning for player in self.get_players()]
            pc_names = [player.pc_name for player in self.get_players()]
            gender = [player.gender for player in self.get_players()]

            payfile_data = dict(room_name=room_name,
                                pc_name=pc_names,
                                gender=gender,
                                payment=payments,
                                has_won=winning,)
            # txt generation
            pd.DataFrame(payfile_data).to_csv(f"{file_dir}\\payfile_{timestr}.txt", sep="\t")

        [group.calculate_points_wins_payments_t0() for group in self.get_groups()]
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
    score_position_options = models.LongStringField()
    score_position = models.StringField()
    point_score = models.PositiveIntegerField(initial=0)
    winning = models.PositiveIntegerField(initial=0.0)
    task_stage_timeout_seconds = models.IntegerField(initial=35)
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

    player_total_points = models.IntegerField(initial=0)
    player_payment = models.IntegerField(initial=0)
    pc_name = models.IntegerField()

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

    # Get index or id of "past" player who their are both slightly_behind and slightly_ahead compared to that index
    def get_pairs_with_past_player(self, sub_table, treatment=1):
        spread = int(self.session.config["pairing_filter_margin"])
        my_score = (self.get_player_point_score_in_rounds(2, 2))[0]
        results_dict = dict(slightly_behind_to=[],
                            slightly_ahead_to=[],)
        filtered_table = sub_table[sub_table["treatment"] == self.session.config["treatment"] - 1]
        filtered_table = filtered_table[filtered_table["gender"] == self.gender]

        # Find indexes matching the filter requirements for slightly_below interval
        filtered_table_sb = filtered_table[filtered_table["round_1"] > my_score]
        results_dict["slightly_behind_to"] = filtered_table_sb[
            filtered_table_sb["round_1"] <= (my_score + spread)].index.tolist()

        # Find indexes matching the filter requirements for slightly_ahead interval
        filtered_table_sa = filtered_table[filtered_table["round_1"] < my_score]
        results_dict["slightly_ahead_to"] = filtered_table_sb[
            filtered_table_sb["round_1"] >= (my_score - spread)].index.tolist()

        return results_dict  # REWRITE:for no interval, change <=/>= to == and ignore/coment first line in both filters
