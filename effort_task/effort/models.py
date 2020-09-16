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
import pandas
import logging
import time

logging.basicConfig(level=logging.ERROR,
                    filename="D:\\__OTree\\__DP - effort task\\TestDataDumps\\debug_log.log",
                    format='%(asctime)s %(message)s'
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
    pc_name__list_203 = [[i, f"VT_205 - {i}"] for i in range(1, 25)]
    date_time = time.asctime(time.localtime(time.time()))

class Subsession(BaseSubsession):

    # unused methods
    def point_score_everyone(self):
        return [p.point_score for p in self.get_players()]

    def show_player_matrix(self):
        return self.get_group_matrix()

    def calculate_payoff_table(self):
        pass

    # Grouping set up
    def creating_session(self):
        # Shuffle players randomly at the start
        self.group_randomly()

    def group_players(self):
        # no feedback random matching
        if self.session.config["treatment"] == 0:
            self.group_like_round(1) # FIXME: is needed? shouldnt it stay the same?


        # single feedback
        elif self.session.config["treatment"] == 1:
            pass

        # double feedback
        elif self.session.config["treatment"] == 2:
            pass



    # Create payfile.txt and Score_records.csv
    def create_record_files(self):
        def get_records():
            timestr = time.strftime("%Y_%m_%d-%H_%M")
            file_dir = self.session.config["file_dir"]
            treatment = self.session.config["treatment"]

            # data lists
            scores_of_players = [[player.point_score for player in player.in_all_rounds()] for player in
                        self.get_players()]
            treatment_list = [treatment for _ in range(len(scores_of_players))]
            scores_of_players = [list(points) for points in zip(*scores_of_players)]


            # format data for pandas
            raw_data = dict(treatment=treatment_list,
                            round_0=scores_of_players[0],
                            round_1=scores_of_players[1],
                            round_2=scores_of_players[2],
                            )
            print(raw_data)
            # csv generation
            #pandas.DataFrame(raw_data).to_csv(f"{file_dir}\\score_records__T{treatment}__{timestr}.csv")

        def get_payfile():
            timestr = time.strftime("%Y_%m_%d-%H_%M")
            file_dir = self.session.config["file_dir"]
            # FIXME: redo this through the groups not players,
            payments = [player.get_player_endowment() for player in self.get_players()]
            pc_names = [player.pc_name for player in self.get_players()]
            payfile_data = dict(pc_name=pc_names,
                                payment=payments,)
            # txt generation
            pandas.DataFrame(payfile_data).to_csv(f"{file_dir}\\payfile_{timestr}.txt", sep="\t")

        get_records()
        get_payfile()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
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
    pc_name = models.IntegerField()
    player_total_points = models.IntegerField()

    def pc_name_choices(self):
        if self.room_name == 205:
            return Constants.pc_name_list_205
        elif self.room_name == 203:
            return Constants.pc_name__list_203
        else:
            return ["error"]

    def other_player_score(self):
        pass
        #TODO

    def player_point_score(self):
        return self.point_score

    def participant_label(self):
        return self.participant.label

    # sum of points in paying rounds
    def get_player_total_points(self, first_round, last_round):
        return sum(
            [score_in_paying_rounds.point_score for score_in_paying_rounds in self.in_rounds(first_round, last_round)])

    def get_player_endowment(self):
        if self.player_total_points:
            return self.player_total_points * self.session.config["conversion_rate"] + self.session.config[
                "participation_fee"] + int(self.session.config["winning_bonus"] * self.winning)
        else:
            player_points = self.get_player_total_points(2, 3)
            payoff = player_points * self.session.config["conversion_rate"] + self.session.config[
                "participation_fee"] + int(self.session.config["winning_bonus"] * self.determine_winner())
            return payoff

    def determine_winner(self):
        if self.session.config["treatment"] == 0:
            player1_points = self.get_player_total_points(2,3)
            player_2 = self.get_others_in_group()[0]
            player2_points = player_2.get_player_total_points(2,3)
        else:
            player1_points = self.get_player_total_points(3, 3)
            player2_points = 666 # TODO
        if player1_points > player2_points:
            self.winning = 1
            self.player_2.winning = 0
        elif player1_points == player2_points:
            self.winning = 0.5
            self.player_2.winning = 0.5
        else:
            self.winning = 0
            self.player_2.winning = 1
        self.player_2.player_total_points = player2_points

        # TODO: self.player_2 is bullshit