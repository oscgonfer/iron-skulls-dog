import asyncio
import json
import os

from command import *
from config import *
from tools import *

from go2_webrtc_driver.constants import *
from go2_webrtc_driver.webrtc_audiohub import WebRTCAudioHub
from aiortc.contrib.media import MediaPlayer

class Dog:
    def __init__(self, conn=None, dry_run=False, broadcast=False, mqtt_handler=None):
        # State
        self.state = {
            'LOW_STATE': None,
            'LF_SPORT_MOD_STATE': None,
            'MULTIPLE_STATE': None, 
            'WIRELESS': None
        }
        self._mode = None
        self._motion_switcher = None
        self.conn = conn
        self.lock = asyncio.Lock()
        self.dry_run = dry_run
        self.broadcast = broadcast
        self.mqtt_handler = mqtt_handler

        self.audio_list = None

    async def connect(self):
        await self.conn.connect()

        # Audio hub
        if not self.dry_run:
            self.audio_hub = WebRTCAudioHub(self.conn)
        
        return

    async def get_audio_list(self, reload = True):
        # From go2_webrtc_connect example
        if self.dry_run: return

        if reload:
            # Get the list of available audio files
            response = await self.audio_hub.get_audio_list()

            if response and isinstance(response, dict):
                data_str = response.get('data', {}).get('data', '{}')
                self.audio_list = json.loads(data_str).get('audio_list', [])
        
        return self.audio_list
    
    def get_audio_uuid(self, audio_file = None):
        if self.dry_run: return

        if audio_file is None:
            std_out(f'Need at least an audio file')
            return None

        filename = os.path.splitext(audio_file)[0]
        # Check if file already exists by CUSTOM_NAME and store UUID
        if self.audio_list is None:
            return None
        
        existing_audio = next((audio for audio in self.audio_list if audio['CUSTOM_NAME'] == filename), None)
        
        if existing_audio:
            uuid = existing_audio['UNIQUE_ID']
            std_out(f"Audio file {filename} found. UUID: {uuid}")
        else:
            uuid = None
        
        return uuid
    
    async def upload_audio_file(self, audio_file = None):
        if self.dry_run: return

        if audio_file is None:
            std_out(f'Need at least an audio file to upload')
            return None

        # Check if file already exists by CUSTOM_NAME and store UUID
        await self.get_audio_list(reload=True)
        uuid = self.get_audio_uuid(audio_file)
        
        if uuid is None:
            filename = os.path.splitext(audio_file)[0]
            std_out(f"Audio file {filename} not found, proceeding with upload")

            # TODO Fix
            audio_file_path = os.path.join(os.path.dirname(__file__), audio_file)
            if not os.path.exists(audio_file_path):
                std_out(f"{audio_file_path} does not exist")
                return None

            # Upload the audio file
            std_out("Starting audio file upload...")
            await self.audio_hub.upload_audio_file(audio_file_path)
            std_out("Audio file upload completed")

            await self.get_audio_list(reload=True)
            uuid = self.get_audio_uuid(audio_file)
            std_out(f"New audio file uuid: {uuid}")
        
        return uuid

    async def play_dog_audio(self, audio_file=None):

        if audio_file is None:
            std_out(f'Need at least an audio file to play')
            return None

        std_out(f'Playing dog audio: {audio_file}')
        if self.dry_run: return

        await self.get_audio_list(reload=True)
        # Check if file already exists by CUSTOM_NAME and store UUID
        uuid = self.get_audio_uuid(audio_file)
        if uuid is None:
            std_out("File not found. Upload it first!")
            return None
        
        await self.audio_hub.play_by_uuid(uuid)

    async def add_media_player_track(self, track_path = ''):
        std_out(f'Adding media player track: {track_path}')
        if track_path != '':
            player = MediaPlayer(track_path)
            audio_track = player.audio
            self.conn.pc.addTrack(audio_track)
        std_out('Done')

    async def play_local_audio(self, audio_file_path=''):
        if audio_file_path == '':
            std_out(f'Need at least a path to play')
            return None
                
        # TODO check file paths in absolute mode
        if os.path.exists(audio_file_path):
            std_out (f'Playing local audio file: {audio_file_path}')
            if self.dry_run: return
            await self.add_media_player_track(audio_file_path)
        else:
            std_out(f'File does not exist: {audio_file_path}')

    async def stream_audio_track(self, audio_file_path=''):
        if audio_file_path == '':
            std_out(f'Need at least a path to play')
            return None
        
        std_out (f'Playing stream audio track: {audio_file_path}')
        if self.dry_run: return
        
        await self.add_media_player_track(audio_file_path)

    async def send_audio_command(self, command):
        std_out(f"Audio command source: {command.source}")
        std_out(f"Audio command options: {command.options}")

        if command.source == 'dog_file':
            await self.play_dog_audio(command.options["audio_file"])
        elif command.source == 'client_file':
            await self.play_local_audio(command.options["audio_file"])
        elif command.source == 'stream_file':
            await self.stream_audio_track(command.options["audio_stream"])

    async def send_async_command(self, command):
        # Reply command, to acquire lock
        std_out(f"Command topic: {command.topic}")
        std_out(f"Command options: {command.options}")
        std_out(f"Command extras: {command.expect_reply, command.update_switcher_mode, command.additional_wait, command.post_hook}")

        std_out(f"Waiting for lock...")
        await self.lock.acquire()
        std_out("Lock acquired")

        if self.dry_run:
            std_out(f"Sleeping 3s...")
            await asyncio.sleep(3)
        else:
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                topic = command.topic, options = command.options)

            std_out(f"Command Response: {response}")

            if command.expect_reply:
                std_out('Command expects reply')
                if response['data']['header']['status']['code'] == 0:
                    data = json.loads(response['data']['data'])
                    if command.update_switcher_mode:
                        self._motion_switcher = data['name']
                    await self.publish_response(command.topic, response=data)
                else:
                    data = json.dumps({"ERROR": response['data']})
                    await self.publish_response(command.topic, response=data)

        if command.additional_wait:
            std_out('Waiting additional timer')
            await asyncio.sleep(command.additional_wait)

        self.lock.release()

        if command.post_hook:
            std_out('Sending command post_hook')
            cmd = Command(command.post_hook)
            await self.send_async_command(cmd)
        
        std_out('Done')

    def send_command(self, command):
        # No reply command
        std_out('Got command', priority=True)
        std_out(f"Command topic: {command.topic}")
        std_out(f"Command options: {command.options}")

        if not self.dry_run:
            asyncio.gather(self.conn.datachannel.pub_sub.publish_request_new(
                command.topic, command.options))

    async def publish_response(self, channel, response):
        if self.broadcast:
            await self.mqtt_handler.publish(topic=f'{RESPONSE_TOPIC}/{channel}', \
                payload=json.dumps(response))

    async def publish_state(self, channel):
        if self.broadcast:
            await self.mqtt_handler.publish(topic=f'{STATE_TOPIC}/{channel}', \
                payload=json.dumps(self.state))
        
            await self.publish_motion_switcher_mode()
    
    async def publish_motion_switcher_mode(self):
        if self.broadcast:
            await self.mqtt_handler.publish(topic=f'{MODE_TOPIC}/mode', \
                payload=json.dumps(self.motion_switcher))

    def lowstate_callback(self, message):
        current_message = message['data']
        self.state['LOW_STATE'] = current_message
        asyncio.gather(self.publish_state('LOW_STATE'))

    def multiplestate_callback(self, message):
        # TODO For whatever reason this needs to be parsed into json
        current_message = json.loads(message['data'])
        self.state['MULTIPLE_STATE'] = current_message
        asyncio.gather(self.publish_state('MULTIPLE_STATE'))

    def sportstate_callback(self, message):
        current_message = message['data']
        # Update state
        self.state['LF_SPORT_MOD_STATE'] = current_message
        # Update mode (DogState)
        self._mode = self.state['LF_SPORT_MOD_STATE']['mode']
        # Eager find motion switcher (DogMode)
        for st in CMD_STATES:
            if self._mode in CMD_STATES[st]:
                self._motion_switcher = st
        # Current 
        asyncio.gather(self.publish_state('LF_SPORT_MOD_STATE'))

    def wireless_callback(self, message):
        print (message)

    @property
    def mode(self):
        return self._mode

    @property
    def dog_state(self):
        return DogState(self.mode)

    @property
    def motion_switcher(self):
        return self._motion_switcher

