import cv2
import numpy as np
from PIL import ImageGrab
import pygetwindow
import pyautogui
import time
import random
import keyboard

def initWindow():
    win = pygetwindow.getWindowsWithTitle('Toontown Rewritten')[0]
    win.resizeTo(800, 600)
    win.moveTo(0, 0)

def getCoordinates(screen, image):
    w, h = image.shape[:-1]

    res = cv2.matchTemplate(screen, image, cv2.TM_CCOEFF_NORMED)
    threshold = .85
    loc = np.where(res >= threshold)

    avg_x, avg_y, count = 0, 0, 0

    for pt in zip(*loc[::-1]):  # Switch columns and rows
        if pt[0] > 50:
            avg_x += pt[0]
            avg_y += pt[1]
            count += 1

    if count > 0:
        avg_x = avg_x / count
        avg_y = avg_y / count
        
    return avg_x + (h/2), avg_y + (w/2)

def calibrate():
    print('Starting Calibration')
    screen = np.array(ImageGrab.grab(bbox=(0, 0, 400, 400)))
    current_mouse_pos = pyautogui.position()

    pictures = {}
    speedchat = cv2.imread('pictures/speedchat.png')
    pets = cv2.imread('pictures/pets.png')
    tricks = cv2.imread('pictures/tricks.png')
    pictures['backflip'] = cv2.imread('pictures/backflip.png')
    pictures['beg'] = cv2.imread('pictures/beg.png')
    pictures['dance'] = cv2.imread('pictures/dance.png')
    pictures['jump'] = cv2.imread('pictures/jump.png')
    pictures['play_dead'] = cv2.imread('pictures/play_dead.png')
    pictures['rollover'] = cv2.imread('pictures/rollover.png')
    pictures['speak'] = cv2.imread('pictures/speak.png')

    coordinates = {}
    coordinates['speedchat'] = getCoordinates(screen=np.array(ImageGrab.grab(bbox=(0, 0, 400, 400))), image=speedchat)
    pyautogui.click(coordinates['speedchat'])
    
    coordinates['pets'] = getCoordinates(screen=np.array(ImageGrab.grab(bbox=(0, 0, 400, 400))), image=pets)
    pyautogui.moveTo(coordinates['pets'])

    coordinates['tricks'] = getCoordinates(screen=np.array(ImageGrab.grab(bbox=(0, 0, 400, 400))), image=tricks)
    pyautogui.moveTo(coordinates['tricks'][0] - 15, coordinates['tricks'][1])
    coordinates['here_boy'] = [coordinates['tricks'][0], coordinates['tricks'][1] + 15]
    
    screen = np.array(ImageGrab.grab(bbox=(0, 0, 400, 400)))
    tricks = []
    for key in pictures.keys():
        coordinate = getCoordinates(screen=screen, image=pictures[key])
        if coordinate[0] > coordinates['tricks'][0]:
            coordinates[key] = coordinate
            tricks.append(key)

    pyautogui.click(coordinates['speedchat'])
    pyautogui.click(current_mouse_pos)
            
    if len(coordinates) > 5:
        print('Calibration Successful')
        return coordinates, tricks
    else:
        print('Calibration Failed')
        return None, None
    
def performTrick(coordinates, selected_tricks):
    trick = random.randint(0, len(selected_tricks) - 1)
    pyautogui.click(coordinates['speedchat'])
    pyautogui.moveTo(coordinates['pets'])
    pyautogui.moveTo(coordinates['tricks'])
    pyautogui.click(coordinates[selected_tricks[trick]])

def hereBoy(coordinates):
    pyautogui.click(coordinates['speedchat'])
    pyautogui.moveTo(coordinates['pets'])
    pyautogui.click(coordinates['here_boy'])

def start():
    initWindow()
    coordinates, tricks = calibrate()
    if not coordinates == None:
        start_time = time.time()

        print('=========================================================================')
        print('Select the tricks you want to perform with commas seperating the numbers:')
        print('=========================================================================')
        for i in range(len(tricks)):
            print(f'{i + 1}: {tricks[i]}')

        print('=========================================================================')
        print(end='>')
        selected = list(map(int, input().split(',')))
        print('=========================================================================')
        print('How many hours would you like to run the trainer:')
        print('=========================================================================')
        print(end='>')
        hours = float(input())
        print('=========================================================================')
        
        for i in range(len(selected)):
            selected[i] -= 1
        
        selected_tricks = [tricks[num] for num in selected]
        tricks_performed = 0

        while(hours > (time.time() - start_time) / 3600):
            if keyboard.is_pressed("ESC"):
                break

            rand_variation = random.randint(0, 100)
            if rand_variation > 82:
                hereBoy(coordinates)
                time.sleep(1 + (rand_variation * 2) / 100)

            print(f'Hours elapsed: {round((time.time() - start_time) / 3600, 2)}/{hours}')
            print(f'Tricks attempted: {tricks_performed}')
            print('=========================================================================')
            performTrick(coordinates, selected_tricks)
            tricks_performed += 1
            time.sleep(3.5 + random.randrange(0,4))

if __name__ == "__main__":
   start()
