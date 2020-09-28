from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Intro(Page):
    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        self.player.label = self.participant.label


class Questionnaire1(Page):
    form_model = "player"
    form_fields = ["gender",]

    def is_displayed(self):
        return self.round_number == 1

    #def before_next_page(self):
    #    print(self.request.POST.dict())


class Questionnaire2(Page):
    form_model = "player"
    form_fields = ["pc_name"]

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
    #    print(self.request.POST.dict())

    def vars_for_template(self):
        return dict(
            round=self.round_number)


class TaskStageWaitPageGrouping(WaitPage):
    def is_displayed(self):
        return self.round_number == 2
    wait_for_all_groups = True
    after_all_players_arrive = "group_players_after_trial_task"



class Instructions2(Page):
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return dict(winnin_reward=int(self.session.config["winning_bonus"]),
                    keystroke_combination_reward=self.session.config["conversion_rate"],
                    participation_reward=self.session.config["participation_fee"],
                    treatment=self.session.config["treatment"])


class Instructions2WaitPage(WaitPage):
    wait_for_all_groups = True


class Results(Page):
    form_model = "player"

    def is_displayed(self):
        return self.round_number > 1 and self.round_number != Constants.num_rounds

    def vars_for_template(self):
        return dict(point_score=self.player.point_score,
                    treatment=self.session.config["treatment"],
                    timeout_seconds=Constants.results_page_timeout_seconds,
                    )

    def get_timeout_seconds(self):
        return Constants.results_page_timeout_seconds


# Grouping players in between rounds
class ResultsWaitPage(WaitPage): # FIXME: Am i needed?
    def is_displayed(self):
        return self.round_number > 1 and self.round_number != Constants.num_rounds
        # FIXME: is this method firing in last round a problem?

    def get_timeout_seconds(self):
        return self.session.config["waitPageTimeout"]

    wait_for_all_groups = True
    #after_all_players_arrive = "group_players_after_trial_task"


class GenerateFiles(WaitPage):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    wait_for_all_groups = True  # this makes after_all_players_arrive look in subsession class
    after_all_players_arrive = "create_record_files"


class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):

        return dict(point_score_1=self.player.in_round(2).point_score,
                    point_score_2=self.player.in_round(3).point_score,
                    total_point_score=self.player.player_total_points)


page_sequence = [Intro,
                 Questionnaire1,
                 #Questionnaire2,
                 Instructions1,
                 Instructions1WaitPage,
                 TaskStage,
                 TaskStageWaitPageGrouping,
                 Instructions2,
                 Instructions2WaitPage,
                 Results,
                 ResultsWaitPage,
                 GenerateFiles,
                 FinalResults,
                 ]
