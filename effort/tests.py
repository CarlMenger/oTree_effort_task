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
            yield pages.Questionnaire1, dict(gender=str(*random.sample([0, 1],1)),
                                             #room_name=str(*random.sample([203, 205], 1))
                                             ),
            """if self.player.room_name == 205:
                yield pages.Questionnaire2, dict(
                    pc_name=random.sample(Constants.pc_name_list_205, 1)[0][0]
                                 )
            else:
                yield pages.Questionnaire2, dict(
                    pc_name=random.sample(Constants.pc_name_list_203, 1)[0][0]
                )"""
            yield pages.Instructions1
        yield Submission(pages.TaskStage, dict(point_score=str(int(numpy.random.normal(100, 20)))), check_html=False)

        if self.round_number == 1:
            yield pages.Instructions2
        if self.round_number > 1 and self.round_number != Constants.num_rounds:
            yield Submission(pages.Results,  check_html=False)


