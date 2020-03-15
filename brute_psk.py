__author__ = "SZP3N10"

import braviacontrol, time

class Brute:
    '''Class used to guess TV's PSK.
    Connected to greeting screen from Control.py file.
    Responsible for displaying current guess and estimated time of guessing on greeting screen'''

    def __init__(self, label, start_value = 0):
        self.attempts = start_value
        self.connected = False
        self.psk = "----"
        self.label = label #Label with informations about estimated time & current guess

        self.start()


    def start(self):
        args = braviacontrol.parse_arguments()

        def generate_psk():
            num = str(self.attempts)

            psk = (4 - len(num))*"0" + num

            self.attempts += 1

            return psk

        def convert(num):
            num = int(round(num, 0))

            if num < 60:
                if len(str(num)) < 2:
                    num = "0"+str(num)

                result = f"00:00:{num}"

            elif num >= 60 and num < 3600:
                y = num//60
                x = num - (y*60)

                if len(str(y)) < 2:
                    y = "0"+str(y)

                if len(str(x)) < 2:
                    x = "0"+str(x)

                result = f"00:{y}:{x}"

            else:
                z = num//3600
                y = (num - (z*3600))//60
                x = num - (z*3600) - (y*60)

                if len(str(z)) < 2:
                    z = "0"+str(z)

                if len(str(y)) < 2:
                    y = "0" + str(y)

                if len(str(x)) < 2:
                    x = "0" + str(x)

                result = f"{z}:{y}:{x}"

            return result


        time_of_one = 0
        count = 0
        once_iter = 0
        l = []
        while self.attempts != 9999 and self.connected == False:

            s = time.time()
            if once_iter < 3:
                time_left = "calculating..."
                once_iter += 1

            else:
                time_left = convert((9999 - self.attempts)*time_of_one)


            self.psk_to_try = psk_to_try = generate_psk()
            self.label.text = f"Bruteforcing TV's PSK, please be patient !\nCurrent guess: {self.psk_to_try}\nEstimated time: {time_left}"
            bravia = braviacontrol.BraviaConsole(psk_to_try)
            bravia.start(args.ip, args.command)

            if bravia.model != "Bravia":
                self.connected = True
                self.psk = psk_to_try


            e = time.time()
            l.append(e-s)
            count += 1

            if count == 3:
                medium_time = (l[0] + l[1] + l[2])/3
                time_of_one = round(medium_time, 1)
                count = 0


        return self.psk