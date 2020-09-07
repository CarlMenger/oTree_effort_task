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

logging.basicConfig(level=logging.DEBUG,
                    filename="example2.log",
                    format='%(asctime)s %(message)s')


author = "Carl_Menger"

doc = """
Separate players based on real effort task into group competing against each other
"""


class Constants(BaseConstants):
    name_in_url = "StopLookingAtUrl"
    players_per_group = None
    num_rounds = 3
    grouping_order_keywords = {
        "score_ahead_high": "You are significantly ahead in score compared to the other player in the group",
        "score_ahead_low": "You are slightly ahead in score compared to the other player in the group",
        "score_equal": "You have the same score compared to the other player in the group",
        "score_behind_low": "You are slightly behind in score compared to the other player in the group",
        "score_behind_high": "You are significantly behind in score compared to the other player in the group",
    }


class Subsession(BaseSubsession):

    def point_score_everyone(self):
        return [p.point_score for p in self.get_players()]

    def show_player_matrix(self):
        return self.get_group_matrix()

    def calculate_payoff_table(self):
        pass

    def create_record_files(self):
        def get_records():
            records = ([[player.point_score for player in player.in_all_rounds()] for player in
                    self.get_players()])
            print(records)
            records_df = pandas.DataFrame(records)
            records_df.to_csv("score_records.csv")

        def get_payfile():
            payfile = [player.get_payoff() for player in self.get_players()]
            print(payfile)
            payfile_df = pandas.DataFrame(payfile)
            payfile_df.to_csv("payfile.txt")

        get_records()
        get_payfile()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    point_score = models.PositiveIntegerField(initial=0)
    piece_rate = models.IntegerField(initial=8)
    task_stage_timeout_seconds = models.IntegerField(initial=35)

    def other_player_score(self):
        pass
        #TODO

    def player_point_score(self):
        return self.point_score

    def participant_label(self):
        return self.participant.label

    def get_payoff(self):
        return sum([player_in_all_rounds.point_score for player_in_all_rounds in self.in_rounds(2, 3)]) * \
               self.session.config["conversion_rate"] + self.session.config["participation_fee"]
