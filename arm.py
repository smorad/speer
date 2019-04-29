import os
from Adafruit_BNO055 import BNO055
import subprocess
import time 
import json
import math
import RPi.GPIO as gpio


RELAY_PIN = 21
CALIBRATION_FILE='calibration0.json'
FREQ = 100

def norm(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

def setup_bno():
    bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)
    while not bno.begin():
        print('Failed to initialize BNO055! Retrying...')
    #if not bno.begin():
    #    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
    status, self_test, error = bno.get_system_status()
    print('System status: {0}'.format(status))
    print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
    return bno

def setup_imu(prefix='imu'):
    bno = setup_bno()
    load_calibration(bno)
    i = 0
    fname = None
    while True:
        if not os.path.exists(prefix + str(i) + '.txt'):
            fp = open(prefix + str(i) + '.txt', 'w', 0);
            break
        i += 1
    print('Writing to IMU data to', prefix + str(i) +'.txt')
    return bno, fp

def start_camera():
    return subprocess.Popen(['/home/pi/capture.sh'])

def start_motor(stime):
    start = time.time()
    gpio.output(RELAY_PIN, gpio.HIGH)
    print('MOTOR START T+{}'.format(stime))
    time.sleep(1)
    gpio.output(RELAY_PIN, gpio.LOW)

def main_loop(bno, imu_fp, t_ign):
    motor_on = False
    t_fall = 0
    fall_detected = False
    w_print = 0

    gx,gy,gz = bno.read_gyroscope()
    ax,ay,az = bno.read_accelerometer()
    qx,qy,qz,qw = bno.read_quaternion()
    grx, gry, grz = bno.read_gravity()
    lax,lay,laz = bno.read_linear_acceleration()
    print('Initial State:')
    print(
            'q:{:0.2F},{:0.2F},{:0.2F},{:0.2F} '
            'w:{:0.2F},{:0.2F},{:0.2F} ' 
            'accel:{:0.2F},{:0.2F},{:0.2F} '
            'lin_accel:{:0.2F},{:0.2F},{:0.2F} '
            'grav:{:0.2F},{:0.2F},{:0.2F} '.format(qx,qy,qz,qw,gx,gy,gz,ax,ay,az,lax,lay,laz,grx,gry,grz))
    print('------------------------')
    print('------------------------')
    print('------------------------')
    print('DANGER!')
    print('MOTOR ARMED FOR {}s DROP: STAND CLEAR'.format(t_ign))
    print('------------------------')
    print('------------------------')
    print('------------------------')
    start_camera()
    tstart = time.time()
    while True:
        try:
            w_print += 1
            stime = time.time() - tstart
            gx,gy,gz = bno.read_gyroscope()
            # Accelerometer data (in meters per second squared):
            ax,ay,az = bno.read_accelerometer()
            qx,qy,qz,qw = bno.read_quaternion()
            grx, gry, grz = bno.read_gravity()
            # Linear acceleration data (i.e. acceleration from movement, not gravity--
            # returned in meters per second squared):
            lax,lay,laz = bno.read_linear_acceleration()
            state_str = (
                'T+{} '
                'q:{:0.2F},{:0.2F},{:0.2F},{:0.2F} '
                'w:{:0.2F},{:0.2F},{:0.2F} ' 
                'accel:{:0.2F},{:0.2F},{:0.2F} '
                'lin_accel:{:0.2F},{:0.2F},{:0.2F} '
                'grav:{:0.2F},{:0.2F},{:0.2F} '
                'ign_t:{:0.2F}' .format(stime,qx,qy,qz,qw,gx,gy,gz,ax,ay,az,lax,lay,laz,grx,gry,grz,t_fall)
            )
            if w_print > FREQ/2:
                print('w: {}'.format(norm([gx, gy, gz])))
                w_print = 0
            imu_fp.write(state_str)



            if norm([lax, lay, lax]) > 7 and not motor_on and not fall_detected:
                fall_detected = True
                t_fall_start = stime

            if norm([lax, lay, laz]) > 7 and not motor_on:
                t_fall = stime - t_fall_start
                print('T+{:.2f} | T{:.2F}'.format(stime, t_fall - t_ign))
                if t_fall >= t_ign:
                    start_motor(stime)
                    motor_on = True
                    os.fsync(imu_fp)
            else:
                t_fall = 0
                t_fall_start = 10e10
                fall_detected = False
        except Exception as e:
            print(e)

        time.sleep(float(1) / FREQ)


def load_calibration(bno):
    # Load calibration from disk.
    loaded = False
    with open(CALIBRATION_FILE, 'r') as cal_file:
        data = json.load(cal_file)
        # Grab the lock on BNO sensor access to serial access to the sensor.
        print('Loading calibration data:', data)
        while not loaded:
            try:
                bno.set_calibration(data)
                loaded = True
            except:
                print('Failed to load, retrying...')

def setup_motor():
    gpio.setmode(gpio.BCM)
    gpio.setup(RELAY_PIN, gpio.OUT)

def setup():
    bno, imu_f = setup_imu()
    cam_proc = start_camera()
    setup_motor()
    main_loop(bno, imu_f, 0.6415)


if __name__ == '__main__':
    setup()

