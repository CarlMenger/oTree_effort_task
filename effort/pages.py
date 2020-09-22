from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Intro(Page):
    def is_displayed(self):
        return self.round_number == 1


class Questionnaire1(Page):
    form_model = "player"
    form_fields = ["gender", "room_name", ]

    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        print(self.request.POST.dict())


class Questionnaire2(Page):
    form_model = "player"
    form_fields = ["pc_name"]

    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        print(self.request.POST.dict())


class Instructions1(Page):
    def is_displayed(self):
        return self.round_number == 1


class Instructions1WaitPage(WaitPage):
    wait_for_all_groups = True

    def is_displayed(self):
        return self.round_number == 1


class TaskStage(Page):
    form_model = "player"
    form_fields = ["point_score"]
    #wait_for_all_groups = True

    def get_timeout_seconds(self):
        return self.player.task_stage_timeout_seconds

    def before_next_page(self):
        print(self.request.POST.dict())


class TaskStageWaitPageGrouping(WaitPage):
    def is_displayed(self):
        return self.round_number == 1
    wait_for_all_groups = True
    after_all_players_arrive = "group_players"


class Instructions2(Page):
    def is_displayed(self):
        return self.round_number == 2

    def vars_for_template(self):
        return dict(winnin_reward=int(self.session.config["winning_bonus"]),
                    keystroke_combination_reward=self.session.config["conversion_rate"],
                    participation_reward=self.session.config["participation_fee"],
                    treatment=self.session.config["treatment"])


class Results(Page):
    form_model = "player"

    def vars_for_template(self):
        return dict(point_score=self.player.point_score,
                    treatment=self.session.config["treatment"]
                    )

    def get_timeout_seconds(self):
        return self.session.config["resultsPage_timeout"]


# Grouping players in between rounds
class ResultsWaitPageAndGrouping(WaitPage):
    def is_displayed(self):
        return self.round_number > 1 and self.round_number != Constants.num_rounds
        # FIXME: is this method firing in last round a problem?

    def get_timeout_seconds(self):
        return self.session.config["waitPageTimeout"]

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


page_sequence = [Intro,
                 Questionnaire1,
                 Questionnaire2,
                 Instructions1,
                 Instructions1WaitPage,
                 TaskStage,
                 TaskStageWaitPageGrouping,
                 Instructions2,
                 Results,
                 ResultsWaitPageAndGrouping,
                 GenerateFiles,
                 FinalResults,
                 ]
