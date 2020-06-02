import random
from time import time

from src.logger import Logger
from src.result import Result
from src.timestamp import Timestamp


class Task:
    def __init__(self, segments, settings, segment_generator):
        self.segments = segments
        self.settings = settings
        self.breath_pause = segment_generator.generate_breath_pause()
        self.logger = Logger()
        self.result = Result()
        self.init()

    def init(self):
        random.seed(self.settings.seed)

    def honours_cool_down(self, segment, cool_down, relaxation):
        offset = -cool_down + relaxation
        if offset >= 0:
            return True
        last_added_segments = self.result.segments[offset:]
        return segment not in last_added_segments

    def get_next_segment(self):
        """
        > The meat of the program <
        This function is responsible for getting the next segment to append to the result. This
        is done as follows:
        - If there is a segment, which has a timestamp which is less than the current time?
          - YES: This must be the next segment for the result
          - NO: Continue
        - Prepare a list of candidate segments, i.e. those segments that either have an "always"
          defined, or those segments that have a section that the current timestamp falls into
        :return:
        """
        current_timestamp = Timestamp(self.result.get_duration_in_seconds())

        # First check if there is a segment with a timestamp that is less than the current
        # time. This must automatically become the next segment (if there are multiple,
        # subsequent calls to this method will retrieve each of them individually)
        for segment in self.segments:
            for timestamp in segment.timestamps:
                if timestamp.is_before(current_timestamp):
                    # We remove the timestamp to mark it as done and such it will not show
                    # up in subsequent calls to this method
                    segment.timestamps.remove(timestamp)
                    return segment

        # Get a list of candidate segments, i.e. those segments:
        # - That have an 'always occurrence' defined, i.e. they should always be included
        # - That have a section that the current timestamp falls into, i.e. they are
        #   momentarily active.
        # If both statements are true, the section options take precedence over the 'always occurrence'
        candidates = []
        for segment in self.segments:
            section = segment.get_section_by_timestamp(current_timestamp)
            if section is not None:
                candidates.append({'segment': segment, 'weight': section.weight, 'cool_down': section.cool_down})
            elif segment.has_always_occurrence():
                candidates.append({
                    'segment': segment,
                    'weight': segment.always_occurrence.weight,
                    'cool_down': segment.always_occurrence.cool_down
                })

        # Filter out segments that do not honour the cool down with relaxation
        filtered_candidates = []
        relaxation = -1
        while len(filtered_candidates) == 0:
            filtered_candidates = []
            relaxation += 1
            for entry in candidates:
                segment, cool_down = entry['segment'], entry['cool_down']
                if self.honours_cool_down(segment, cool_down, relaxation):
                    filtered_candidates.append(entry)

        # Generate distribution, according to their weight
        distribution = []
        for entry in filtered_candidates:
            segment, weight = entry['segment'], entry['weight']
            distribution.extend([segment for _ in range(weight)])

        # Finally, pick random value from list
        return random.choice(distribution)

    def finalise(self):
        start_time = time()
        total = len(self.result.parts)
        for index, part in enumerate(self.result.parts):
            self.result.audio += part
            elapsed_time = round(time() - start_time, 2)
            self.logger.print_progress(index + 1, total, suffix=f'Finalising ({elapsed_time}s)', bar_length=32)

    def execute(self):
        start_time = time()
        while self.result.get_duration_in_seconds() < self.settings.duration:
            segment = self.get_next_segment()
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
