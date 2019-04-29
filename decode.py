import sys
import math
import numpy as np
from arm import FREQ

t_ign = 0.6415
path = sys.argv[1]
with open(path, 'r') as f:
    motor_on = False
    fall_detected = False
    t_fall_start = 0
    for line in f:
        stime,quat,gyro,acc,linacc,grav = line.split(' ')
        stime = float(stime.replace('T+',''))
        quat = np.array([float(q) for q in quat.replace('q:','').split(',')])
        gyro = np.array([float(q) for q in gyro.replace('w:','').split(',')])
        acc = np.array([float(q) for q in acc.replace('accel:','').split(',')])
        linacc = np.array([float(q) for q in linacc.replace('lin_accel:','').split(',')])
        grav = np.array([float(q) for q in grav.replace('grav:','').split(',')])

        
        if np.linalg.norm(linacc) > 7 and not motor_on and not fall_detected:
            fall_detected = True
            t_fall_start = stime

        if np.linalg.norm(linacc) > 7 and not motor_on:
            t_fall = stime - t_fall_start
            print('T+{:.2f} | T{:.2F}'.format(stime, t_fall - t_ign))
            if t_fall >= t_ign:
                print('start motor', stime)
                #start_motor(stime)
                motor_on = True
        else:
            t_fall = 0
            t_fall_start = 0
            fall_detected = False


        #print(stime, np.linalg.norm(linacc))

