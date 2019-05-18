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
        self.t = self.add(npyscreen.TitleFixedText, name='T+', value='0', editable=False)
        self.a = self.add(npyscreen.TitleFixedText, name='Armed', value=False, editable=False)
        self.ft = self.add(npyscreen.TitleFixedText, name='Fall Time', value=False, editable=False)

        self.lin_acc = self.add(npyscreen.BoxTitle, name='Linear Acceleration', max_height=7, editable=False)
        self.gyro = self.add(npyscreen.BoxTitle, name='Angular Velocity', max_height=7, editable=False)
        self.quat = self.add(npyscreen.BoxTitle, name='Orientation', max_height=6, editable=False)

        self.add_handlers({
            'q': quit,
            'a': toggle_arm})

    def while_waiting(self):
        #npyscreen.notify_wait('Update')
        #self.gyro = self.add(npyscreen.BoxTitle, name='Angular Velocity', max_height=3, values=[0,0,0])
        self.t.value = str(time.time() - T_START) 
        self.a.value = 'YES' if arm.ARMED else 'NO'
        self.ft.value = arm.TLM.fall_time
        self.lin_acc.values = ['Mag: '+str(arm.norm(arm.TLM.lin_acc))] + arm.TLM.lin_acc
        self.gyro.values = ['Mag: '+str(arm.norm(arm.TLM.gyro))] + arm.TLM.gyro
        self.quat.values = [self.t.value, 0, 0, 0]
        self.display()


if __name__ == '__main__':
    g = GUI()
    g.run()
