from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Instructions1(Page):
    form_model = 'player'


class Preview(Page):
    form_model = 'player'


class BeforeQuestionnaires(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = "shuffle_quest_sequence"


class Questionnaires(Page):
    form_model = 'player'
    form_fields = ['tokens_quest1', 'tokens_quest2', 'tokens_quest3', 'tokens_quest4', ]

    def vars_for_template(self):
        return dict(tokens_quest1=self.player.tokens_quest1,
                    tokens_quest2=self.player.tokens_quest2,
                    tokens_quest3=self.player.tokens_quest3,
                    tokens_quest4=self.player.tokens_quest4,
                    tab_1=Constants.quests[f"quest{self.player.quest_sequence[0]}"],
                    tab_2=Constants.quests[f"quest{self.player.quest_sequence[1]}"],
                    tab_3=Constants.quests[f"quest{self.player.quest_sequence[2]}"],
                    tab_4=Constants.quests[f"quest{self.player.quest_sequence[3]}"],
                    )


class CalculatePayoffs(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = 'calculate_payments'


class Results(Page):
    form_model = 'player'

    def vars_for_template(self):
        return dict(payoff=self.player.payoff,
                    chosen_quest=self.player.chosen_quest)


page_sequence = [Instructions1, Preview, BeforeQuestionnaires, Questionnaires, CalculatePayoffs, Results]
