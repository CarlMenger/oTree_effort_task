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


author = "Carl_Menger"

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = "StopLookingAtUrl"
    players_per_group = 2
    num_rounds = 4
    grouping_order_keywords = {"score_ahead_high":"",
                      "score_ahead_low":"",
                      "score_equal":"",
                      "score_behind_low":"",
                      "score_behind_high":"" ,
                      }


class Subsession(BaseSubsession):
    def group_players(self):
        point_score_everyone = [p.point_score for p in self.get_players()].sort()
        # TODO


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    point_score = models.PositiveIntegerField()
    piece_rate = models.IntegerField(initial=8)

    def other_player_score(self):
        return self.get_others_in_group()[0].point_score


