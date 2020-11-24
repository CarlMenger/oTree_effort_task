from django.contrib.auth.models import User
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
    players_per_group = None
    num_rounds = 3
    all_score_positions = {
        "slightly_ahead": "You are slightly ahead in score compared to your opponent",
        "slightly_behind": "You are slightly behind in score compared to your opponent",
        "far_ahead": "You are far ahead in score compared to your opponent",
        "far_behind": "You are far behind in score compared to your opponent",
        "equal_position": "You have the same score as your opponent",
        "T0": ""  # Placeholder for T0 so it doesnt raise error
    }
    date_time = time.asctime(time.localtime(time.time()))
    results_page_timeout_seconds = 30
    task_stage_timeout_seconds = 35  # 30 sec game time + 5 sec prep time
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(BASE_DIR, "effort", "data")


class Subsession(BaseSubsession):

    dir_path = models.StringField(initial=Constants.path)

    def after_task_stage(self):
        """
        Transfer data fields point_score, overall_keystroke_count to fields according to round
        :return: None
        """
        treatment = self.session.config["treatment"]
        for p in self.get_players():
            p.treatment = treatment
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
            if treatment == 0:
                for p in self.get_players():  # Second loop because it needs to finish assigning points before comparing
                    p.paired_player_round_2_points = p.get_player_object_by_t0id(
                        p.in_round(2).id_of_paired_player).in_round(3).point_score_2
            for p in self.get_players():  # Third loop because I probably cant code properly
                p.compare_players()

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
        """ Main function for round 2 only.
            pair players after first round (trial task) using 2 separate loops for T0 and T{x}
            """
        self.group_like_round(1)
        treatment = self.session.config["treatment"]

        if treatment == 0:
            for player in self.get_players():
                player.t0_randomly_select_opponents()
                player.compare_players()

        else:
            for player in self.get_players():
                if self.session.config["use_csv_system"]:
                    player.pair_players_csv_system()
                else:
                    player.find_score_position_options()

    def create_record_files(self):
        """
        1) unload all data fields from different rounds into last round for DB (so round_number = self.round_numbers
            has all data)
        2) if enabled in settings: create_csv_files: make actual .csv and .json data files in app/data folder
               """

        timestr = time.strftime("%Y_%m_%d-%H_%M")
        file_dir = Constants.path
        treatment = self.session.config["treatment"]

        def create_csv_files():
            player_info = {}
            df = pd.DataFrame()
            for player in self.get_players():
                player_info["date"] = timestr
                player_info["treatment"] = treatment
                player_info["gender"] = player.gender
                player_info["label"] = player.in_round(1).label

                player_info["point_score_0"] = player.point_score_0
                player_info["point_score_1"] = player.point_score_1
                player_info["point_score_2"] = player.point_score_2

                player_info["paired_player_round_1_points"] = player.paired_player_round_1_points
                player_info["paired_player_round_2_points"] = player.paired_player_round_2_points

                player_info["overall_keystroke_count_0"] = player.overall_keystroke_count_0
                player_info["overall_keystroke_count_1"] = player.overall_keystroke_count_1
                player_info["overall_keystroke_count_2"] = player.overall_keystroke_count_2

                player_info["winning_1"] = player.winning_1
                player_info["winning_2"] = player.winning_2

                player_info["my_player_id"] = player.my_player_id
                player_info["index_of_paired_player"] = player.id_of_paired_player

                player_info["slightly_behind"] = player.sb_options
                player_info["slightly_ahead"] = player.sa_options
                player_info["score_position"] = player.score_position

                player_info["spread"] = player.session.config["pairing_filter_margin"]
                player_info["testing"] = player.session.config["testing"]

                df = df.append(player_info, ignore_index=True)
                player_info = {}

            # csv generation
            # if use_csv_system == True, also update CSR (all sessions combined df)
            if self.session.config["use_csv_system"]:
                if not os.path.isfile(f"{file_dir}\\Central_Score_Records.json"):
                    df.to_json(f"{file_dir}\\Central_Score_Records.json")
                    df.to_excel(f"{file_dir}\\Central_Score_Records.xlsx", engine="xlsxwriter")
                else:
                    csr = pd.read_json(f"{file_dir}\\Central_Score_Records.json")
                    df.reset_index(inplace=True, drop=True)
                    csr.reset_index(inplace=True, drop=True)
                    pd.concat([csr, df], ignore_index=True).to_json(f"{file_dir}\\Central_Score_Records.json")
                    pd.concat([csr, df], ignore_index=True).to_excel(f"{file_dir}\\Central_Score_Records.xlsx",
                                                                     engine="xlsxwriter")

            # Always create session records
            df.to_excel(f"{file_dir}\\score_records__T{treatment}__{timestr}.xlsx", engine='xlsxwriter')

        def unload_data_into_round_3():
            for p in self.get_players():
                p.date = timestr
                p.treatment = p.in_round(1).treatment
                p.gender = p.in_round(1).gender
                p.point_score_0 = p.in_round(1).point_score_0
                p.point_score_1 = p.in_round(2).point_score_1
                p.point_score_2 = p.in_round(3).point_score_2
                p.overall_keystroke_count_0 = p.in_round(1).overall_keystroke_count_0
                p.overall_keystroke_count_1 = p.in_round(2).overall_keystroke_count_1
                p.overall_keystroke_count_2 = p.in_round(3).overall_keystroke_count_2
                p.paired_player_round_1_points = p.in_round(2).paired_player_round_1_points
                p.paired_player_round_2_points = p.in_round(3).paired_player_round_2_points
                p.winning_1 = p.in_round(2).winning_1
                p.winning_2 = p.in_round(3).winning_2
                p.my_player_id = p.in_round(2).my_player_id
                p.id_of_paired_player = p.in_round(2).id_of_paired_player
                p.sb_options = p.in_round(2).sb_options
                p.sa_options = p.in_round(2).sa_options
                p.score_position = p.in_round(2).score_position
                p.payoff = p.winning_2 * self.session.config["winning_bonus"]
                p.participant.label = p.in_round(1).hroot_id

        # In last round call to create data frames
        unload_data_into_round_3()
        if self.session.config["use_csv_system"]:
            create_csv_files()


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    hroot_id = models.StringField(label="Unique ID")
    gender = models.IntegerField(widget=widgets.RadioSelect,
                                 choices=[
                                     [0, "male"],
                                     [1, "female"],
                                 ])
    # General fields
    treatment = models.IntegerField()
    date = models.StringField()
    label = models.StringField()
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

    def get_player_object_by_t0id(self, id):
        for player_object in self.subsession.in_round(2).get_players():
            if player_object.__repr__()[1:-1] == id:
                return player_object

    def t0_randomly_select_opponents(self):
        """
        randomly choose from all players with id_of_paired_player == None, save "id" to player.id_of_paired_player,
        set player.paired_player_round_1_points

        """
        if self.id_of_paired_player is None:
            try:
                available_players = [player for player in self.get_others_in_subsession() if
                                     player.id_of_paired_player is None and self.in_round(1).gender == player.in_round(
                                         1).gender]
                player = random.sample(available_players, 1)[0]
            except ValueError:  # if you get unbalanced uneven genders, pair with already paired guy
                available_players = [player for player in self.get_others_in_subsession() if
                                     self.in_round(1).gender == player.in_round(1).gender]
                player = random.sample(available_players, 1)[0]
            self.paired_player_round_1_points = player.point_score_1
            self.id_of_paired_player = str(player.__repr__()[1:-1])
            self.my_player_id = str(self.__repr__()[1:-1])
            player.id_of_paired_player = self.my_player_id
            player.my_player_id = self.id_of_paired_player
            player.paired_player_round_1_points = self.in_round(2).point_score_1

    def tx_randomly_select_opponents(self, restricted_options, basic_query):
        allowed_ids = basic_query not in restricted_options
        self.id_of_paired_player = str(random.sample(allowed_ids, 1)[0])

    def compare_players(self):
        """
        Load up both paired players scores, compare them and set winning
        :return: None
        """
        # Look up player object based on .__repr__() saved in DB field
        if self.round_number == 2:
            results = self.subsession.determine_winner(self.point_score_1, self.paired_player_round_1_points)
            self.winning_1 = results[0]

        elif self.round_number == 3:
            self.total_points = self.in_round(2).point_score_1 + self.point_score_2
            try:
                results = self.subsession.determine_winner(self.total_points,
                                                           self.in_round(2).paired_player_round_1_points +
                                                           self.paired_player_round_2_points)
            except TypeError:
                results = self.subsession.determine_winner(self.total_points,
                                                           self.in_round(2).paired_player_round_1_points +
                                                           self.in_round(2).paired_player_round_2_points)

            self.winning_2 = results[0]

    def find_score_position_options(self):
        """
        From DB find all options for sb_position, sa_position, write it into DB
        :return: None
        """
        my_points = self.point_score_1
        spread = self.session.config["pairing_filter_margin"]
        treatment = self.session.config["treatment"]
        basic_query = Player.objects.filter(treatment=self.in_round(1).treatment - 1,
                                            gender=self.in_round(1).gender,
                                            round_number=Constants.num_rounds,
                                            )
        # Looking for sb_option to:
        sb_options_q = basic_query.filter(point_score_1__range=[my_points + 1, my_points + spread])
        if treatment == 2:
            sb_options_q = sb_options_q.filter(winning_1=1)
        sb_options_ids = [option.id for option in sb_options_q]
        # Looking for sa_option to:
        sa_options_q = basic_query.filter(point_score_1__range=[my_points - spread, my_points - 1])
        if treatment == 2:
            sa_options_q = sa_options_q.filter(winning_1=0)
        sa_options_ids = [option.id for option in sa_options_q]
        all_options_dict = {"slightly_ahead": sa_options_ids, "slightly_behind": sb_options_ids}
        all_options = [*sa_options_ids, *sb_options_ids]

        if len(sa_options_ids) > 0 and len(sb_options_ids) > 0:
            self.score_position = str(random.sample(all_options_dict.keys(), 1)[0])
            self.id_of_paired_player = str(random.sample(all_options_dict[self.score_position], 1)[0].id)

        else:
            self.tx_randomly_select_opponents(all_options, basic_query)

        paired_player_object = Player.objects.filter(id=self.id_of_paired_player)[0]
        self.paired_player_round_1_points = paired_player_object.point_score_1
        self.paired_player_round_2_points = paired_player_object.point_score_2
        self.winning_1 = paired_player_object.winning_1
        self.winning_2 = paired_player_object.winning_2

    def test_db_loading(self):  # REWRITE ME: DELETE THIS AFTER TESTING
        def display_query_data():
            """ Query data from DB and return them in usable form """
            my_points = 90
            spread = 4
            fil = []
            basic_query = Player.objects.filter(treatment=self.in_round(1).treatment - 1,
                                                gender=self.in_round(1).gender,
                                                round_number=Constants.num_rounds,
                                                )
            # Looking for sb_option to:
            filtered_sb = basic_query.filter(point_score_1__range=[my_points + 1, my_points + spread])
            filtered_sa = basic_query.filter(point_score_1__range=[my_points - spread, my_points - 1, ])

            #id_f = [filtered_sb.id, filtered_sa.id]
            #logger.info(f"Listed filter {id_f}")
            try:
                if len(filtered_sa) > 0:
                    fil.append((filtered_sa))
                if len(filtered_sb) > 0:
                    fil.append((filtered_sb))
                logger.info(f"Query filtered : {filtered_sb,filtered_sa}")
                logger.info(f"Listed filter {list(filtered_sb), list(filtered_sa)}")
                logger.info(f"single player {fil[0] }")
            except:
                pass

            try:
                logger.info(f"fil[0].id {fil[0][0].id}")
            except:
                pass

        self.treatment = self.session.config["treatment"]
        if self.treatment > 0:
            display_query_data()

    def player_point_score(self):
        return self.point_score

    def participant_label(self):
        return self.participant.label

    def pair_players_csv_system(self):
        """ Set id_of_paired_player, score_position and if possible sb_options + sa_options vars
            Called after trial task """

        def load_csv_data():
            """
            Load .json file from BASE_DIR <data_folder>
            :return: pandas data frame with important columns
            """
            wanted_data_columns = ["treatment", "gender", "point_score_1", "point_score_2", "winning_1", "winning_2", ]
            file_dir = Constants.path
            df_csr = pd.read_json(f"{file_dir}\\Central_Score_Records.json")
            sub_table = df_csr[wanted_data_columns].dropna()
            return sub_table

        def find_score_position_for_unmatched_players(my_score, spread):
            """
            Find score position for players not eligible for SB nor SA
            :param my_score: self.point_score_1
            :param spread:
            :return: None
            """
            if not self.score_position or self.score_position == "T0":
                # FIXME: after testing delete error parts and simplify
                if self.paired_player_round_1_points > my_score:
                    if self.paired_player_round_1_points <= (my_score + spread):
                        self.score_position = "error1"
                    else:
                        self.score_position = "far_behind"
                elif self.paired_player_round_1_points < my_score:
                    if self.paired_player_round_1_points >= (my_score - spread):
                        self.score_position = "error2"
                    else:
                        self.score_position = "far_ahead"
                else:
                    self.score_position = "equal_position"

            """
                if self.paired_player_round_1_points > my_score:
                        self.score_position = "far_behind"
                elif self.paired_player_round_1_points < my_score:
                        self.score_position = "far_ahead"
                else:
                    self.score_position = "equal_position"
            """

        def pair_with_random_past_player(sub_table, position_options, disallowed_indexes):
            """
            Randomly search for index of player to be matched with
            :param sub_table: pandas data frame with -g-t rows.
            :param position_options:
            :param disallowed_indexes: indexes of either SA or SB option, thus not eligible for random search
            :return: None
            """
            index_all = sub_table.index.tolist()
            all_disallowed_indexes = disallowed_indexes + list(position_options.values())
            flat_list = [item for sublist in all_disallowed_indexes for item in sublist]
            index_clean = [index for index in index_all if index not in flat_list]
            opponent_index = random.sample(index_clean, 1)[0]
            self.id_of_paired_player = str(opponent_index)
            #print(f"{self.participant_label()} says: I was randomly matched")

        def find_score_position(sub_table):
            disallowed_indexes = []
            position_options = {"slightly_behind": [],
                                "slightly_ahead": [],
                                }
            sub_table = sub_table[sub_table["treatment"] == (self.session.config["treatment"] - 1)]
            sub_table = sub_table[sub_table["gender"] == self.in_round(1).gender]

            # SB filtering #
            filtered_table = sub_table[sub_table["point_score_1"] > my_score]
            filtered_table = filtered_table[filtered_table["point_score_1"] <= my_score + spread]
            disallowed_indexes.append(filtered_table.index.tolist())  # store options that cant be randomly chosen
            if self.session.config["treatment"] == 2:
                filtered_table = filtered_table[filtered_table["winning_1"] == 1]
            #print(f"This is sub_table SB -treatment -gender -point_interval -winning: {filtered_table}")
            if len(filtered_table.index.tolist()):  # at least one match in SB
                position_options["slightly_behind"] = filtered_table.index.tolist()
                self.sb_options = str(filtered_table.index.tolist())[1:-1]
                #print(f"{self.participant_label()} says: I found SB position")

            # SA filtering #
            filtered_table = sub_table[sub_table["point_score_1"] < my_score]
            filtered_table = filtered_table[filtered_table["point_score_1"] >= my_score - spread]
            disallowed_indexes.append(filtered_table.index.tolist())  # store options that cant be randomly chosen
            if self.session.config["treatment"] == 2:
                filtered_table = filtered_table[filtered_table["winning_1"] == 0]
            #print(f"This is sub_table SA -treatment -gender -point_interval -winning: {filtered_table}")

            if len(filtered_table.index.tolist()):  # at least one match in SA
                position_options["slightly_ahead"] = filtered_table.index.tolist()
                self.sa_options = str(filtered_table.index.tolist())[1:-1]
                #print(f"{self.participant_label()} says: I found SA position")

            if len(position_options["slightly_behind"]) > 0 and len(position_options["slightly_ahead"]) > 0:
                # Save results to player attributes
                self.score_position = str(random.sample(position_options.keys(), 1)[0])
                self.id_of_paired_player = str(random.sample(position_options[self.score_position], 1)[0])
                #print(f"{self.participant_label()} says: I found SB and SA position {self.id_of_paired_player}")

            else:
                #print(sub_table.to_string())
                pair_with_random_past_player(sub_table, position_options, disallowed_indexes)

        # Init basic data
        spread = int(self.session.config["pairing_filter_margin"])
        my_score = self.in_round(2).point_score

        # Main part of function
        sub_table = load_csv_data()
        find_score_position(sub_table)
        self.paired_player_round_1_points = sub_table.loc[int(self.id_of_paired_player)]["point_score_1"]
        self.paired_player_round_2_points = sub_table.loc[int(self.id_of_paired_player)]["point_score_2"]
        find_score_position_for_unmatched_players(my_score, spread)
        self.compare_players()
