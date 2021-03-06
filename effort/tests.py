from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants
from otree.api import Submission
import random
import numpy


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            yield pages.Intro
            yield pages.Questionnaire1, dict(gender=str(*random.sample([0, 1], 1)),
                                             hroot_id="I am a bot, Beep boop."),
            yield pages.Instructions1
        yield Submission(pages.TaskStage,
                         dict(point_score=str(int(numpy.random.normal(100, 15)))),
                         check_html=False)

        if self.round_number == 1:
            yield pages.Instructions2
        if self.round_number > 1 and self.round_number != Constants.num_rounds:
            yield Submission(pages.Results,  check_html=False)


