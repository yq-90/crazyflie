# This example contains single drone motion commander
import logging
import time
from threading import Event

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper

from cflib.crazyflie.log import LogConfig
from cflib.positioning.motion_commander import MotionCommander

uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

deck_attached = Event()

def check_deck_attached_cb(name, value):
    v = int(value)
    # Check if the corresponding deck is attached
    if v:
        deck_attached.set()
    else:
        raise ValueError

def check_deck_attached_async(scf, deckstr):
    scf.cf.param.add_update_callback(group='deck', name=deckstr,
            cb=check_deck_attached_cb)

def takeoff_simple(scf, height=0.5):
    # mc has 6 basic commands: up, down, forward, back, turn_left, turn_right
    with MotionCommander(scf, default_height=height) as mc:
        time.sleep(5)
        mc.up(0.3)
        mc.forward(1)
        time.sleep(5)
        mc.turn_right(90)
        mc.forward(0.3)
        time.sleep(5)
        mc.down(0.3)
        time.sleep(5)
        mc.stop()


def logging_cb(timestamp, data, logconf):
    print(f'{timestamp} {logconf.name}: {data}')

if __name__ == '__main__':
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
    lg_stab.add_variable('stabilizer.roll', 'float')
    lg_stab.add_variable('stabilizer.pitch', 'float')
    lg_stab.add_variable('stabilizer.yaw', 'float')

    lg_est = LogConfig(name='Position', period_in_ms=10)
    lg_est.add_variable('stateEstimate.x', 'float')
    lg_est.add_variable('stateEstimate.y', 'float')
    lg_est.add_variable('stateEstimate.z', 'float')

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:

        check_deck_attached_async(scf, 'bcFlow2')

        if not deck_attached.wait(timeout=5):
            print('No flow deck detected')
            raise ValueError

        scf.cf.log.add_config(lg_stab)
        scf.cf.log.add_config(lg_est)
        lg_stab.data_received_cb.add_callback(logging_cb)
        lg_est.data_received_cb.add_callback(logging_cb)

        lg_stab.start()
        lg_est.start()

        takeoff_simple(scf)

        lg_stab.stop()
        lg_est.stop()
