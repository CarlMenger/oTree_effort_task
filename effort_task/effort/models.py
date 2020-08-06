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
import copy
import logging
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
    num_rounds = 2
    grouping_order_keywords = {
        "score_ahead_high": "You are significantly ahead in score compared to the other player in the group",
        "score_ahead_low": "You are slightly ahead in score compared to the other player in the group",
        "score_equal": "You have the same score compared to the other player in the group",
        "score_behind_low": "You are slightly behind in score compared to the other player in the group",
        "score_behind_high": "You are significantly behind in score compared to the other player in the group",
    }
    # TaskStage variables

    def countdown_timer(self):
        return 5

    score_position_bound = 0.2# 0.2 == 20 % difference

class Subsession(BaseSubsession):
    def point_score_everyone(self):
        return [p.point_score for p in self.get_players()]

    def show_player_matrix(self):
        return self.get_group_matrix()

    def create_group_matrix(self):
        # find if starting from index 0 or 1 gives less average differences between pairs
        def pairing_algorithm(scores_all):
            pair_combinations = []
            for index in range(0, len(scores_all), 2):
                try:
                    pair_combinations.append([scores_all[index], scores_all[index + 1]])
                except IndexError:
                    # except is point pairing if uneven players, adding second highest score to be paired with 3rd and 1 st
                    pair_combinations.append([scores_all[index], scores_all[index - 1]])

            return pair_combinations

        # add ids to point matrix
        def create_point_ids(points_all):
            return dict(enumerate(points_all, start=1))

        # points_ids --> dict of id:points, point_matrix --> list of list of points (same as group_matrix)
        def convert_points_to_ids(points_ids, point_matrix):
            for group_index in range(len(point_matrix)):
                for point_index in range(len(point_matrix[group_index])):
                    value = point_matrix[group_index][point_index]
                    try:
                        key = (list(points_ids.keys())[list(points_ids.values()).index(value)])
                        point_matrix[group_index][point_index] = key
                        points_ids.pop(key, -999)
                    except ValueError:
                        # if uneven players, point matrix has one more element than ids, uses last
                        point_matrix[group_index][point_index] = point_matrix[group_index - 1][point_index]
            return point_matrix

        points_all = self.point_score_everyone()
        point_matrix = pairing_algorithm(sorted(points_all))
        points_ids = create_point_ids(points_all)
        new_group_matrix = convert_points_to_ids(points_ids, point_matrix)
        return new_group_matrix

    def group_based_on_score(self):
        if self.round_number == 1:  # regrouping limited to first game
            output = self.create_group_matrix()
            self.set_group_matrix(output)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    point_score = models.PositiveIntegerField(initial=0)
    piece_rate = models.IntegerField(initial=8)
    task_stage_timeout_seconds = models.IntegerField(initial=35)

    def other_player_score(self):
        return self.get_others_in_group()[0].point_score

    def player_point_score(self):
        return self.point_score

    def get_score_position(self):
        other_player_score = self.other_player_score()
        try:
            score_difference = (other_player_score - self.point_score) /\
                           (self.point_score + other_player_score / 2)
        except ZeroDivisionError:
            score_difference = 0

        if score_difference >= Constants.score_position_bound:
            return Constants.grouping_order_keywords["score_ahead_high"]
        elif 0.2 > score_difference > 0:
            return Constants.grouping_order_keywords["score_ahead_low"]
        elif score_difference == 0:
            return Constants.grouping_order_keywords["score_equal"]
        elif 0 > score_difference > - Constants.score_position_bound:
            return Constants.grouping_order_keywords["score_behind_low"]
        elif - 0.2 >= score_difference:
            return Constants.grouping_order_keywords["score_behind_high"]
