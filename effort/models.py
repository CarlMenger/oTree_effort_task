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

"""logging.basicConfig(level=logging.INFO,
                    filename="D:\\__OTree\\test-carl\\effort\\data\\DB_debug.log",
                    format="%(asctime)s: %(message)s",
                    filemode="a",
                    )"""

logger = logging.getLogger('server_logger')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('server.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

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
    pc_name_list_205 = [[i, f"VT_205 - {i}"] for i in range(1, 19)]     # FIXME: DELETE THIS AFTER TESTING
    pc_name_list_203 = [[i, f"VT_203 - {i}"] for i in range(1, 25)]     # FIXME: DELETE THIS AFTER TESTING
    date_time = time.asctime(time.localtime(time.time()))
    results_page_timeout_seconds = 30
    task_stage_timeout_seconds = 35  # 30 sec game time + 5 sec prep time
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(BASE_DIR, "effort", "data")


class Subsession(BaseSubsession):
    """    def get_treatment(self):
            return self.session.config["treatment"]
        t = get_treatment()
        treatment = models.IntegerField(initial=t)"""
    dir_path = models.StringField(initial=Constants.path)

    def after_task_stage(self):
        """
        Transfer data fields point_score, overall_keystroke_count to fields according to round
        :return: None
        """
        current_round = self.round_number
        if current_round == 1:
            for p in self.get_players():
                p.point_score_0 = p.point_score
                p.overall_keystroke_count_0 = p.overall_keystroke_count
        elif current_round == 2:
            for p in self.get_players():
                p.point_score_1 = p.point_score
                p.overall_keystroke_count_1 = p.overall_keystroke_count
        elif current_round == 3:
            for p in self.get_players():
                p.point_score_2 = p.point_score
                p.overall_keystroke_count_2 = p.overall_keystroke_count
            for p in self.get_players():  # Needs to finish assigning points before comparing
                p.compare_players()
                #p.total_points = p.in_round(2).point_score_1 + p.point_score_2

    def test_db(self):
        for player in self.get_players():
            player.test_db_loading()

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

    def pair_players(self):
        """ pair players after first round (trial task) using 2 separate loops for T0 and T{x}
            """
        self.group_like_round(1)

        if self.round_number == 2:
            if self.session.config["treatment"] == 0:
                for player in self.get_players():
                    player.t0_randomly_select_opponents()
                    player.compare_players()

            else:
                for player in self.get_players():
                    player.find_score_position_options()
                    player.choose_position_option()

    """         p1 = group.get_players()[0]
                p2 = group.get_players()[1]
                first_player_score_r2 = p1.get_player_point_score_in_rounds(1, 1)[0]
                second_player_score_r2 = p2.get_player_point_score_in_rounds(1, 1)[0]
                results = self.determine_winner(first_player_score_r2, second_player_score_r2)
                p1.winning = results[0]
                p2.winning = results[1]"""

    def create_record_files(self):
        """
        1) create_score_records: make actual .csv and .js data set in app data folder
            """

        def create_score_records():
            timestr = time.strftime("%Y_%m_%d-%H_%M")
            file_dir = Constants.path
            treatment = self.session.config["treatment"]

            # TODO  --> use pd.insert(pos,[data]) for positions of columns
            player_info = {}
            df = pd.DataFrame()
            for player in self.get_players():
                player_info["date"] = timestr
                player_info["treatment"] = treatment
                player_info["gender"] = player.in_round(1).gender

                player_info["point_score_0"] = player.in_round(1).point_score_0
                player_info["point_score_1"] = player.in_round(2).point_score_1
                player_info["point_score_2"] = player.in_round(3).point_score_2

                player_info["overall_keystroke_count_0"] = player.in_round(1).overall_keystroke_count_0
                player_info["overall_keystroke_count_1"] = player.in_round(2).overall_keystroke_count_1
                player_info["overall_keystroke_count_2"] = player.in_round(3).overall_keystroke_count_2

                player_info["winning_1"] = player.in_round(2).winning_1
                player_info["winning_2"] = player.in_round(3).winning_2

                player_info["my_player_id"] = player.in_round(2).my_player_id
                player_info["index_of_paired_player"] = player.in_round(2).id_of_paired_player

                player_info["slightly_behind_to"] = player.in_round(2).sb_options
                player_info["slightly_ahead_to"] = player.in_round(2).sa_options
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

        # In last round call to create dataframes and payfile
        create_score_records()


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    gender = models.IntegerField(widget=widgets.RadioSelect,
                                 choices=[
                                     [0, "male"],
                                     [1, "female"],
                                 ]
                                 )
    # FIXME: DELETE THIS AFTER TESTING
    """    room_name = models.IntegerField(choices=[ 
        [203, " VT 203 "],
        [205, " VT 205 "]
    ]
    )"""
    # General fields
    treatment = models.IntegerField()
    label = models.StringField()  # REWRITE ME based on ztree version
    winning_1 = models.PositiveIntegerField()
    winning_2 = models.PositiveIntegerField()

    point_score = models.PositiveIntegerField()
    point_score_0 = models.PositiveIntegerField()
    point_score_1 = models.PositiveIntegerField()
    point_score_2 = models.PositiveIntegerField()
    total_points = models.IntegerField()
    paired_player_round_1_points = models.PositiveIntegerField()
    paired_player_round_2_points = models.PositiveIntegerField()

    overall_keystroke_count = models.PositiveIntegerField()
    overall_keystroke_count_0 = models.PositiveIntegerField()
    overall_keystroke_count_1 = models.PositiveIntegerField()
    overall_keystroke_count_2 = models.PositiveIntegerField()

    my_player_id = models.StringField(initial=None)
    id_of_paired_player = models.StringField(initial=None)

    # T1 T2 specific fields
    sb_options = models.StringField()
    sa_options = models.StringField()
    score_position = models.StringField(initial="T0")
    # DEBUG ONLY
    # FIXME: DELETE THIS AFTER TESTING
    """    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(BASE_DIR, "effort", "data")
    Ts_score_difference = models.IntegerField()
    dir_path = models.StringField(initial=path)"""

    def t0_randomly_select_opponents(self):
        """
        randomly choose from all players with id_of_paired_player == None, save "id" to player.id_of_paired_player,
        set player.paired_player_round_1_points

        """
        # TODO: add assert
        available_players = [player for player in self.get_others_in_subsession()]
        player = random.sample(available_players, 1)[0]
        self.id_of_paired_player = str(player.__repr__()[1:-1])
        self.my_player_id = str(self.__repr__()[1:-1])

    def compare_players(self):
        # Look up player object based on .__repr__() saved in DB field
        current_round = self.round_number
        paired_player = [player for player in self.subsession.in_round(2).get_players() if
                         player.__repr__()[1:-1] == self.in_round(2).id_of_paired_player][0]
        if current_round == 2:
            opponent_points = paired_player.point_score_1
            self.paired_player_round_1_points = opponent_points
            results = self.subsession.determine_winner(self.point_score_1, opponent_points)
            self.winning_1 = results[0]

        elif current_round == 3:
            opponent_points = paired_player.in_round(3).point_score_2
            self.paired_player_round_2_points = opponent_points
            results = self.subsession.determine_winner(self.point_score_2, opponent_points)
            self.winning_2 = results[0]
            self.total_points = self.in_round(2).point_score_1 + self.point_score_2

    def find_score_position_options(self):
        """
        From DB find all options for sb_position, sa_position, write it into DB
        :return:
        """
        my_points = self.point_score_1
        spread = self.session.config["pairing_filter_margin"]
        basic_query = Player.objects.filter(treatment=self.in_round(1).treatment - 1, gender=self.in_round(1).gender)
        # Looking for sb_option to:
        sb_options_q = basic_query.filter(round_score_1__range=[my_points + 1, my_points + spread])
        sb_options_ids = [option["id"] for option in sb_options_q]


        # Looking for sa_option to:
        sa_options_q = basic_query.filter(round_score_1__range=[my_points - spread, my_points - 1])
        sa_options_ids = [option["id"] for option in sa_options_q]

    def choose_position_option(self):
        """
        Choose one index from either sa_position or sb_position. If there is no record in both options at the same time
        choose index randomly but exclude any index from sb_option or sa_option.
        :return:
        """
    def test_db_loading(self):
        def display_query_data():
            """ Query data from DB and retrun them in usable form """
            my_points = 90
            spread = 2
            basic_query = Player.objects.filter(treatment=self.in_round(1).treatment - 1,
                                                gender=self.in_round(1).gender)

            # Looking for sb_option to:
            filtered = basic_query.filter(round_score_1__range=[my_points + 1, my_points + spread])
            id_f = filtered["id"]
            logger.info(f"Query filtered : {filtered}")
            logger.info(f"Listed filter {list(filtered)}")
            logger.info(f"Listed filter {id_f}")


        self.treatment = self.session.config["treatment"]
        if self.treatment > 0:
            query_table =  display_query_data()

    def player_point_score(self):
        return self.point_score

    def participant_label(self):
        return self.participant.label

    # FIXME: DELETE THIS AFTER TESTING
    # list of points in paying rounds x to y, + 1 to keep pythonic indexing for rounds
    def get_player_point_score_in_rounds(self, first_round, last_round):
        return [in_paying_rounds.point_score for in_paying_rounds in
                self.in_rounds(first_round + 1, last_round + 1)]

    def get_pairs_after_trial_task_for_t1_t2(self, sub_table):
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
            sub_table = sub_table[sub_table["treatment"] == (self.session.config["treatment"] - 1)] # FIXME: do this with Qset beforehand
            sub_table = sub_table[sub_table["gender"] == self.in_round(1).gender]  # FIXME: do this with Qset beforehand

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
        self.total_points = my_points
        assert (0 < round_1 < 3), "Function calculate_winner_t1_t2_for_rounds received false argument #1 "
        assert (0 < round_2 < 3 and round_1 <= round_2), \
            "Function calculate_winner_t1_t2_for_rounds received false argument #2 or #1 > #2"
        past_player_points = self.in_round(2).paired_past_player_round_1_points + \
                             self.in_round(2).paired_past_player_round_2_points * (round_2 - round_1)
        self.winning = self.subsession.determine_winner(my_points, past_player_points)[0]


