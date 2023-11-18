import cv2
import numpy as np
from PIL import ImageGrab
import pygetwindow
import pyautogui
import time
import random
import keyboard

stop = False


def initWindow():
    """Grabs and resizes the window of the game"""
    win = pygetwindow.getWindowsWithTitle('Toontown Rewritten')[0]
    win.resizeTo(800, 600)
    win.moveTo(0, 0)


def getCoordinates(screen, image):
    """Gets the position of a specified image on the screen using cv2 to match it"""
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

    return avg_x + (h / 2), avg_y + (w / 2)


def calibrate():
    """Determines the coordinates of each of the tricks on the screen"""
    displayMessage('Enter the row number the "PETS" field is at')
    pets_row = input()
    displayMessage('Starting Calibration... please wait...')
    current_mouse_pos = pyautogui.position()

    trick_names = ('jump', 'play_dead', 'rollover', 'backflip', 'speak', 'beg', 'dance')

    speedchat = cv2.imread('speedchat.png')

    coordinates = {'speedchat': getCoordinates(screen=np.array(ImageGrab.grab(bbox=(0, 0, 400, 400))), image=speedchat)}
    coordinates['pets'] = (coordinates['speedchat'][0] + 40, coordinates['speedchat'][1] + (18 * (int(pets_row) - 1)))
    coordinates['tricks'] = (coordinates['pets'][0] + 120, coordinates['pets'][1])
    coordinates['here_boy'] = [coordinates['tricks'][0], coordinates['tricks'][1] + 15]

    tricks = []
    for i in range(len(trick_names)):
        key = str(trick_names[i])
        coordinates[key] = [coordinates['tricks'][0] + 50, coordinates['tricks'][1] + 18.5 * i]
        tricks.append(key)

    pyautogui.click(coordinates['speedchat'])
    pyautogui.moveTo(coordinates['pets'])
    pyautogui.moveTo(coordinates['tricks'])
    pyautogui.click(coordinates['speedchat'])
    pyautogui.moveTo(current_mouse_pos)

    if len(coordinates) > 5:
        displayMessage('Calibration Successful')
        return coordinates, tricks
    else:
        displayMessage('Calibration Failed')
        return None, None


def performTrick(coordinates, selected_tricks):
    """Navigates the mouse to the specified trick via dropdowns and predetermined coordinates"""
    trick = random.randint(0, len(selected_tricks) - 1)
    pyautogui.click(coordinates['speedchat'])
    pyautogui.moveTo(coordinates['pets'])
    pyautogui.moveTo(coordinates['tricks'])
    pyautogui.click(coordinates[selected_tricks[trick]])


def hereBoy(coordinates):
    """Navigates the mouse to call the doodle back to us if it runs too far away"""
    pyautogui.click(coordinates['speedchat'])
    pyautogui.moveTo(coordinates['pets'])
    pyautogui.click(coordinates['here_boy'])


def takeUserInput():
    """Navigates the mouse to call the doodle back to us if it runs too far away"""
    displayMessage('Select the tricks you want to perform with commas separating the numbers:')
    trick_message = ""
    for i in range(len(tricks)):
        trick_message += f'{i + 1}: {tricks[i]}'
        if i < len(tricks) - 1:
            trick_message += '\n'
    displayMessage(trick_message)
    print(end='>')
    selected = list(map(int, input().split(',')))
    displayMessage('How many hours (4-8 is recommended) would you like to run the trainer:')
    print(end='>')
    hours = float(input())
    for i in range(len(selected)):
        selected[i] -= 1

    for num in selected:
        print(num)
        print(tricks[num])
    selected_tricks = [tricks[num] for num in selected]
    return hours, selected_tricks


def displayMessage(message):
    """Input a string and have it wrapped nicely"""
    print(message)
    print('=========================================================================')


def on_escape():
    global stop
    if not stop:
        print("STOPPING TRAINER")
        stop = True


keyboard.add_hotkey('ESC', on_escape)

if __name__ == "__main__":
    initWindow()
    coordinates, tricks = calibrate()

    if coordinates is not None:
        start_time = time.time()
        hours, selected_tricks = takeUserInput()
        tricks_performed = 0
        displayMessage('Starting training, you can press the escape key to cancel at any time')
        while hours > (time.time() - start_time) / 3600 and not stop:
            rand_variation = random.randint(0, 100)
            if rand_variation > 82:
                hereBoy(coordinates)
                time.sleep(1 + (rand_variation * 2) / 100)

            hours_message = f'Hours elapsed: {round((time.time() - start_time) / 3600, 2)}/{hours}'
            tricks_message = f'Tricks attempted: {tricks_performed}'
            displayMessage(hours_message + "\n" + tricks_message)

            performTrick(coordinates, selected_tricks)
            tricks_performed += 1
            time.sleep(3.5 + random.randrange(0, 4))
