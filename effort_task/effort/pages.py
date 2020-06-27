from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1


class Instructions(Page):
    def is_displayed(self):
        return self.round_number == 1


class TaskStage(Page):
    form_model = "player"
    form_fields = ["point_score"]

    def before_next_page(self):
        if self.round_number == 1:
            point_score_everyone = [p.point_score for p in self.get_players()].sort()




class Results(Page):
    form_model = "player"


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        pass


class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        pass




page_sequence = [Instructions, TaskStage, Results, FinalResults]


