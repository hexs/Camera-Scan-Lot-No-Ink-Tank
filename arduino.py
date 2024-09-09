import time
import serial
from serial.tools.list_ports_windows import comports


def find_comports(args):
    for i in comports():
        for name_of_comports in args:
            if name_of_comports in i.description:
                print(f'auto connect to {i.device}')
                return i.device


class Arduino:
    BUF_SIZE = 50

    def __init__(self):
        self.buff = '-' * self.BUF_SIZE

    def setup(self, *args):
        while True:
            try:
                port = find_comports(args)
                baud_rate = 9600
                self.ser = serial.Serial(port, baud_rate, timeout=1)
                return
            except:
                print(f'ERROR serial.Serial(...)')
                time.sleep(1)

    def addToBuffer(self, string):
        string = string.replace('\n', '').replace('\r', '')
        self.buff += string
        self.buff = self.buff[len(self.buff) - self.BUF_SIZE:]

    def extractCommand(self, string):
        """
        Extract a command enclosed in angle brackets from the given string.

        Args:
        string (str): The input string to check for a command.

        Returns:
        str or None: The extracted command if found, otherwise None.
        """
        if not string.endswith('>'):
            return None

        start = string.rfind('<')

        if start != -1 and start < len(string) - 1:
            return string[start + 1:-1]

        return None

    def splitCommand(self, command: str):
        """
        # Examples:
        >> splitCommand('set(abc,500)')
        ['set', 'abc', '500']
        >> splitCommand('get()')
        ['get']
        >> splitCommand('complex(a,b,c)')
        ['complex', 'a', 'b', 'c']
        >> splitCommand('no_parens')
        ['no_parens']
        """
        # Check if the command contains parentheses
        if '(' in command and command.endswith(')'):
            # Split the command into function name and arguments
            func_name, args_str = command.split('(', 1)
            args_str = args_str[:-1]  # Remove the closing parenthesis

            # Split arguments and handle empty arguments
            args = [arg.strip() for arg in args_str.split(',') if arg.strip()]

            return [func_name] + args
        else:
            # If there are no parentheses, return the command as is
            return [command]

    def write(self, string):
        '''
        string = 'crgb(255,255,255)'
        '''
        self.ser.write(f'<{string}>'.encode('utf-8'))

    def read(self):
        x = self.ser.read(1)
        self.addToBuffer(x.decode('utf-8'))
        command = self.extractCommand(self.buff)
        if command is not None:
            self.addToBuffer('-')
        return command


def run_arduino(data):
    arduino = Arduino()
    arduino.setup('Arduino', 'USB Serial Device')
    while data['run']:
        try:
            command = arduino.read()
            if command:
                # print(command)
                split_command = arduino.splitCommand(command)
                # print(split_command)
                if command == 'press':
                    data['command'] = 'read data'
                    arduino.write('crgb(255,255,150)')
                if command == 'release':
                    data['command'] = ''
                    arduino.write('crgb(10,10,10)')

            if data['command'] == 'read data ok':
                data['command'] = ''
                arduino.write('crgb(0,255,0)')
                time.sleep(0.1)
                arduino.write('crgb(0,0,0)')
                time.sleep(0.1)
                arduino.write('crgb(0,255,0)')
                time.sleep(0.1)
                arduino.write('crgb(0,0,0)')
        except Exception as e:
            print(f"arduino Error: {e}")
            arduino.setup('Arduino')
            time.sleep(0.5)


def main(data):
    ...


if __name__ == '__main__':
    import multiprocessing

    manager = multiprocessing.Manager()
    data = manager.dict()
    data['command'] = ''
    data['split_command'] = ''

    arduino_process = multiprocessing.Process(target=run_arduino, args=(data,))
    main_process = multiprocessing.Process(target=main, args=(data,))

    arduino_process.start()
    main_process.start()

    arduino_process.join()
    main_process.start()
