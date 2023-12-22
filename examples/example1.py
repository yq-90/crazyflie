# This example contains basic connection, logging (sync/async) and parameter setting
import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper

from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

def logging_cb(timestamp, data, logconf):
    print(f'{timestamp} {logconf.name}: {data}')

def simple_logging_async(scf, logconf):
    scf.cf.log.add_config(logconf)
    logconf.data_received_cb.add_callback(logging_cb)

    # FIXME Put the following code to main in usage
    logconf.start()
    time.sleep(2)
    logconf.stop()

def simple_logging_sync(scf, logconf):
    with SyncLogger(scf, logconf) as logger:
        for log_entry in logger:
            # entry[0]: timestampe
            # entry[1]: data
            # entry[2]: logger name
            print(f'{log_entry[0]} {log_entry[2]}: {log_entry[1]}')


def param_update_cb(name, value):
    print(f'Parameter updated: {name} -> {value}')


# registering callback requires a group and a name serparated by a "."
def simple_param_update_async(scf, groupstr, namestr):
    full_name = f'{groupstr}.{namestr}'
    scf.cf.param.add_update_callback(group=groupstr, name=namestr,
            cb=param_update_cb)

    scf.cf.param.set_value(full_name, 1)
    time.sleep(1)
    scf.cf.param.set_value(full_name, 2)
    time.sleep(1)


if __name__ == '__main__':
    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    lg_stab = LogConfig(name='Stabilizer', period_in_ms=10)
    lg_stab.add_variable('stabilizer.roll', 'float')
    lg_stab.add_variable('stabilizer.pitch', 'float')
    lg_stab.add_variable('stabilizer.yaw', 'float')

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        #simple_logging_async(scf, lg_stab)
        simple_param_update_async(scf, 'stabilizer', 'estimator')
