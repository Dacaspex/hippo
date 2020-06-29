import random

from src.timestamp import Timestamp


class SegmentSelector:
    def __init__(self, segments):
        self.segments = segments

    def get_segment(self, result):
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
        current_timestamp = Timestamp(result.get_duration_in_seconds())

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
                if self.honours_cool_down(segment, cool_down, relaxation, result):
                    filtered_candidates.append(entry)

        # Generate distribution, according to their weight
        distribution = []
        for entry in filtered_candidates:
            segment, weight = entry['segment'], entry['weight']
            distribution.extend([segment for _ in range(weight)])

        # Finally, pick random value from list
        return random.choice(distribution)

    @staticmethod
    def honours_cool_down(segment, cool_down, relaxation, result):
        offset = -cool_down + relaxation
        if offset >= 0:
            return True
        last_added_segments = result.segments[offset:]
        return segment not in last_added_segments
