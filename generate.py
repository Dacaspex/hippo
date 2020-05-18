import json
import random
from pydub import AudioSegment
import argparse


class TooStrictSegmentRulesException(Exception):
    pass


class Settings:
    def __init__(self, seed, duration, breath_pause_length):
        self.seed = seed
        self.duration = duration
        self.breath_pause_length = breath_pause_length


class Segment:
    def __init__(self, segment_id, text, text_appender_symbol, audio, weight, cool_down):
        self.id = segment_id
        self.text = text
        self.text_appender_symbol = text_appender_symbol
        self.audio = audio
        self.weight = weight
        self.cool_down = cool_down


class SegmentGenerator:
    def __init__(self, length):
        self.length = length

    def generate_breath_pause(self):
        return Segment('silent', '', '', AudioSegment.silent(self.length), 0, 0)


class Stats:
    def __init__(self):
        self.histogram = {}

    def record_segment(self, segment):
        if segment.id not in self.histogram:
            self.histogram[segment.id] = 0
        self.histogram[segment.id] += 1


class Task:
    def __init__(self, segments, settings, segment_generator):
        self.segments = segments
        self.settings = settings
        self.segment_generator = segment_generator
        self.MAX_ATTEMPTS = 128
        self.total_weight = 0
        self.result = Result()
        self.init()

    def init(self):
        random.seed(self.settings.seed)
        for segment in self.segments:
            self.total_weight += segment.weight

    def honours_cool_down(self, segment, relaxation):
        offset = segment.cool_down + relaxation
        if offset >= 0:
            return True
        last_added_segments = self.result.segments[-offset:]
        return segment not in last_added_segments

    def get_next_segment(self):
        attempts = 0
        while attempts < self.MAX_ATTEMPTS:
            threshold = random.randint(1, self.total_weight)
            segment = random.choice(self.segments)
            relaxation = int(attempts / 2)
            if segment.weight >= threshold and self.honours_cool_down(segment, relaxation):
                return segment
            else:
                attempts += 1
        raise TooStrictSegmentRulesException()

    def execute(self):
        while self.result.get_duration_in_seconds() < self.settings.duration:
            segment = self.get_next_segment()
            self.result.add_segment(segment)
            self.result.add_segment(self.segment_generator.generate_breath_pause(), record_stats=False)


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


def load_json(file_name):
    with open(file_name, 'r') as handle:
        raw = handle.read()
        return json.loads(raw)


def load_segments(task_file, audio_folder):
    segments = []
    segment_ids = []
    for segment in task_file["segments"]:
        # Make sure to generate a unique segment id for each segment
        base_segment_id = '_'.join(segment['text'].lower().split()) if 'id' not in segment else segment['id']
        segment_id = base_segment_id
        id_number = 1
        while segment_id in segment_ids:
            segment_id = base_segment_id + '_' + str(id_number)
            id_number += 1
        segment_ids.append(segment_id)

        audio = AudioSegment.from_mp3(audio_folder + '/' + segment['audio'])
        cool_down = 0 if 'cool_down' not in segment else segment['cool_down']
        text_appender_symbol = '. ' if 'text_appender_symbol' not in segment else segment['text_appender_symbol']
        segments.append(Segment(segment_id, segment['text'], text_appender_symbol, audio, segment['weight'], cool_down))
    return segments


def load_settings(task_file, arg_duration, arg_seed):
    settings = task_file['settings']
    if arg_seed is None and 'seed' not in settings:
        seed = None
    else:
        seed = int(arg_seed) if arg_seed is not None else settings['seed']

    if arg_duration is None and 'duration' not in settings:
        print('No duration specified, using the default of 30 seconds')
        duration = 30
    else:
        duration = int(arg_duration) if arg_duration is not None else settings['duration']

    breath_pause_length = settings['breath_pause_length']
    return Settings(seed, duration, breath_pause_length)


def load_task(task_file, audio_folder, arg_duration, arg_seed):
    segments = load_segments(task_file, audio_folder)
    settings = load_settings(task_file, arg_duration, arg_seed)
    segment_generator = SegmentGenerator(settings.breath_pause_length)
    return Task(segments, settings, segment_generator)


def run(args):
    task_file_path = args.task
    audio_folder = args.audio_base_directory
    output_name = args.output
    arg_duration = args.duration
    arg_seed = args.seed

    task = load_task(load_json(task_file_path), audio_folder, arg_duration, arg_seed)
    try:
        task.execute()
    except TooStrictSegmentRulesException as e:
        print('Could not execute task because some constraints were too strict. Perhaps lower some cool downs?')
        exit(-1)

    print(task.result.text)
    print(task.result.stats.histogram)
    task.result.audio.export(output_name + '.mp3')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Command line utility tool to generate controlled random speech audio and text samples',
        add_help=True
    )
    parser.add_argument(
        'task',
        help='Location of the task file'
    )
    parser.add_argument(
        'audio_base_directory',
        help='Path to the directory where the audio files are located'
    )
    parser.add_argument(
        '-o', '--output',
        help='The name of the created audio file',
        default='output'
    )
    parser.add_argument(
        '-d', '--duration',
        help='Sets (roughly) the duration of the created audio file in seconds. '
             'This overrides the value in the task file',
    )
    parser.add_argument(
        '-s', '--seed',
        help='Sets the seed for the psuedo-random number generator. This overrides the value in the task file'
    )

    run(parser.parse_args())
