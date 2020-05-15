import json
import sys
import random
import os
from pydub import AudioSegment
import math


class Duration:
    def __init__(self, seconds, segments):
        self.seconds = seconds
        self.segments = segments


class Settings:
    def __init__(self, seed, duration, breath_pause_length):
        self.seed = seed
        self.duration = duration
        self.breath_pause_length = breath_pause_length


class Segment:
    def __init__(self, text, audio, weight, cool_down):
        self.text = text
        self.audio = audio
        self.weight = weight
        self.cool_down = cool_down


class Task:
    def __init__(self, segments, settings):
        self.segments = segments
        self.settings = settings
        self.breath_pause = AudioSegment.silent(settings.breath_pause_length)
        self.total_weight = 0
        self.init()

    def init(self):
        random.seed(self.settings.seed)
        for segment in self.segments:
            self.total_weight += segment.weight

    def get_random_segment(self):
        return random.choice(self.segments)

    def passed_max_duration(self, result):
        if len(result.segments) > self.settings.duration.segments:
            return True
        if result.get_duration_in_seconds() > self.settings.duration.seconds:
            return True
        return False


class Result:
    def __init__(self):
        self.text = None
        self.audio = None
        self.segments = []

    def add_segment(self, segment):
        self.segments.append(segment)
        if self.text is None:
            self.text = segment.text
        else:
            self.text += '. ' + segment.text
        if self.audio is None:
            self.audio = segment.audio
        else:
            self.audio += segment.audio

    def add_breath_pause(self, breath_pause):
        if self.audio is None:
            self.audio = breath_pause
        else:
            self.audio += breath_pause

    def get_duration_in_seconds(self):
        if self.audio is None:
            return 0
        else:
            return self.audio.duration_seconds


def load_json(file_name):
    with open(file_name, 'r') as handle:
        raw = handle.read()
        return json.loads(raw)


def load_segments(task_file, audio_folder):
    segments = []
    for segment in task_file["segments"]:
        audio = AudioSegment.from_mp3(audio_folder + '/' + segment['audio'])
        segments.append(Segment(segment['text'], audio, segment['weight'], segment['cool_down']))
    return segments


def load_settings(task_file):
    settings = task_file['settings']
    seed = settings['seed']
    duration_in_seconds = settings['duration']['seconds']
    duration_in_segments = settings['duration']['segments']
    duration = Duration(duration_in_seconds, duration_in_segments)
    breath_pause_length = settings['breath_pause_length']
    return Settings(seed, duration, breath_pause_length)


def load_task(task_file, audio_folder):
    segments = load_segments(task_file, audio_folder)
    settings = load_settings(task_file)
    return Task(segments, settings)


def get_percentage_done(result, settings):
    return max(
        len(result.segments) / settings.duration.segments,
        result.get_duration_in_seconds() / settings.duration.seconds
    )


def execute_task(task):
    result = Result()
    failed_attempts = 0
    report_at_next_percentage = 0
    report_interval = 0.1

    def honours_cool_down(_segment, _result, _relaxation):
        if _segment.cool_down == 0:
            return True
        last_items = _result.segments[-(_segment.cool_down + _relaxation):]
        return _segment not in last_items

    while not task.passed_max_duration(result):
        percentage_done = get_percentage_done(result, task.settings)
        if percentage_done >= report_at_next_percentage:
            print('Progress : ' + str(int(percentage_done * 100)))
            report_at_next_percentage += report_interval

        threshold = random.randint(1, task.total_weight)
        segment = task.get_random_segment()
        if segment.weight >= threshold and honours_cool_down(segment, result, math.floor(failed_attempts / 10)):
            failed_attempts = 0
            result.add_segment(segment)
            result.add_breath_pause(task.breath_pause)
        else:
            failed_attempts += 1
    print('Progress : 100')
    return result


if __name__ == '__main__':
    # Load arguments
    task_file_path = sys.argv[1]
    audio_folder = sys.argv[2]

    print('initialising...')
    task = load_task(load_json(task_file_path), audio_folder)
    print('generating...')
    result = execute_task(task)

    print(result.text)
    result.audio.export('export.mp3')
