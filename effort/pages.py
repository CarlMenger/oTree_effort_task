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


class GroupingWaitPage(WaitPage):
    wait_for_all_groups = True


class TaskStageWaitPage(WaitPage):
    wait_for_all_groups = True


class Results(Page):
    form_model = "player"

    def vars_for_template(self):
        return self.player.participant.label


class ResultsWaitPage(WaitPage):
    pass


class GenerateFiles(WaitPage):
    wait_for_all_groups = True  # this makes after_all_players_arrive look in subsession class
    after_all_players_arrive = "create_record_files"


class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    """def vars_for_template(self):
        return dict(create_score_records=self.subsession.get_records(),
                    create_payfile=self.subsession.get_payfile(),
                    )"""


page_sequence = [Instructions, InstructionsWaitPage, TaskStage,
                 TaskStageWaitPage, Results, GenerateFiles, FinalResults]
