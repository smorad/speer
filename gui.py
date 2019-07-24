import npyscreen
import time
import arm
import sys


T_START = time.time()


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
        self.setg = self.add(npyscreen.TitleFixedText, name='Set G?', value='NO', editable=False)
        self.acc_from_grav = self.add(npyscreen.TitleFixedText, name='G Acc.', value='0', editable=False)
        self.ft = self.add(npyscreen.TitleFixedText, name='Fall Time', value=False, editable=False)

        self.lin_acc = self.add(npyscreen.BoxTitle, name='Linear Acceleration', max_height=7, editable=False)
        self.gyro = self.add(npyscreen.BoxTitle, name='Angular Velocity', max_height=7, editable=False)
        self.quat = self.add(npyscreen.BoxTitle, name='Orientation', max_height=6, editable=False)

        self.add_handlers({
            'q': quit,
            'a': toggle_arm,
            'g': self.set_grav})

    def set_grav(self, *args, **kwargs):
        arm.GRAV_VECTOR = arm.unit(arm.TLM.grav)

    def while_waiting(self):
        #npyscreen.notify_wait('Update')
        #self.gyro = self.add(npyscreen.BoxTitle, name='Angular Velocity', max_height=3, values=[0,0,0])
        self.t.value = str(time.time() - T_START) 
        if arm.ARMED:
            self.a.value = 'YES' 
            self.a.labelColor = 'DANGER'
        else:
            self.a.value = 'NO'
            self.a.color = 'DEFAULT'
            self.a.labelColor = 'DEFAULT'

        if arm.GRAV_VECTOR:
            self.setg.value='YES : ' + str(','.join([str(x) for x in arm.GRAV_VECTOR]))
            self.setg.labelColor = 'DANGER'
            self.setg.color = 'DANGER'

        self.acc_from_grav.value = arm.TLM.acc_from_grav
        self.ft.value = arm.TLM.fall_time
        self.lin_acc.values = ['Mag: '+str(arm.norm(arm.TLM.lin_acc))] + arm.TLM.lin_acc
        self.gyro.values = ['Mag: '+str(arm.norm(arm.TLM.gyro))] + arm.TLM.gyro
        self.quat.values = arm.TLM.quat 
        self.display()


if __name__ == '__main__':
    g = GUI()
    g.run()
