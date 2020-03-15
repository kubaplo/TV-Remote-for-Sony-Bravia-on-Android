import sys
import argparse
import socket
import re
import requests
import json
import collections


version = "2.0 on Kivy"  #Prepared to use in Kivy

'''
Information about the author of this module:

Author: Darko Sancanin
Twitter: @darkosan
GitHub: https://github.com/darkosancanin
'''

'''
You can find original (not modified by me) files of this project here:
        https://github.com/darkosancanin/bravia_console
'''



def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", type=str, help="the ip address of the TV", required=False)
    parser.add_argument("-c", "--command", type=str, help="the command to send to the TV", required=False)
    args = parser.parse_args()
    return args


class BraviaConsole:
    def __init__(self, psk: str):
        self.psk = psk
        self.ip = None
        self.sys_info = {}
        self.commands = {}
        self.model = "Bravia"
        #----------------------
        self.tv_exists = "Unable to find Bravia TV..."
        self.psk_needed = False
        self.undefined_error = False


    def exit_braviaremote(self):
        sys.exit()

    def find_tv(self):
        SSDP_ADDR = "239.255.255.250"
        SSDP_PORT = 1900

        ssdpRequest = "M-SEARCH * HTTP/1.1\r\n" + \
                      "HOST: %s:%d\r\n" % (SSDP_ADDR, SSDP_PORT) + \
                      "MAN: \"ssdp:discover\"\r\n" + \
                      "MX: 1\r\n" \
                      "ST: urn:schemas-sony-com:service:ScalarWebAPI:1\r\n\r\n";

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5.0)
        dest = socket.gethostbyname(SSDP_ADDR)
        sock.sendto(ssdpRequest.encode('utf-8'), (dest, SSDP_PORT))
        sock.settimeout(5.0)
        try:
            data = sock.recv(1000)
        except socket.timeout:
            return
        response = data.decode('utf-8')
        match = re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", response)
        if match:
            self.ip = match.group()
            self.tv_exists = "Bravia TV found at IP: %s" % self.ip
        else:
            pass

    def update_commands(self):
        self.commands = {}
        result = self.send_info_request_to_tv("getRemoteControllerInfo")
        if result is not None:
            controller_commands = result[1]
            for command_data in controller_commands:
                self.commands[command_data.get('name').lower()] = command_data.get('value')
            self.commands = collections.OrderedDict(sorted(self.commands.items()))

    def show_commands(self):
        command_list = ""
        for command in self.commands:
            command_list += command + ", "
        if len(command_list) > 0:
            command_list = command_list[:-2]

        return command_list

    def search_commands(self, search_string):
        command_list = ""
        for command in self.commands:
            if search_string in command:
                command_list += command + ", "
        if len(command_list) > 0:
            command_list = command_list[:-2]


    def update_sys_info(self):
        if self.ip is None:
            return
        result = self.send_info_request_to_tv("getSystemInformation")
        if result is not None:
            self.sys_info = result[0]
            self.model = f"Bravia {self.sys_info['model']}"

    def show_sys_info(self):
        for info in self.sys_info:
            pass

    def send_info_request_to_tv(self, command):
        body = {"method": command, "params": [], "id": 1, "version": "1.0"}
        json_body = json.dumps(body).encode('utf-8')
        headers = {}
        headers['X-Auth-PSK'] = self.psk
        try:
            response = requests.post('http://' + self.ip + '/sony/system', headers=headers, data=json_body, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError as exception_instance:
            if response.status_code == 403:
                self.psk_needed = True
            else:
                self.undefined_error = True
            return None
        except Exception as exception_instance:
            self.undefined_error = True
            return None
        else:
            return json.loads(response.content.decode('utf-8'))["result"]

    def send_command_to_tv(self, command):
        if command not in self.commands:
            return False;
        ircc_code = self.commands[command]
        body = "<?xml version=\"1.0\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body><u:X_SendIRCC xmlns:u=\"urn:schemas-sony-com:service:IRCC:1\"><IRCCCode>" + ircc_code + "</IRCCCode></u:X_SendIRCC></s:Body></s:Envelope>"
        headers = {}
        headers['X-Auth-PSK'] = self.psk
        headers['Content-Type'] = "text/xml; charset=UTF-8"
        headers['SOAPACTION'] = "\"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC\""
        try:
            response = requests.post('http://' + self.ip + '/sony/IRCC', headers=headers, data=body, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError as exception_instance:
            if response.status_code == 403:
                self.psk_needed = True
            else:
                self.undefined_error = True

        except Exception as exception_instance:
            self.undefined_error = True
        return True

    def auto_configure(self):
        if self.ip is None:
            self.find_tv()
        if self.ip is not None:
            self.update_sys_info()
            self.update_commands()
        else:
            pass

    def show_options(self):
        pass

    def set_ip_address(self, ip):
        match = re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", ip)
        if match:
            self.ip = match.group()
        else:
            pass

    def set_option(self, option_name_value):
        if option_name_value.startswith("psk "):
            psk = option_name_value[4:]
            self.psk = psk
        elif option_name_value.startswith("ip "):
            self.set_ip_address(option_name_value)
        else:
            pass

    def signal_handler(self, signal, frame):
        self.exit_braviaremote()

    def execute_user_command(self, command):
        if command == "?" or command == "help":
            pass
        elif command == "configure":
            self.auto_configure()
        elif command == "find tv":
            self.find_tv()
        elif command == "update commands":
            self.update_commands()
        elif command == "show commands":
            self.show_commands()
        elif command == "show info":
            self.show_sys_info()
        elif command == "show options":
            self.show_options()
        elif command == "update info":
            self.update_sys_info()
        elif command.startswith("search"):
            search_string = command[6:].strip()
            self.search_commands(search_string)
        elif command.startswith("set option"):
            option_name_value = command[10:].strip()
            self.set_option(option_name_value)
        elif command == "quit" or command == "exit":
            self.exit_braviaremote()
        elif command in self.commands:
            self.send_command_to_tv(command)
        else:
            pass

    def start(self, ip, command):
        if ip is not None:
            self.set_ip_address(ip)

        self.auto_configure()

        if command is not None:
            self.execute_user_command(command)
            self.exit_braviaremote()



    def command(self, command):
        self.execute_user_command(command)







def main():
    args = parse_arguments()
    console = BraviaConsole("0000")
    console.start(args.ip, args.command)

if __name__ == "__main__":
    main()