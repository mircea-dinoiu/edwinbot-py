# Project imports
from manager.Bot import Bot
from configs import *


def animate():
    Bot(
        name=db.get_config('bot.name'),
        password=db.get_config('bot.password'),
        pm=db.get_config('pm.enable'),
        db=db
    )