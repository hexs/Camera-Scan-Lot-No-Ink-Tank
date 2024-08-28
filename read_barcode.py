from pyzbar.pyzbar import decode
import cv2


def read_barcodes(image):
    decoded_objects = decode(image)
    for obj in decoded_objects:
        # print("Type:", obj.type)
        # print("Data:", obj.data.decode('utf-8'))
        return obj.data.decode('utf-8')


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)

    while True:
        _, img = cap.read()
        read_barcodes(img)
        cv2.imshow('img', img)
        cv2.waitKey(1)
