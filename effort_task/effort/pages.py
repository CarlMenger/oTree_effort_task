from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1


class Instructions(Page):
    def is_displayed(self):
        return self.round_number == 1


class InstructionsWaitPage(WaitPage):
    wait_for_all_groups = True


class TaskStage(Page):
    form_model = "player"
    form_fields = ["point_score"]

    # timeout_seconds = 35 #FIXME: no hardcoding

    def get_timeout_seconds(self):
        return self.player.task_stage_timeout_seconds

    # def before_next_page(self):
    #    scores_all = self.subsession.point_score_everyone() #FIXME: Useless


class GroupingWaitPage(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = "group_based_on_score"


class TaskStageWaitPage(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = "group_based_on_score"


class Results(Page):
    form_model = "player"

    def vars_for_template(self):
        score_position = self.player.get_score_position()
        print(score_position)
        return dict(score_position=score_position)

class ResultsWaitPage(WaitPage):
    pass


class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        pass


page_sequence = [Instructions, InstructionsWaitPage, TaskStage,
                 TaskStageWaitPage, Results, FinalResults]
