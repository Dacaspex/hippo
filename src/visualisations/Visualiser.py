import matplotlib.pyplot as plt
import numpy as np


class Visualiser:
    def __init__(self, result):
        self.result = result

    def show_visualisation(self):
        id_segment_map = {}
        for entry in self.result.segment_timestamp_map:
            segment = entry['segment']
            segment_list = id_segment_map.get(segment.id, [])
            segment_list.append(entry)
            id_segment_map[segment.id] = segment_list

        timestamp_data = []
        labels = []
        for segment_id, entries in id_segment_map.items():
            segment_timestamp_data = []
            for entry in entries:
                timestamp = entry['timestamp']
                segment_timestamp_data.append(timestamp)
            timestamp_data.append(segment_timestamp_data)
            labels.append(segment_id)

        plt.eventplot(timestamp_data, colors=np.random.rand(len(timestamp_data), 3))
        plt.legend(labels)
        plt.show()
