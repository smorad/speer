import npyscreen
import time
import arm
import sys
import threading


#T_START = time.time()
IGN_TIME = 0.6415


def quit(*args, **kwargs):
    sys.exit(0)

def toggle_arm(*args, **kwargs):
    arm.ARMED = not arm.ARMED


class GUI(npyscreen.NPSAppManaged):
    keypress_timeout_default = 1
    def onStart(self):
        #self.registerForm('MAIN', Form())
        self.addForm("MAIN", Form, name='SPEER Telemetry Monitor')

class Form(npyscreen.Form):
    def create(self):
        #self.F = npyscreen.Form(name='SPEER TELEMETRY MONITOR')
        self.ins = self.add(npyscreen.TitleFixedText, name="'q' to quit, 'a' to toggle motor arm, 'g' to set gravity vector", editable=False)
        self.t = self.add(npyscreen.TitleFixedText, name='T+', value='0', editable=False)
        self.a = self.add(npyscreen.TitleFixedText, name='Armed', value=False, editable=False)
        self.fall = self.add(npyscreen.TitleFixedText, name='Falling?', value='NO', editable=False)
        self.ft = self.add(npyscreen.TitleFixedText, name='Fall Time', value=False, editable=False)

        self.lin_acc = self.add(npyscreen.BoxTitle, name='Linear Acceleration', max_height=7, editable=False)
        self.gyro = self.add(npyscreen.BoxTitle, name='Angular Velocity', max_height=7, editable=False)
        self.quat = self.add(npyscreen.BoxTitle, name='Orientation', max_height=6, editable=False)

        self.bno, self.imu_f = arm.setup()
        self.start_time = time.time()

        self.thr = threading.Thread(target=arm.main_loop2, args=(self.bno, self.imu_f, IGN_TIME))
        self.thr.daemon = True
        self.thr.start()

        self.add_handlers({
            'q': quit,
            'a': toggle_arm,
            })

    def while_waiting(self):
        #npyscreen.notify_wait('Update')
        #self.gyro = self.add(npyscreen.BoxTitle, name='Angular Velocity', max_height=3, values=[0,0,0])
        #arm.main_loop2(self.start_time, self.bno, self.imu_f, IGN_TIME)
        #self.t.value = str(time.time() - arm.START_TIME) 
        if arm.ARMED:
            self.a.value = 'YES' 
            self.a.labelColor = 'DANGER'
        else:
            self.a.value = 'NO'
            self.a.color = 'DEFAULT'
            self.a.labelColor = 'DEFAULT'

        if arm.FALLING:
            self.fall.value = 'YES' 
            self.fall.labelColor = 'DANGER'
        else:
            self.fall.value = 'NO'
            self.fall.color = 'DEFAULT'
            self.fall.labelColor = 'DEFAULT'



        self.ft.value = arm.TLM.fall_time
        self.lin_acc.values = ['Mag: '+str(arm.norm(arm.TLM.lin_acc))] + list(arm.TLM.lin_acc)
        self.gyro.values = ['Mag: '+str(arm.norm(arm.TLM.gyro))] + list(arm.TLM.gyro)
        self.quat.values = arm.TLM.quat 
        self.t.value = arm.TLM.stime
        self.display()


if __name__ == '__main__':
    g = GUI()
    g.run()
    import os
    os.touch('bork')
    a = arm.setup()
