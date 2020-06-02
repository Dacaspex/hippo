import json

import argparse

from pydub import AudioSegment

from src.segment import Segment
from src.settings import Settings
from src.task import Task


class SegmentGenerator:
    def __init__(self, length):
        self.length = length

    def generate_breath_pause(self):
        return Segment('silent', '', '', AudioSegment.silent(self.length), None, [], [])


def load_json(file_name):
    with open(file_name, 'r') as handle:
        raw = handle.read()
        return json.loads(raw)


def load_segments(task_file, audio_folder, max_time):
    segments = []
    for segment_json in task_file["segments"]:
        segments.append(Segment.from_json(segment_json, audio_folder, max_time))
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
    settings = load_settings(task_file, arg_duration, arg_seed)
    segments = load_segments(task_file, audio_folder, settings.duration)
    segment_generator = SegmentGenerator(settings.breath_pause_length)
    return Task(segments, settings, segment_generator)


def run(args):
    task_file_path = args.task
    audio_folder = args.audio_base_directory
    output_name = args.output
    arg_duration = args.duration
    arg_seed = args.seed

    print('Initialising...')
    task = load_task(load_json(task_file_path), audio_folder, arg_duration, arg_seed)
    print('Initialised')
    task.execute()

    print()
    print(task.result.text_string)
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
