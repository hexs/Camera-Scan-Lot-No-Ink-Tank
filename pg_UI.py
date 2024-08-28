import numpy as np
import pygame
import sys
import cv2
from datetime import datetime


def putTextRect(img, text, pos, font, scale, colorT=(255, 255, 255), thickness=3,
                colorR=(0, 0, 0), offset=1):
    ox, oy = pos
    (w, h), _ = cv2.getTextSize(text, font, scale, thickness)
    x1, y1, x2, y2 = ox - offset, oy + offset, ox + w + offset, oy - h - offset
    cv2.rectangle(img, (x1, y1), (x2, y2), colorR, cv2.FILLED)
    cv2.putText(img, text, (ox, oy), font, scale, colorT, thickness, -1)
    return img, [x1, y2, x2, y1]


def array_to_surface(array):
    # array = np.transpose(array)
    array = np.uint8(array)  # Convert to 8-bit integer
    array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
    surface = pygame.surfarray.make_surface(array)
    return surface


def cvimage_to_pygame(image):
    """Convert cvimage into a pygame image"""
    if type(None) == type(image):
        image = np.full((480, 640, 3), (30, 50, 25), np.uint8)
    else:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return pygame.image.frombuffer(image.tobytes(), image.shape[1::-1], "RGB")


def pg_UI(data):
    # import win32gui
    # import win32con

    pygame.init()
    WIDTH, HEIGHT = 900, 480
    display = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Camera Scan")

    # Get the window handle
    hwnd = pygame.display.get_wm_info()["window"]
    # use Always On Top
    # win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)

    rect_width, rect_height = 50, 50
    rect_x, rect_y = WIDTH // 2 - rect_width // 2, HEIGHT // 2 - rect_height // 2
    rect_speed = 5

    clock = pygame.time.Clock()
    font = pygame.font.Font('Roboto-Regular.ttf', 18)
    while data['run']:
        s, img = data['cap']
        if s:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            for i in [100, 200, 300, 400]:
                cv2.line(img, (0, i), (640, i), (255, 0, 0), 1)

        surface = cvimage_to_pygame(img)

        t_fps = f"fps: {data['fps']}"
        t_barcode_ok = f"read barcode = {data['data complete'][1]}"
        c_barcode_ok = (20, 255, 20) if data['data complete'][1] else (255, 20, 20)
        t_lot_ok = f"read lot and date = {data['data complete'][0]}"
        c_lot_ok = (20, 255, 20) if data['data complete'][0] else (255, 20, 20)
        if isinstance(data['date'], datetime):
            t_date = f"{data['date'].strftime('%d/%m/%y')}"
        else:
            t_date = ''
        texts = {
            'fps': (font.render(t_fps, True, (0, 0, 0)), 1),
            'barcode ok': (font.render(t_barcode_ok, True, c_barcode_ok), 4),
            'barcode': (font.render(f"barcode: {data['barcode']}", True, (120, 90, 255)), 5),
            'MC': (font.render(f"MC  : {data['bar MC']}", True, (20, 90, 255)), 6),
            'QTY': (font.render(f"QTY : {data['bar QTY']}", True, (20, 90, 255)), 7),
            'lot ok': (font.render(t_lot_ok, True, c_lot_ok), 10),
            'LN': (font.render(f"LN    : {data['LN']}", True, (120, 90, 255)), 11),
            'lot': (font.render(f"lot     : {data['lot']}", True, (20, 90, 255)), 12),
            'date': (font.render(f'date : {t_date}', True, (20, 90, 255)), 13)
        }
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                data['run'] = False
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            rect_x -= rect_speed
        if keys[pygame.K_RIGHT]:
            rect_x += rect_speed

        display.fill(WHITE)
        pygame.draw.rect(display, BLUE, (rect_x, rect_y, rect_width, rect_height))
        display.blit(surface, (0, 0))
        for k, v in texts.items():
            display.blit(v[0], (650, 20 * v[1]))
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    data = {}
    data['cap'] = None, None
    data['run'] = True
    pg_UI(data)
