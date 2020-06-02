from pydub import AudioSegment

from src.timestamp import Timestamp
from src.util import extract


class AlwaysOccurrence:
    def __init__(self, weight, cool_down):
        self.weight = weight
        self.cool_down = cool_down


class Section:
    def __init__(self, weight, cool_down, start, end):
        self.weight = weight
        self.cool_down = cool_down
        self.start = start
        self.end = end

    @staticmethod
    def from_json(json, max_time):
        weight = extract('weight', json, 1)
        cool_down = extract('cool_down', json, 0)
        start = Timestamp.from_json(json['start'], max_time)
        end = Timestamp.from_json(json['end'], max_time)
        return Section(weight, cool_down, start, end)


class Segment:
    def __init__(self, segment_id, text, text_appender_symbol, audio, always_occurrence, sections, timestamps):
        self.id = segment_id
        self.text = text
        self.text_appender_symbol = text_appender_symbol
        self.audio = audio
        self.always_occurrence = always_occurrence
        self.sections = sections
        self.timestamps = timestamps
        self.timestamps.sort(key=lambda t: t.seconds)

    def has_always_occurrence(self):
        return self.always_occurrence is not None

    def get_section_by_timestamp(self, timestamp):
        """
        :param Timestamp timestamp:
        :return: A section such that section.start <= timestamp section.end, else None
        """
        for section in self.sections:
            if timestamp.is_between(section.start, section.end):
                return section
        return None

    @staticmethod
    def from_json(json, audio_folder, max_time):
        segment_id = extract('id', json, json['text'])
        text = extract('text', json)
        text_appender_symbol = extract('text_appender_symbol', json, '. ')
        audio = AudioSegment.from_mp3(audio_folder + '/' + json['audio'])

        always_occurrence = None
        if 'always' in json:
            always_occurrence = AlwaysOccurrence(json['always']['weight'], json['always']['cool_down'])

        sections = []
        if 'sections' in json:
            for section in json['sections']:
                sections.append(Section.from_json(section, max_time))

        timestamps = []
        if 'timestamps' in json:
            for timestamp in json['timestamps']:
                timestamps.append(Timestamp.from_json(timestamp, max_time))

        return Segment(segment_id, text, text_appender_symbol, audio, always_occurrence, sections, timestamps)
