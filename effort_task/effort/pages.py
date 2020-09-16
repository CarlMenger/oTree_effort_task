from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1


class Instructions1(Page):
    def is_displayed(self):
        return self.round_number == 1


class Instructions2(Page):
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return dict(winnin_reward=self.session.config["winning_bonus"],
                    keystroke_combination_reward=self.session.config["conversion_rate"],
                    participation_reward=self.session.config["participation_fee"])

class Questionnaire1(Page):
    form_model = "player"
    form_fields = ["gender", "room_name",]

    def is_displayed(self):
        return self.round_number == 1

class Questionnaire2(Page):
    form_model = "player"
    form_fields = ["pc_name"]

    def is_displayed(self):
        return self.round_number == 1



class InstructionsWaitPage(WaitPage):
    wait_for_all_groups = True
    def is_displayed(self):
        return self.round_number == 1


class TaskStage(Page):
    form_model = "player"
    form_fields = ["point_score"]

    def get_timeout_seconds(self):
        return self.player.task_stage_timeout_seconds


class TaskStageWaitPage(WaitPage):
    pass


class Results(Page):
    form_model = "player"

    def vars_for_template(self):
        return self.player.participant.label


# Grouping players in between rounds
class ResultsWaitPageAndGrouping(WaitPage):
    def is_displayed(self):
        return self.round_number > 1 and self.round_number != Constants.num_rounds
        # FIXME: is this method firing in last round a problem?
    wait_for_all_groups = True
    after_all_players_arrive = "group_players"


class GenerateFiles(WaitPage):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds
    wait_for_all_groups = True  # this makes after_all_players_arrive look in subsession class
    after_all_players_arrive = "create_record_files"


class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    """def vars_for_template(self):
        return dict(create_score_records=self.subsession.get_records(),
                    create_payfile=self.subsession.get_payfile(),
                    )"""


page_sequence = [Introduction, Questionnaire1, Questionnaire2, Instructions1,
                 InstructionsWaitPage, TaskStage, Instructions2,
                 TaskStageWaitPage, Results, ResultsWaitPageAndGrouping, GenerateFiles,
                 FinalResults]
