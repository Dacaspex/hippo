import random
from time import time

from src.logger import Logger
from src.result import Result
from src.timestamp import Timestamp


class TooStrictSegmentRulesException(Exception):
    pass


class Task:
    def __init__(self, segments, settings, segment_generator):
        self.segments = segments
        self.settings = settings
        self.segment_generator = segment_generator
        self.logger = Logger()
        self.MAX_ATTEMPTS = 128  # TODO: Deduce from max cool down
        self.result = Result()
        self.init()

    def init(self):
        random.seed(self.settings.seed)

    def honours_cool_down(self, segment, cool_down, relaxation):
        offset = cool_down + relaxation
        if offset >= 0:
            return True
        last_added_segments = self.result.segments[-offset:]
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
        # If both options are YES, then the weight and cool down in the section has higher
        # priority. Therefore, we must compute the total weight now and save the selected
        # weight and cool down per segment (coming from 'always occurrence' or the section)
        candidates = []
        total_weight = 0
        for segment in self.segments:
            # Check whether there is a section that is currently active, i.e. the current timestamp
            # falls between the start and end of the section
            section = None
            for candidate_section in segment.sections:
                if current_timestamp.is_between(candidate_section.start, candidate_section.end):
                    section = candidate_section
                    break

            # If there is an active section, then we must use those weight and cool down values
            # else, we must use those values from the 'always occurrence' if that exists
            # if both do not exist, then we simply do not add the segment to the candidates
            if section is not None:
                candidates.append({'segment': segment, 'weight': section.weight, 'cool_down': section.cool_down})
                total_weight += section.weight
            elif segment.has_always_occurrence():
                # Fallback, if the section is None or if there is only an always occurrence component
                candidates.append({
                    'segment': segment,
                    'weight': segment.always_occurrence.weight,
                    'cool_down': segment.always_occurrence.cool_down
                })
                total_weight += segment.always_occurrence.weight

        # Now that we have a list of candidate segments, we must pick one according
        # to the approximate probability distribution defined by the weights
        attempts = 0
        while attempts < self.MAX_ATTEMPTS:
            # Get the random values
            threshold = random.randint(1, total_weight)
            candidate = random.choice(candidates)

            # Extract the values we packed earlier
            segment = candidate['segment']
            weight = candidate['weight']
            cool_down = candidate['cool_down']

            # To avoid a deadlock situation (i.e. no segment can be added because the cool downs
            # are too big), we reduce the cool down slightly after x attempts
            relaxation = int(attempts / 8)

            if weight >= threshold and self.honours_cool_down(segment, cool_down, relaxation):
                return segment
            else:
                attempts += 1
        # TODO: This can be avoided by computing the maximum cool down and adjust the
        #   max_attempts and relaxation accordingly
        raise TooStrictSegmentRulesException()

    def execute(self):
        start_time = time()
        while self.result.get_duration_in_seconds() < self.settings.duration:
            segment = self.get_next_segment()
            self.result.add_segment(segment)
            self.result.add_segment(self.segment_generator.generate_breath_pause(), record_stats=False)
            # TODO: Add last defined timestamps

            # Print progress to the console
            current_length = self.result.get_duration_in_seconds()
            total_length = self.settings.duration

            self.logger.print_progress(
                current_length,
                total_length,
                prefix='Progress',
                bar_length=32
            )
