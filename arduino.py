import time
import serial


class Arduino:
    BUF_SIZE = 50

    def __init__(self):
        self.buff = '-' * self.BUF_SIZE
        self.setup()

    def setup(self):
        port = 'COM7'
        baud_rate = 9600
        while True:
            try:
                self.ser = serial.Serial(port, baud_rate, timeout=1)
                return
            except:
                print(f'ERROR ser = serial.Serial({port}, {baud_rate})')
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
        return command


def run_arduino(arduino_data):
    arduino = Arduino()
    while True:
        command = arduino.read()
        if command:
            # print(command)
            split_command = arduino.splitCommand(command)
            # print(split_command)

            arduino_data['command'] = command
            arduino_data['split_command'] = split_command

            if arduino_data['command'] == 'press':
                print(arduino_data['command'])
                arduino_data['command'] = ''
                arduino.write('crgb(255,255,255)')
                # time.sleep(1)


def main(arduino_data):
    ...


if __name__ == '__main__':
    import multiprocessing

    manager = multiprocessing.Manager()
    arduino_data = manager.dict()
    arduino_data['command'] = ''
    arduino_data['split_command'] = ''

    arduino_process = multiprocessing.Process(target=run_arduino, args=(arduino_data,))
    main_process = multiprocessing.Process(target=main, args=(arduino_data,))

    arduino_process.start()
    main_process.start()

    arduino_process.join()
    main_process.start()

