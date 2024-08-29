import time
import cv2
import numpy as np
from datetime import datetime

BLACK = '\033[90m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
PINK = '\033[95m'
CYAN = '\033[96m'
ENDC = '\033[0m'
BOLD = '\033[1m'
ITALICIZED = '\033[3m'
UNDERLINE = '\033[4m'


def capture(data):
    cap = cv2.VideoCapture(0)

    while data['run']:
        s, img = cap.read()
        if s:
            data['cap'] = s, cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            time.sleep(1)
            cap = cv2.VideoCapture(0)


def main(data):
    import pytesseract
    from read_barcode import read_barcodes

    pytesseract.pytesseract.tesseract_cmd = r'C:\Tesseract-OCR\tesseract.exe'
    t1 = datetime.now()
    while data['run']:
        t2 = t1
        t1 = datetime.now()
        data['fps'] = round(1 / max(0.001, (t1 - t2).total_seconds()), 1)
        s, img = data['cap']
        if data['command'] == 'read data':

            if not data['data complete'][0]:
                texts = pytesseract.image_to_string(
                    img,
                    config='--psm 6 -c tessedit_char_whitelist=0123456789[]:ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                )
                # print(texts)
                for text in texts.split('\n'):
                    if text == '':
                        continue
                    # print("--->", text)
                    if 'MC' in text:
                        data['MC'] = text
                    if 'QTY' in text:
                        data['QTY'] = text
                    if 'LN' in text or 'N:' in text:
                        print(BLUE, text, ENDC)
                        text = text.split('N')[-1]
                        ndmy = text.strip().strip('LN').strip().strip(':').strip()
                        print(PINK, ndmy, ENDC)
                        if len(ndmy) == 7:
                            l = ndmy[0:2]
                            y = ndmy[2:4]
                            m = ndmy[4]
                            d = ndmy[5:]
                            print((l, d, m, y,))
                            if all(i.isdigit() for i in (d, y)) and m in 'ABCDEFGHIJKL':
                                d = int(d)
                                y = int(y) + 2000
                                m = ord(m) - ord('A') + 1
                                if 1 <= d <= 31:
                                    data['LN'] = ndmy
                                    data['date'] = datetime(year=y, month=m, day=d)
                                    data['lot'] = l

                                    data['data complete'] = True, data['data complete'][1]

            if not data['data complete'][1]:
                bar = read_barcodes(img)
                if bar:
                    data['barcode'] = bar
                    if len(bar) == 20 and '92' in bar and '30' in bar:
                        bar = bar.replace('92', '[').replace('30', ']')
                        QTY = bar.split(']')[1]
                        data['bar QTY'] = QTY
                        data['bar MC'] = bar[2:-2].replace('[', '').replace(']', '')

                        data['data complete'] = data['data complete'][0], True

            if all(data['data complete']):
                data['command'] = 'read data ok'


def getkey(data):
    import pyperclip
    import keyboard
    import time
    import pygame

    pygame.init()
    pygame.mixer.init()

    sound1 = pygame.mixer.Sound('teed.mp3')
    sound2 = pygame.mixer.Sound('teed teed.mp3')
    while data['run']:
        if data['old data complete'] != data['data complete']:
            data['old data complete'] = data['data complete']
            if all(data['data complete']):
                pass
            else:
                sound1.play()

        if all(data['data complete']):
            sound2.play()
            pyperclip.copy(data['bar MC'])
            time.sleep(0.1)
            keyboard.press_and_release('right, ' * 2 + 'Ctrl + v')
            time.sleep(0.1)
            pyperclip.copy(data['LN'])
            time.sleep(0.1)
            keyboard.press_and_release('right, ' * 5 + 'Ctrl + v')
            time.sleep(0.1)
            pyperclip.copy(data['bar QTY'])
            time.sleep(0.1)
            keyboard.press_and_release('right, Ctrl + v, \n, Home')

            data['data complete'] = False, False
            data['old data complete'] = False, False

            data['MC'] = ''
            data['LN'] = ''
            data['QTY'] = ''

            data['barcode'] = ''
            data['bar MC'] = ''
            data['bar QTY'] = ''

            data['date'] = ''
            data['lot'] = ''


if __name__ == '__main__':
    import multiprocessing
    from pg_UI import pg_UI
    from arduino import run_arduino

    manager = multiprocessing.Manager()
    data = manager.dict()
    data['run'] = True
    data['cap'] = (False, np.full((480, 640, 3), (30, 50, 25), np.uint8))
    data['fps'] = 0

    data['data complete'] = False, False
    data['old data complete'] = False, False

    data['MC'] = ''
    data['LN'] = ''
    data['QTY'] = ''

    data['barcode'] = ''
    data['bar MC'] = ''
    data['bar QTY'] = ''

    data['date'] = ''
    data['lot'] = ''

    data['command'] = ''

    capture_process = multiprocessing.Process(target=capture, args=(data,))
    main_process = multiprocessing.Process(target=main, args=(data,))
    show_process = multiprocessing.Process(target=pg_UI, args=(data,))
    getkey_process = multiprocessing.Process(target=getkey, args=(data,))
    arduino_process = multiprocessing.Process(target=run_arduino, args=(data,))

    capture_process.start()
    main_process.start()
    show_process.start()
    getkey_process.start()
    arduino_process.start()

    capture_process.join()
    main_process.join()
    show_process.join()
    getkey_process.join()
    arduino_process.join()
