from pydub import AudioSegment

from src.stats import Stats


class Result:
    def __init__(self):
        self.text = ''
        self.audio = AudioSegment.silent(1)
        self.segments = []
        self.stats = Stats()

    def add_segment(self, segment, record_stats=True):
        self.segments.append(segment)
        self.text += segment.text if self.text == '' else segment.text_appender_symbol + segment.text
        self.audio += segment.audio
        if record_stats:
            self.stats.record_segment(segment)

    def get_duration_in_seconds(self):
        return self.audio.duration_seconds
