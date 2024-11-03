from config import *
import asyncio
import json
import os
import pygame
from dotenv import load_dotenv
load_dotenv()

pygame.init()
pygame.joystick.init()

from pythonosc import tcp_client
from go2_webrtc_driver.constants import *
from tools import *

def gen_command_payload(command_name):

    payload = {
        "parameter": "",
        "api_id": SPORT_CMD[command_name],
        "topic": RTC_TOPIC["SPORT_MOD"],
    }

    return json.dumps(payload)

def gen_movement_payload(x: float, y: float, z: float):
    x = round(x * JOY_SENSE, 2)
    y = round(y * JOY_SENSE, 2)

    payload = {
        "parameter": json.dumps({"x": x, "y": y, "z": z}),
        "api_id": SPORT_CMD["Move"],
        "topic": RTC_TOPIC["SPORT_MOD"],
    }

    return json.dumps(payload)

def handle_client_msg(client, topic, msg):
    if client is not None:
        try:
            client.send_message(topic, msg)
        except BrokenPipeError:
            client.close()
            raise SystemExit("Broken pipe. Disconnected")

async def get_joystick_values(joystick = None, joystick_nums = {}):
    # This is necessary to smooth things up
    pygame.event.pump()

    if joystick is not None:

        d = {}

        for axe in range(joystick_nums["axes"]):
            if axe not in AXES: continue
            d[AXES[axe]] = round(joystick.get_axis(axe), 1) * -1

        for button in range(joystick_nums["buttons"]):
            if button not in BUTTONS: continue
            d[BUTTONS[button]] = joystick.get_button(button)

        for hat in range(joystick_nums["buttons"]):
            if hat not in HATS: continue
            d[HATS[hat]] = joystick.get_hat(hat)

        for ball in range(joystick_nums["balls"]):
            if ball not in BALLS: continue
            d[BALLS[ball]] = joystick.get_ball(ball)

        return d

    return DEF_JOY

async def start_joy_bridge(client = None, joystick=None):

    # Get numbers at the beginning to avoid overhead
    joystick_nums = {
        'axes': joystick.get_numaxes(),
        'balls': joystick.get_numballs(),
        'buttons': joystick.get_numbuttons(),
        'hats': joystick.get_numhats()
    }

    # TODO Make this listen to topics?
    robot_stat = "BalanceStand"

    while True:
        joystick_values = await get_joystick_values(
            joystick=joystick, joystick_nums=joystick_nums)

        if DEBUG:
            std_out (f"Joystick values: {joystick_values}")

        robot_cmd = None

        # We are moving the axes
        if any([joystick_values[item] for item in joystick_values if 'Axis' in item]):
            if DEBUG:
                std_out ('Movement with axis!')

            if robot_stat == "BalanceStand":
                robot_cmd = gen_movement_payload(
                    x = joystick_values["Axis 1"],
                    y = joystick_values["Axis 0"],
                    z = joystick_values["Axis 2"]
                )

            if DEBUG:
                std_out (f'Robot command: {robot_cmd}')

            if robot_cmd is not None: handle_client_msg(client, MOVE_TOPIC, robot_cmd)

        # We are moving the hat
        # if any([joystick_values[item] for item in joystick_values if 'Hat' in item]):
        #     if DEBUG:
        #         std_out ('Movement with hat!')

            # robot_cmd = gen_movement_payload(
            #     x = joystick_values["Axis 1"],
            #     y = joystick_values["Axis 0"],
            #     z = joystick_values["Axis 2"]
            # )

            # if DEBUG:
            #     std_out ('Robot command ', robot_cmd)

            # if client is not None:
            #     client.send_message("/dog/move", robot_cmd)

        # We are pressing a button
        if any([joystick_values[item] for item in joystick_values if ('Axis' not in item and 'Hat' not in item)]):
            if DEBUG:
                std_out ('A button was pressed!')

            for item in joystick_values:
                if 'Axis' in item or 'Hat' in item: continue

                if joystick_values[item]:
                    if BUTTON_CMD[item] is not None:
                        robot_cmd = gen_command_payload(BUTTON_CMD[item])

                        # Check if we can change status
                        if BUTTON_CMD[item] == "BalanceStand":
                            robot_stat = "BalanceStand"
                            if DEBUG:
                                std_out (f'Robot status {robot_stat}')
                        if BUTTON_CMD[item] == "StandUp":
                            robot_stat = "StandUp"
                            if DEBUG:
                                std_out (f'Robot status {robot_stat}')

                        if DEBUG:
                            std_out (f'Robot command {robot_cmd}')

                        if robot_cmd is not None: handle_client_msg(client, CMD_TOPIC, robot_cmd)

        await asyncio.sleep(0.001)

async def main():
    coroutine = await start_joy_bridge(
        client = client,
        joystick = joystick)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(coroutine)
    # Quit pygame smoothly
    except KeyboardInterrupt:
        raise SystemExit()
        pass
    finally:
        pygame.joystick.quit()


if __name__ == '__main__':

    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    else:
        joystick = None

    client = None
    if not DRY_RUN:
        client = tcp_client.SimpleTCPClient(SERVER_IP, SERVER_PORT)

    asyncio.run(main())
