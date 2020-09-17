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
    pc_name_list_203 = [[i, f"VT_203 - {i}"] for i in range(1, 25)]
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

        def create_score_records():
            timestr = time.strftime("%Y_%m_%d-%H_%M")
            file_dir = self.session.config["file_dir"]
            treatment = self.session.config["treatment"]

            # data lists # TODO more relaible version, where order of lines of code is not deteriminal to
            # TODO headers
            player_info = []
            raw_data = []
            for player in self.get_players():
                player_info.append(timestr)
                player_info.append(treatment)
                player_info.append(player.in_round(1).room_name)
                player_info.append(player.in_round(1).pc_name)
                for round in player.get_player_point_score_in_rounds(1, 3):
                    player_info.append(round)
                player_info.append(player.in_round(1).gender)
                player_info.append(player.winning) # TODO: win for all rounds
                player_info.append(player.get_others_in_group()[0].room_name)
                player_info.append(player.get_others_in_group()[0].pc_name)
                raw_data.append(player_info)
                player_info = []

            columns = [list(column) for column in zip(*raw_data)]

            # format data for pandas
            raw_data = dict(date=columns[0],
                            treatment=columns[1],
                            room_name=columns[2],
                            pc_name=columns[3],
                            round_0=columns[4],
                            round_1=columns[5],
                            round_2=columns[6],
                            gender=columns[7],
                            win=columns[8],
                            other_player_room_name=columns[9],
                            other_player_pc_name=columns[10],
                            )
            print(raw_data)
            # csv generation
            pandas.DataFrame(raw_data).to_csv(f"{file_dir}\\score_records__T{treatment}__{timestr}.csv")

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
            pandas.DataFrame(payfile_data).to_csv(f"{file_dir}\\payfile_{timestr}.txt", sep="\t")

        [group.calculate_points_wins_payments() for group in self.get_groups()]
        #calculate_points_wins_payments()
        create_score_records()
        create_payfile()


    def determine_winner(self, player1_points, player2_points):
        if player1_points > player2_points:
            return [1.0,0.0]
        elif player1_points < player2_points:
            return [0.0, 1.0]
        else:
            return [0.5, 0.5]


class Group(BaseGroup):
    def calculate_points_wins_payments(self):
        # Load up players in this group
        p1, p2 = self.get_players()

        # Load point scores of players
        p1_points = p1.get_player_point_score_in_rounds(2, 3)
        p2_points = p2.get_player_point_score_in_rounds(2, 3)

        # Write down total points to player attribute
        p1.player_total_points = sum(p1_points)
        p2.player_total_points = sum(p2_points)

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
        return [score_in_paying_rounds.point_score for score_in_paying_rounds in
                self.in_rounds(first_round, last_round)]

    def get_player_endowment(self):
        return self.player_total_points * self.session.config["conversion_rate"] + self.session.config[
            "participation_fee"] + int(self.session.config["winning_bonus"] * self.winning)
