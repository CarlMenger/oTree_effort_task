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
                    filename="debug_log.log",
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
        "score_ahead": "You are slightly ahead in score compared to the other player in your group",
        "score_behind": "You are slightly behind in score compared to the other player in your group",
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
            treatment = self.session.config["treatment"]
            timestr = time.strftime("%Y_%m_%d-%H_%M")
            file_dir = self.session.config["file_dir"]
            records = [treatment, *[[player.point_score for player in player.in_all_rounds()] for player in
                        self.get_players()]]
            logging.debug(F"records: {records}")
            pandas.DataFrame(records, columns=["treatment", *[f"Round_{round}" for round in range(Constants.num_rounds)],
                                               ]).to_csv(
                f"{file_dir}\\score_records__T{treatment}__{timestr}.csv")

        def get_payfile():
            timestr = time.strftime("%Y_%m_%d-%H_%M")
            file_dir = self.session.config["file_dir"]
            payfile = [player.get_payoff() for player in self.get_players()]

            payfile_df = pandas.DataFrame(payfile, columns=[
                "Payment"])  # FIXME might need exeption if #n of colums is different from #n of arguments
            payfile_df.to_csv( f"{file_dir}\\payfile_{timestr}.txt")

        get_records()
        get_payfile()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    point_score = models.PositiveIntegerField(initial=0)
    piece_rate = models.IntegerField(initial=8)  #TODO: Used anywhere ?
    task_stage_timeout_seconds = models.IntegerField(initial=35)

    def other_player_score(self):
        pass
        #TODO

    def player_point_score(self):
        return self.point_score

    def participant_label(self):
        return self.participant.label

    def get_payoff(self):
        return sum([score_in_all_rounds.point_score for score_in_all_rounds in self.in_rounds(2, 3)]) * \
               self.session.config["conversion_rate"] + self.session.config["participation_fee"] + \
               self.session.config["winning_bonus"]



# TODO: get_payoff need winning bonus