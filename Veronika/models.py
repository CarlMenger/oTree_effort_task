from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random
import re
doc = '""\n'


class Constants(BaseConstants):
    name_in_url = 'Veronika'
    players_per_group = None
    num_rounds = 1
    refund_quest1 = 48
    refund_quest2 = 24
    refund_quest3 = 24
    refund_quest4 = 48
    token_reward_quest1 = 6
    token_reward_quest2 = 6
    token_reward_quest3 = 8
    token_reward_quest4 = 8
    starting_funds = 80
    token_price_quest_all = 4
    quests = {"quest1": f"text_quest1{refund_quest1}",
              "quest2": "text_quest2",
              "quest3": "text_quest3",
              "quest4": "text_quest4",
              }


class Subsession(BaseSubsession):
    def shuffle_quest_sequence(self):
        [player.shuffle_my_quest_sequence() for player in self.get_players()]

    def calculate_payments(self):
        [player.calculate_my_payment() for player in self.get_players()]


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    gender = models.StringField(choices=[['Male', 'Male'], ['Female', 'Female']], label='What is your gender',
                                widget=widgets.RadioSelect)
    tokens_quest1 = models.IntegerField(label='Kolik žetonu chcete koupit?', max=20, min=0)
    tokens_quest2 = models.IntegerField(label='Kolik žetonu chcete koupit?', max=20, min=0)
    tokens_quest3 = models.IntegerField(label='Kolik žetonu chcete koupit?', max=20, min=0)
    tokens_quest4 = models.IntegerField(label='Kolik žetonu chcete koupit?', max=20, min=0)
    #payment = models.IntegerField(initial=0)
    chosen_quest = models.IntegerField()
    win = models.IntegerField()
    quest_sequence = models.StringField()

    def shuffle_my_quest_sequence(self):
        my_sequence = [1, 2, 3, 4]
        random.shuffle(my_sequence)
        self.quest_sequence = re.sub(r'[^\w]', '', str(my_sequence))
        print(self.quest_sequence)

    def calculate_my_payment(self):
        self.chosen_quest = random.randint(1, 4)
        q_vars = self.get_quest_vars()
        win = int(random.random())
        self.win = win
        """self.payment = Constants.starting_funds + (q_vars["Amount_of_tokens"] * (
                    q_vars["Reward_per_token"] * win - Constants.token_price_quest_all)) + ((win - 1) ** 2) * q_vars[
                           "Refund"]"""
        self.payoff = Constants.starting_funds + (q_vars["Amount_of_tokens"] * (
                    q_vars["Reward_per_token"] * win - Constants.token_price_quest_all)) + ((win - 1) ** 2) * q_vars[
                           "Refund"]

    def get_quest_vars(self):
        # return number of tokens(tokens_questx), reward for tokens (token_rewardx), cost of tokens (refund_tokenx)
        quest = self.chosen_quest
        if quest == 1:
            return {"Amount_of_tokens": self.tokens_quest1,
                    "Reward_per_token": Constants.token_reward_quest1,
                    "Refund": Constants.refund_quest1}
        elif quest == 2:
            return {"Amount_of_tokens": self.tokens_quest2,
                    "Reward_per_token": Constants.token_reward_quest2,
                    "Refund": Constants.refund_quest2}
        elif quest == 3:
            return {"Amount_of_tokens": self.tokens_quest3,
                    "Reward_per_token": Constants.token_reward_quest3,
                    "Refund": Constants.refund_quest3}
        elif quest == 4:
            return {"Amount_of_tokens": self.tokens_quest4,
                    "Reward_per_token": Constants.token_reward_quest4,
                    "Refund": Constants.refund_quest4}
