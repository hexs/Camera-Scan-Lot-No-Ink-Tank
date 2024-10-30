import time
import cv2
import numpy as np
from datetime import datetime
from hexss.constants.cml import *


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
    from hexss import json_load

    changes_data = {}
    changes = json_load('MC_change.json')

    for _, change in changes.items():
        from_part = change['from']
        to_part = change['to']
        count = change['n']

        base_from = int(from_part[:4])
        suffix_from = from_part[4:]

        base_to = int(to_part.split('-')[1])

        for i in range(count):
            old_part = f"{base_from + i:04d}{suffix_from}"
            new_part = f"Q99-{base_to + i:04d}-001"
            changes_data[old_part] = new_part

    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\chtjn\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
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
                oldtext = ''
                # print(texts)
                for text in texts.split('\n'):
                    if text == '':
                        continue
                    if 'LN' in text or 'N:' in text:
                        print(BLUE, text, ENDC)
                        oldtext = text
                        text = text.split('N')[-1]
                        ndmy = text.strip().strip('LN').strip().strip(':').strip()
                        print(PINK, ndmy, ENDC)
                        if len(ndmy) == 7:
                            l = ndmy[0:2]
                            y = ndmy[2:4]
                            m = ndmy[4]
                            d = ndmy[5:]
                            print((l, d, m, y,))
                            if m == '6':
                                m = 'C'
                                ndmy = l + y + m + d
                            if m == '1':
                                m = 'I'
                                ndmy = l + y + m + d
                            if all(i.isdigit() for i in (d, y)) and m in 'ABCDEFGHIJKL':
                                d = int(d)
                                y = int(y) + 2000
                                m = ord(m) - ord('A') + 1
                                if 1 <= d <= 31:
                                    data['LN'] = ndmy
                                    data['date'] = datetime(year=y, month=m, day=d)
                                    data['lot'] = l

                                    data['data complete'] = True, data['data complete'][1]

                    if 'QTY' in text:
                        ndmy = oldtext
                        print(PINK, ndmy, ENDC)
                        if len(ndmy) == 7:
                            l = ndmy[0:2]
                            y = ndmy[2:4]
                            m = ndmy[4]
                            d = ndmy[5:]
                            print((l, d, m, y,))
                            if m == '6':
                                m = 'C'
                                ndmy = l + y + m + d
                            if m == '1':
                                m = 'I'
                                ndmy = l + y + m + d

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
                        bar = bar[2:-2].replace('[', '').replace(']', '')

                        if bar in changes_data:
                            bar = changes_data[bar]

                        data['bar QTY'] = QTY
                        data['bar MC'] = bar

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

            keyboard.press_and_release("Home, right, right, right")
            keyboard.write("'")
            for i in data['bar MC']:
                keyboard.write(f"{i}")

            keyboard.press_and_release('right, right, right, right, right')
            for i in data['LN']:
                keyboard.write(f"{i}")

            keyboard.press_and_release('right')
            for i in data['bar QTY']:
                keyboard.write(f"{i}")

            keyboard.press_and_release('\n, Home')

            data['data complete'] = False, False
            data['old data complete'] = False, False

            data['LN'] = ''

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

    data['LN'] = ''

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
