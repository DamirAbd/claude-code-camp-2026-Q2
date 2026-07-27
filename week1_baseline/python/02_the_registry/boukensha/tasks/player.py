from .base import TaskBase


class Player(TaskBase):
    @classmethod
    def task_name(cls):
        return "player"
