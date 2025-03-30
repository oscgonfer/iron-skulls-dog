from config import *
from tools import *
import json
import vlc
import time

# start_at is the time when we want the song to start in ms
# end_at is the time when we want the song to end in ms

class Track():
    def __init__(self, path:str = None, start_at = None, end_at = None):
        self.path = path
        self.start_at = start_at # In ms
        self.end_at = end_at # In ms
        # self.loop = loop
        self.media = None
        
        if self.path is not None:
            try:
                self.media_player = vlc.MediaPlayer()
                self.media = vlc.Media(self.path)
                self.media_player.set_media(self.media)

                # We need to play a bit to be able to get the length
                # 0.05 seems to be a good trade-off
                self.media_player.play()
                time.sleep(0.05)
                self._duration = self.media_player.get_length() # In ms
                self.media_player.stop()
            except:
                pass

            # if self.loop:
            #     self.media.add_option('--loop')
        else:
            return None
        
        if self.media is None:
            return None

    @property
    def duration(self):
        # Duration in ms
        return self._duration

    def play(self):
        if self.path is None: return

        if self.end_at is not None and self.end_at < self.duration and self.end_at > self.start_at:
            self.media.add_option(f'stop-time={self.end_at/1000}')
        
        self.media_player.play()
        
        if self.start_at is not None and self.start_at < self.duration:
            self.media_player.set_time(self.start_at)

    def stop(self):
        if self.path is None: return
        self.media_player.stop()

    def as_dict(self):

        return {
            'path': self.path,
            'duration': self.duration,
            'start_at': self.start_at if self.start_at is not None else 0,
            'end_at': self.end_at if self.end_at is not None else self.duration,
            'loop': self.loop
        }
    
    def to_json(self):
        return json.dumps(self.as_dict())