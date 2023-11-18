import cv2
import numpy as np
from PIL import ImageGrab
import pygetwindow
import pyautogui
import time
import random
import keyboard

def getGameWindows():
    """Tries to get Rewritten and CC windows"""
    toontown_rewritten_win = pygetwindow.getWindowsWithTitle('Toontown Rewritten')
    corporate_clash_win = pygetwindow.getWindowsWithTitle('Corporate Clash')

    return toontown_rewritten_win, corporate_clash_win


def initWindow():
    """Grabs and resizes the window of the game"""

    displayMessage('Finding Window')
    
    toontown_rewritten_win, corporate_clash_win = getGameWindows()

    main_window = None
    if not toontown_rewritten_win == []:
        main_window = toontown_rewritten_win[0]
    elif not corporate_clash_win == []:
        main_window = corporate_clash_win[0]

    if main_window is None:
        return main_window

    main_window.resizeTo(800, 600)
    main_window.moveTo(0, 0)

    return main_window


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
    displayMessage('Starting Calibration... Please Wait...')
    current_mouse_pos = pyautogui.position()

    pictures = {}
    speedchat = cv2.imread('ImageData/speedchat.png')
    pets = cv2.imread('ImageData/pets.png')
    tricks = cv2.imread('ImageData/tricks.png')
    pictures['backflip'] = cv2.imread('ImageData/backflip.png')
    pictures['beg'] = cv2.imread('ImageData/beg.png')
    pictures['dance'] = cv2.imread('ImageData/dance.png')
    pictures['jump'] = cv2.imread('ImageData/jump.png')
    pictures['play_dead'] = cv2.imread('ImageData/play_dead.png')
    pictures['rollover'] = cv2.imread('ImageData/rollover.png')
    pictures['speak'] = cv2.imread('ImageData/speak.png')

    coordinates = {'speedchat': getCoordinates(screen=np.array(ImageGrab.grab(bbox=(0, 0, 400, 400))), image=speedchat)}
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
    displayMessage('Select the tricks you want to train with commas separating the numbers:')
    trick_message = ""
    for i in range(len(tricks)):
        trick_message += f'{i + 1}: {tricks[i]}'
        if i < len(tricks) - 1:
            trick_message += '\n'
    print('0: All')
    displayMessage(trick_message)
    print(end='>')
    selected = input()
    printBreak()
    displayMessage('How many hours (4-8 is recommended) would you like to run the trainer:')
    print(end='>')
    hours = float(input())
    printBreak()

    selected_tricks = []
    if selected == '0':
        selected_tricks = tricks
    else:
        selected = list(map(int, input().split(',')))
        for i in range(len(selected)):
            selected[i] -= 1
        selected_tricks = [tricks[num] for num in selected]

    return hours, selected_tricks

def printBreak():
    """Break Line for after inputs"""
    print('=========================================================================')

def displayMessage(message):
    """Input a string and have it wrapped nicely"""
    print(message)
    printBreak()


if __name__ == "__main__":
    print('=========================================================================')
    mode = initWindow()
    if mode is not None:
        displayMessage(f'{mode.title} mode')
        coordinates, tricks = calibrate()

        if coordinates is not None:
            start_time = time.time()
            hours, selected_tricks = takeUserInput()
            tricks_performed = 0
            displayMessage('Starting training, hold esc for 1 cycle to stop')
            while hours > (time.time() - start_time) / 3600:
                if keyboard.is_pressed("ESC"):
                    break

                rand_variation = random.randint(0, 100)
                if rand_variation > 88:
                    hereBoy(coordinates)
                    time.sleep(1 + (rand_variation * 2) / 100)

                hours_message = f'Hours elapsed: {round((time.time() - start_time) / 3600, 2)}/{hours}'
                tricks_message = f'Tricks attempted: {tricks_performed}'
                displayMessage(hours_message + "\n" + tricks_message)

                performTrick(coordinates, selected_tricks)
                tricks_performed += 1
                time.sleep(4.5 + random.randrange(0, 4))
            displayMessage('Training Completed')
    else:
        displayMessage('No Window Found, Aborting')
