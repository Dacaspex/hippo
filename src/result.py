from pydub import AudioSegment

from src.stats import Stats


class Result:
    def __init__(self):
        self.text = ''
        self.segments = []
        self.stats = Stats()
        self.audio = AudioSegment.empty()
        self.length_threshold = 10 * 60
        self.parts = [AudioSegment.empty()]

    def add_segment(self, segment, is_silence=False, record_stats=True):
        if not is_silence:
            self.segments.append(segment)
            self.text += segment.text if self.text == '' else segment.text_appender_symbol + segment.text
        self.parts[-1] += segment.audio
        # Appending more and more segments to the current audio segment becomes slow over time.
        # Therefore, we split up the current result in parts and add new segments to the last
        # part. At the threshold, we split the part up and create a new one. This massively
        # speeds up the program
        if self.parts[-1].duration_seconds >= self.length_threshold:
            self.parts.append(AudioSegment.empty())
        if record_stats:
            self.stats.record_segment(segment)

    def get_duration_in_seconds(self):
        return self.parts[-1].duration_seconds + (len(self.parts) - 1) * self.length_threshold
