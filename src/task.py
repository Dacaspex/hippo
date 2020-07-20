import random
from time import time

from src.SegmentSelector import SegmentSelector
from src.logger import Logger
from src.result import Result


class Task:
    def __init__(self, segments, settings, segment_generator, effects):
        self.segments = segments
        self.settings = settings
        self.breath_pause = segment_generator.generate_breath_pause()
        self.effects = effects
        self.segment_selector = SegmentSelector(segments)
        self.logger = Logger()
        self.result = Result()
        self.init()

    def init(self):
        random.seed(self.settings.seed)

    def preview(self):
        for segment in self.segments:
            self.result.add_segment(segment)
            self.result.add_segment(self.breath_pause, is_silence=True, record_stats=False)
        self.finalise()

    def finalise(self):
        start_time = time()
        total = len(self.result.parts) + len(self.effects)
        progress = 1
        for part in self.result.parts:
            self.result.audio += part
            elapsed_time = round(time() - start_time, 2)
            self.logger.print_progress(progress, total, suffix=f'Finalising ({elapsed_time}s)', bar_length=32)
            progress += 1
        for effect in self.effects:
            effect.post_finalise(self.result)
            elapsed_time = round(time() - start_time, 2)
            self.logger.print_progress(progress, total, suffix=f'Finalising ({elapsed_time}s)', bar_length=32)
            progress += 1

    def execute(self):
        start_time = time()
        while self.result.get_duration_in_seconds() < self.settings.duration:
            segment = self.segment_selector.get_segment(self.result)
            self.result.add_segment(segment)
            self.result.add_segment(self.breath_pause, is_silence=True, record_stats=False)

            # Calculate current progress
            length = self.result.get_duration_in_seconds()
            total = self.settings.duration
            elapsed_time = round(time() - start_time, 2)

            self.logger.print_progress(length, total, suffix=f'Creating sample ({elapsed_time}s)', bar_length=32)

        # Add the remaining segments that still have a timestamp
        for segment in self.segments:
            if len(segment.timestamps) > 0:
                self.result.add_segment(segment)
                self.result.add_segment(self.breath_pause, is_silence=True, record_stats=False)

        elapsed_time = round(time() - start_time, 2)
        self.logger.print_progress(1, 1, suffix=f'Done ({elapsed_time}s)', bar_length=32)

        self.finalise()
