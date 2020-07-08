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
    grouping_order_keywords = {"score_ahead_high":"",
                      "score_ahead_low":"",
                      "score_equal":"",
                      "score_behind_low":"",
                      "score_behind_high":"" ,
                      }
    # TaskStage variables
    countdown_timer = 5


class Subsession(BaseSubsession):
    def point_score_everyone(self):
        return [p.point_score for p in self.get_players()]

    def create_group_matrix(self):
        # find if starting from index 0 or 1 gives less average differences between pairs
        def pairing_algorithm(scores_all):
            mean_differences = [-1, -1]
            pair_combinations = [[], []]
            for shift in range(2):
                difference = 0
                for index in range(0, len(scores_all) - shift - 1, 2):
                    difference += abs(scores_all[index + shift] - scores_all[index + shift + 1])
                    pair_combinations[shift].append([scores_all[index + shift], scores_all[index + shift + 1]])
                mean_differences[shift] = difference / (len(scores_all))
            print(mean_differences)
            print(pair_combinations[0])
            print(pair_combinations[1])
            return pair_combinations[mean_differences.index(min(mean_differences))]

        # FIXME: pair the leftover subjects
        #points_ids --> dict of id:points, point_matrix --> list of list of points (same as group_matrix)
        def convert_points_to_ids(points_ids, point_matrix):
            id_matrix = copy.deepcopy(point_matrix)
            for group_index in range(len(point_matrix)):
                for point_index in range(len(point_matrix[group_index])):
                    id_matrix[group_index][point_index] = points_ids.pop(point_matrix[group_index][point_index], -1)
            return id_matrix

        def create_point_ids(points_all):
            return dict(list(enumerate(points_all, start=1)))

        points_all = self.point_score_everyone
        point_matrix = pairing_algorithm(sorted(points_all))
        points_ids = create_point_ids(points_all)
        # FIXME: return this to original state
        output = convert_points_to_ids(points_ids, point_matrix)
        logging.info(f"group_matrix is : {output}")
        return output
        #return convert_points_to_ids(points_ids, point_matrix)

    def group_based_on_score(self):
        self.set_group_matrix(self.create_group_matrix())


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


