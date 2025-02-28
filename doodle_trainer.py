import cv2
import numpy as np
from PIL import ImageGrab
import pygetwindow
import pyautogui
import time
import random
import keyboard
import sys
import os
from art import *


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return str(os.path.join(base_path, relative_path))


def initWindow():
    """Grabs and resizes the window of the game"""
    win = pygetwindow.getWindowsWithTitle('Toontown Rewritten')[0]
    win.resizeTo(800, 600)
    win.moveTo(0, 0)


def clamp(n, smallest, largest): return max(smallest, min(n, largest))


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
    tprint("Doodle Trainer V5.0")
    displayMessage('Enter the row number the "PETS" field is at')
    print(end='>')
    pets_row = int(input())
    pets_row = clamp(pets_row, 1, 32)  # Must be at least on row 1
    displayMessage('Enter the number of tricks you have unlocked')
    print(end='>')
    num_tricks = int(input())
    num_tricks = clamp(num_tricks, 1, 7)  # Must be at least 1 and less than or equal to 7
    displayMessage('Starting Calibration... please wait...')
    print(end='>')
    current_mouse_pos = pyautogui.position()

    speedchat = cv2.imread(resource_path('speedchat.png'))

    coordinates = {'speedchat': getCoordinates(screen=np.array(ImageGrab.grab(bbox=(0, 0, 400, 400))), image=speedchat)}
    coordinates['pets'] = (coordinates['speedchat'][0] + 40, coordinates['speedchat'][1] + (18 * (pets_row - 1)))
    coordinates['tricks'] = (coordinates['pets'][0] + 120, coordinates['pets'][1])
    coordinates['here_boy'] = [coordinates['tricks'][0], coordinates['tricks'][1] + 15]

    tricks = []
    for i in range(num_tricks):
        key = "trick_" + str(i)
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
    time.sleep(random.uniform(0.25, 1.25))
    pyautogui.moveTo(coordinates['pets'])
    time.sleep(random.uniform(0.25, 1.25))
    pyautogui.moveTo(coordinates['tricks'])
    time.sleep(random.uniform(0.25, 1.25))
    pyautogui.click(coordinates[selected_tricks[trick]])


def here_boy(coordinates):
    """Navigates the mouse to call the doodle back to us if it runs too far away"""
    pyautogui.click(coordinates['speedchat'])
    time.sleep(random.uniform(0.25, 1.25))
    pyautogui.moveTo(coordinates['pets'])
    time.sleep(random.uniform(0.25, 1.25))
    pyautogui.click(coordinates['here_boy'])


def takeUserInput():
    """Determine all the users criteria"""
    # Select number of tricks
    displayMessage(
        'Select the row numbers of the tricks you want to train. Use commas to separate each trick you want to perform or just enter 0 to train everything. (For example, typing "1,3,5" would train the first, third, and fifth tricks you have. Typing "4" would just train the fourth trick, etc...)')
    print(end='>')
    selected_input = input()
    if '0' in selected_input:
        selected_input = ",".join(map(str, range(1, len(tricks) + 1)))
    selected = list(map(int, selected_input.split(',')))

    # Select percentage of "here boy!"
    displayMessage(
        "What percent of the time would you like other phrases to be mixed in like 'Here Boy!'? Type 0 to turn it off completely, type any decimal from 0.01 to 0.99 to determine the frequency otherwise. (0.05 is recommended)")
    print(end='>')
    here_boy_percent = clamp(float(input()), 0.00, 0.99)

    # Select minimum and maximum trick times
    displayMessage('Select the minimum time between each trick press in seconds. 3-6 seconds is generally recommended.')
    print(end='>')
    minimum_trick_time = clamp(int(input()), 0, 999999999)
    displayMessage(
        'Select the maximum time between each trick press in seconds. 8-10 seconds is generally recommended.')
    print(end='>')
    maximum_trick_time = clamp(int(input()), minimum_trick_time, 999999999)

    # Select hours to run
    displayMessage('How many hours (under or at 6 is recommended) would you like to run the trainer:')
    print(end='>')
    hours = float(input())
    for i in range(len(selected)):
        selected[i] -= 1
    selected_tricks = [tricks[num] for num in selected]

    return hours, selected_tricks, minimum_trick_time, maximum_trick_time, here_boy_percent


def displayMessage(message):
    """Input a string and have it wrapped nicely"""
    print(message)
    print('=========================================================================')


def on_escape():
    tprint("Exiting...")
    print("Thanks for using this program! Remember, I'm not responsible if you get banned :)")
    os._exit(0)


keyboard.add_hotkey('ESC', on_escape)

if __name__ == "__main__":
    initWindow()
    coordinates, tricks = calibrate()

    if coordinates is not None:
        start_time = time.time()
        hours, selected_tricks, minimum_trick_time, maximum_trick_time, here_boy_percent = takeUserInput()
        tricks_performed = 0
        displayMessage('Starting training, you can press the escape key to cancel at any time')
        while hours > (time.time() - start_time) / 3600:
            rand_variation = random.random()
            if rand_variation < here_boy_percent:
                here_boy(coordinates)
                time.sleep(random.uniform(minimum_trick_time, maximum_trick_time))

            hours_message = f'Hours elapsed: {round((time.time() - start_time) / 3600, 2)}/{hours}'
            tricks_message = f'Tricks attempted: {tricks_performed}'
            displayMessage(hours_message + "\n" + tricks_message)

            performTrick(coordinates, selected_tricks)
            tricks_performed += 1
            time.sleep(random.uniform(minimum_trick_time, maximum_trick_time))
