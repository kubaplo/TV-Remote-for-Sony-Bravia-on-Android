__author__ = "SZP3N10"

import braviacontrol, brute_psk

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.lang import Builder

import threading



class MainLayout(FloatLayout):
    def get_ids(self):
        return self.ids.main_container, self.ids.model_label, self.ids.ip_label, self.ids.psk_label, self.ids.canvas_widget



class HiddenLayout(FloatLayout):
    def get_ids(self):
        return self.ids.all_options_box_layout



class AllOptionsBox(GridLayout):
    def get_ids(self):
        return self.ids.all_options_final_box



class AOButton(Button):
    pass


class GreetingScreen(FloatLayout):
    def get_ids(self):
        return self.ids.textinput, self.ids.loading_label

class Layout(BoxLayout):
    pass



class RemoteApp(App):
    Builder.load_file("style.kv")

    def user_variables(self):
        '''Method to decide if bruteforcing is needed or PSK was already provided.
        This method takes action only when bruteforcing was requested'''

        if "BRUTE" in self.psk_code:
            if len(self.psk_code.split()) == 1:
                start_psk = 0

            elif len(self.psk_code.split()) == 2:
                try:
                    start_psk = int(self.psk_code.split()[1])
                except:
                    start_psk = 0

            else:
                start_psk = 0

            label_id = self.greeting_layout.get_ids()[1]
            self.brute = brute_psk.Brute(label_id, start_psk)   #Insert start value of guessing psk, default is 0
            self.psk_code = self.brute.start()



    def connect(self, md, ip, psk, diode):
        '''Method that connects to Sony Bravia TV on the local network.
        Takes 4 arguments: label containing TV's model; label with ip; label with psk; diode widget'''

        self.user_variables()

        bravia = braviacontrol.BraviaConsole(self.psk_code)
        args = braviacontrol.parse_arguments()
        bravia.start(args.ip, args.command)

        self.bravia = bravia

        if bravia.model == "Bravia":
            bravia.model = "Unable to find Bravia TV ..."

        if bravia.ip == None:
            bravia.ip = "---"

        if bravia.model == "Unable to find Bravia TV ..." and bravia.ip != "---":
            bravia.model = "Wrong PSK !"

            diode.my_color = (1, 1, 0, 1)
            md.my_color = (1, 1, 0, 1)
            ip.my_color = (1, 1, 0, 1)
            psk.my_color = (1, 1, 0, 1)


        md.text = bravia.model
        ip.text = f"IP: {bravia.ip}"
        psk.text = f"PSK: {bravia.psk}"

        if md.text != "Unable to find Bravia TV ..." and md.text != "Wrong PSK !":
            diode.my_color = (0, 1, 0, 1)
            md.my_color = (0, 1, 0, 1)
            ip.my_color = (0, 1, 0, 1)
            psk.my_color = (0, 1, 0, 1)





    def build(self):
        '''Method to build application's body'''

        self.title = "Bravia Remote Control"
        self.window_size = Window.size

        self.main_window = Layout()

        self.greeting_layout = GreetingScreen() #Creating screen with widget to enter TV's PSK or request to guess it

        self.main_window.add_widget(self.greeting_layout)

        textinput = self.greeting_layout.get_ids()[0]
        textinput.bind(on_text_validate = self.open_remote) #Go to the next screen after clicking <enter>


        self.aobutton_height = 200
        self.total_height = 0

        self.main_layout = MainLayout() #Creating screen with main widgets to control your TV, visible after entering your PSK in previous screen

        self.hidden_layout = HiddenLayout()
        self.all_options_box_layout = self.hidden_layout.get_ids()

        self.all_options_box = AllOptionsBox()
        self.all_options_final_box = self.all_options_box.get_ids()


        return self.main_window


    def buttons_functions(self, instance):
        '''Method that defines each button functions'''

        if instance.text == "UP":
            self.bravia.command("up")

        elif instance.text == "RIGHT":
            self.bravia.command("right")

        elif instance.text == "DOWN":
            self.bravia.command("down")

        elif instance.text == "LEFT":
            self.bravia.command("left")

        elif instance.text == "OK":
            self.bravia.command("confirm")

        elif instance.text == "Channel\nUP":
            self.bravia.command("channelup")

        elif instance.text == "Channel\nDOWN":
            self.bravia.command("channeldown")

        elif instance.text == "Volume\nUP":
            self.bravia.command("volumeup")

        elif instance.text == "Volume\nDOWN":
            self.bravia.command("volumedown")

        elif instance.text == "MUTE":
            self.bravia.command("mute")


        elif instance.text == "INPUTS":
            self.bravia.command("input")

        elif instance.text == "OPTIONS":
            self.bravia.command("options")

        elif instance.text == "EPG":
            self.bravia.command("epg")


        elif instance.text == "1":
            self.bravia.command("num1")

        elif instance.text == "2":
            self.bravia.command("num2")

        elif instance.text == "3":
            self.bravia.command("num3")

        elif instance.text == "4":
            self.bravia.command("num4")

        elif instance.text == "5":
            self.bravia.command("num5")

        elif instance.text == "6":
            self.bravia.command("num6")

        elif instance.text == "7":
            self.bravia.command("num7")

        elif instance.text == "8":
            self.bravia.command("num8")

        elif instance.text == "9":
            self.bravia.command("num9")

        elif instance.text == "0":
            self.bravia.command("num0")


        elif instance.text == "ON/\nOFF":
            self.bravia.command("poweroff")

        elif instance.text == "HOME":
            self.bravia.command("home")

        elif instance.text == "RETURN":
            self.bravia.command("return")


        elif instance.text == "EXPAND":
            self.main_container.height = self.window_size[1] * 2

            self.main_container.add_widget(self.hidden_layout)

            instance.text = "SHRINK"

        elif instance.text == "SHRINK":
            self.main_container.height = self.window_size[1]

            self.main_container.remove_widget(self.hidden_layout)

            instance.text = "EXPAND"


        elif instance.clr == "red":
            self.bravia.command("red")

        elif instance.clr == "green":
            self.bravia.command("green")

        elif instance.clr == "blue":
            self.bravia.command("blue")

        elif instance.clr == "yellow":
            self.bravia.command("yellow")


        elif instance.text == "Show all options":
            self.all_options_box_layout.add_widget(self.all_options_box)
            instance.text = "Hide all options"

        elif instance.text == "Hide all options":
            self.all_options_box_layout.remove_widget(self.all_options_box)
            instance.text = "Show all options"




    def all_options_functions(self, instance):
        '''Method that defines functions of AOButtons (All Options Buttons).
        They are displayed after clicking [expand] --> [show all buttons].
        These buttons represents all available remote commands on a specific TV'''

        self.bravia.command(instance.text)



    def open_remote(self, instance = None):
        '''Method for switching between greeting screen and TV remote screen.
        Takes action after clicking on button or pressing <enter> key'''


        def switch_screens():
            textinput, loading_label = self.greeting_layout.get_ids()
            self.psk_code = textinput.text

            def loading_text():
                if "BRUTE" in self.psk_code:
                    loading_label.text = f"Bruteforcing TV's PSK, please be patient !"

                else:
                    loading_label.text = "Loading, please wait ..."

            loading_thread = threading.Thread(target=loading_text, daemon=True)
            loading_thread.start()


            self.main_container, md, ip, psk, diode = self.main_layout.get_ids()
            self.connect(md, ip, psk, diode)

            iter = 0
            for command in (self.bravia.show_commands()).split(", "):

                if self.bravia.show_commands() == '':
                    lab = Label(text="\n\n\n    No commands found ...", color=(1, 0, 0, 1), font_size="20dp")
                    self.all_options_final_box.add_widget(lab)

                else:
                    btn = AOButton(text=command)
                    self.all_options_final_box.add_widget(btn)

                    iter += 1
                    if iter == 3:
                        self.total_height += self.aobutton_height + 10
                        iter = 0

            if iter == 1 or iter == 2:
                self.total_height += self.aobutton_height + 10
                pass

            self.all_options_final_box.height = self.total_height + 10


            self.main_window.remove_widget(self.greeting_layout)
            self.main_window.add_widget(self.main_layout)


        switch_screens_thread = threading.Thread(target=switch_screens, daemon=True)
        switch_screens_thread.start()





def main():
    remote = RemoteApp()
    remote.run()




if __name__ == '__main__':
    main()