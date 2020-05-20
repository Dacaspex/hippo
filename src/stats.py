class Stats:
    def __init__(self):
        self.histogram = {}

    def record_segment(self, segment):
        if segment.id not in self.histogram:
            self.histogram[segment.id] = 0
        self.histogram[segment.id] += 1
