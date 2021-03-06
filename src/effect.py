from pydub import AudioSegment

from src.util import extract


class Effect:
    def post_finalise(self, result):
        pass


class OverlayEffect(Effect):
    def __init__(self, overlay, gain) -> None:
        """
        :param AudioSegment overlay:
        :param in gain:
        """
        super().__init__()
        self.overlay = overlay
        self.gain = gain

    def post_finalise(self, result) -> None:
        """
        :param Result result:
        """
        self.overlay = self.overlay.apply_gain(self.gain)
        result.audio = result.audio.overlay(self.overlay, position=0, loop=True)

    @staticmethod
    def from_json(json, audio_folder):
        audio = AudioSegment.from_mp3(audio_folder + '/' + json['audio'])
        gain = extract('gain', json, 0)
        return OverlayEffect(audio, gain)


class PostVolumeGainEffect(Effect):
    def __init__(self, gain) -> None:
        """
        :param int gain:
        """
        super().__init__()
        self.gain = gain

    def post_finalise(self, result):
        result.audio = result.audio.apply_gain(self.gain)
        pass

    @staticmethod
    def from_json(json):
        gain = extract('gain', json, 0)
        return PostVolumeGainEffect(gain)
