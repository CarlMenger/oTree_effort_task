from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class TestDB(WaitPage):
    def is_displayed(self):
        return self.round_number == 1

    wait_for_all_groups = True
    after_all_players_arrive = "test_db"


class Intro(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.player.label = self.participant.label


class Questionnaire1(Page):
    form_model = "player"
    form_fields = ["gender", ]

    def is_displayed(self):
        return self.round_number == 1

    #def before_next_page(self):
    #    print(self.request.POST.dict())


class Instructions1(Page):
    def is_displayed(self):
        return self.round_number == 1


class Instructions1WaitPage(WaitPage):
    wait_for_all_groups = True

    def is_displayed(self):
        return self.round_number == 1


class TaskStage(Page):
    form_model = "player"
    form_fields = ["point_score", "overall_keystroke_count"]
    wait_for_all_players = True

    def get_timeout_seconds(self):
        return Constants.task_stage_timeout_seconds

    #def before_next_page(self):
     #   self.subsession.after_task_stage()

    def vars_for_template(self):
        return dict(
            round=self.round_number)


class AfterTaskStage(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = "after_task_stage"


class PairPlayersWaitPage(WaitPage):
    def is_displayed(self):
        return self.round_number == 2
    wait_for_all_groups = True
    after_all_players_arrive = "pair_players"


class Instructions2(Page):
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return dict(winning_reward=int(self.session.config["winning_bonus"]),
                    treatment=self.session.config["treatment"])


class Instructions2WaitPage(WaitPage):
    def is_displayed(self):
        return self.round_number == 1
    wait_for_all_groups = True


class Results(Page):
    form_model = "player"

    def is_displayed(self):
        return self.round_number > 1 and self.round_number != Constants.num_rounds

    def vars_for_template(self):
        return dict(point_score=self.player.in_round(self.round_number).point_score,
                    treatment=self.session.config["treatment"],
                    timeout_seconds=Constants.results_page_timeout_seconds,
                    score_position=Constants.all_score_positions[self.player.score_position],)

    def get_timeout_seconds(self):
        return Constants.results_page_timeout_seconds


class ResultsWaitPage(WaitPage):  # FIXME: Am i needed?
    def is_displayed(self):
        return self.round_number > 1 and self.round_number != Constants.num_rounds

    def get_timeout_seconds(self):
        return self.session.config["waitPageTimeout"]

    wait_for_all_groups = True


class GenerateFiles(WaitPage):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    wait_for_all_groups = True  # this makes after_all_players_arrive look in subsession class
    after_all_players_arrive = "create_record_files"


class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):

        return dict(point_score_1=self.player.in_round(2).point_score_1,
                    point_score_2=self.player.in_round(3).point_score_2,
                    total_points=self.player.total_points,
                    )


page_sequence = [
    Intro,
    Questionnaire1,
    #TestDB,
    Instructions1,
    Instructions1WaitPage,
    TaskStage,
    AfterTaskStage,
    PairPlayersWaitPage,
    Instructions2,
    Instructions2WaitPage,
    Results,
    #ResultsWaitPage,
    GenerateFiles,
    FinalResults,

]
