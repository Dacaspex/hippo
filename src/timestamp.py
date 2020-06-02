from src.util import extract


class Timestamp:
    def __init__(self, seconds):
        self.seconds = seconds

    def is_before(self, other):
        """
        :param Timestamp other:
        :return: True if self is before other, False otherwise
        """
        return self.seconds <= other.seconds

    def is_between(self, left, right):
        """
        :param Timestamp left:
        :param Timestamp right:
        :return: True if left <= self <= right, False otherwise
        """
        return left.seconds <= self.seconds <= right.seconds

    @staticmethod
    def from_json(json, max_time):
        seconds = extract('seconds', json)
        if seconds is None:
            seconds = extract('percentage', json, 0) * max_time
        return Timestamp(seconds)
