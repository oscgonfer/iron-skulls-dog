# Iron Skulls Dog

Development files for a robot dog controller via MQTT server that listens to commands or joysticks. Completely experimental.

## Installation

```
sudo apt install portaudio19-dev x86_64-linux-gnu-gcc build-essential libssl-dev libffi-dev python3-dev mosquitto
```

```
git clone git@github.com:oscgonfer/iron-skulls-dog.git
git clone --recurse-submodules git@github.com:legion1581/go2_webrtc_connect.git
cd go2_webrtc_connect
pip install -e .
cd ../iron-skulls-dog
<!-- Create a virtual environment if you want -->
pip install -r requirements.txt
```

## Running

Check in config.py the necessary parameters (`DEBUG` and the different ports, server IPs).

Create:
- `.pass`: Unitree account password
- `.sn`: Unitree GO2 Serial Number

Turn on the dog and configure the mode. Choose this mode in `main.py`.

Run `get-token.sh` with your email as a parameter to get the connection token and dog IP in the local network:

```
./get-token.sh -e email@email.com
```

Run mosquitto

```
mosquitto
```

Run main.py

```
python main.py --broadcast
```

Run clients, for instance, joystick:

```
python joystick_bridge.py
```