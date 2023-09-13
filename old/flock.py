import logging

from autogpt.singleton import Singleton

from .dolly import Dolly

logger = logging.getLogger(__name__)


class Flock(metaclass=Singleton):
    def __init__(self, max_size: int = 0):
        self._max_size: int = max_size
        self._members: list[Dolly] = []

    @property
    def max_size(self):
        return self._max_size

    @max_size.setter
    def max_size(self, max_size: int):
        if self._max_size == 0:
            self._max_size = max_size
        elif self._max_size != max_size:
            raise ValueError("Max size cannot be changed.")

    @property
    def size(self):
        return len(self._members)

    def add_member(self, member: Dolly):
        if member.index is not None:
            raise ValueError("Member already in a flock.")

        if self.size == self.max_size:
            raise ValueError("Max flock size reached.")

        member.index = self.size
        self._members.append(member)

    def disperse(self):
        pids = []
        for member in self._members:
            if not member.dispersed:
                try:
                    pid = member.disperse()
                    pids.append(pid)
                except:
                    logger.exception(f"Failed to deploy {member.name}")
        return pids
