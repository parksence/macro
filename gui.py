import tkinter as tk
from tkinter import ttk
import pyautogui
import keyboard
import threading
import time
import pygetwindow as gw
from PIL import ImageGrab
import pytesseract
import cv2
import numpy as np
from PIL import Image

# Tesseract 경로 설정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

stop_key = 'F12'  # 기본 종료 키
running = True

def create_gui():
    root = tk.Tk()
    root.title("매크로 프로그램")
    root.geometry("600x500")
    root.configure(bg='#f7f9fc')
    
    # 왼쪽 메뉴 프레임
    menu_frame = tk.Frame(root, bg='#dfe6e9', width=150)
    menu_frame.pack(side='left', fill='y')
    
    # 메뉴 버튼 추가
    menu_label = tk.Label(menu_frame, text="메뉴", bg='#dfe6e9', font=('Helvetica', 14, 'bold'))
    menu_label.pack(pady=10)
    
    # 설정 탭
    settings_button = tk.Button(menu_frame, text="설정", bg='#b2bec3', relief='flat', command=lambda: show_frame(settings_frame))
    settings_button.pack(fill='x')
    
    # 설정 프레임
    settings_frame = tk.Frame(root, bg='#f7f9fc')
    settings_frame.pack(side='right', fill='both', expand=True)
    
    # 단축키 입력 라벨 및 입력 칸 추가
    key_label = ttk.Label(settings_frame, text="매크로 중지 단축키:")
    key_label.pack(pady=10)
    key_entry = ttk.Entry(settings_frame, font=('Helvetica', 12))
    key_entry.pack(pady=5)
    key_entry.insert(0, stop_key)
    
    # 시작 버튼 추가
    start_button = ttk.Button(settings_frame, text="시작", command=lambda: start_macro(key_entry.get()))
    start_button.pack(pady=10)
    
    # 종료 버튼 추가
    stop_button = ttk.Button(settings_frame, text="종료", command=stop_macro)
    stop_button.pack(pady=10)
    
    root.mainloop()

def show_frame(frame):
    frame.tkraise()

def start_macro(user_key):
    global stop_key, running
    stop_key = user_key
    running = True
    print(f"매크로 시작 - 종료 키: {stop_key}")
    activate_game_window()  # 게임 창 활성화
    threading.Thread(target=monitor_stop_key).start()
    threading.Thread(target=monitor_mana_and_cast_skill).start()

def stop_macro():
    global running
    running = False
    print("매크로 종료")

def activate_game_window():
    windows = gw.getWindowsWithTitle('MapleStory Worlds-옛날바람')
    if windows:
        windows[0].activate()
        time.sleep(1)

def calculate_non_black_pixel_ratio(screenshot):
    # 이미지를 numpy 배열로 변환
    image = np.array(screenshot)
    
    # 대비 조정
    image = cv2.convertScaleAbs(image, alpha=2.5, beta=0)
    
    # 검은색 범위 설정 (RGB 값이 모두 0에 가까운 경우)
    non_black_pixels = cv2.countNonZero(cv2.inRange(image, (30, 30, 30), (255, 255, 255)))
    
    # 전체 픽셀 수
    total_pixels = image.shape[0] * image.shape[1]
    
    # 비검은색 픽셀 비율 계산
    return (non_black_pixels / total_pixels) * 100

def monitor_mana_and_cast_skill():
    global running
    while running:
        # 마나바의 정확한 위치로 조정
        mana_region = (1584, 896, 1765, 916)  # x1, y1, x2, y2
        screenshot = ImageGrab.grab(bbox=mana_region)
        
        # 캡처한 이미지 저장
        screenshot.save("mana_capture.png")
        
        # 비검은색 픽셀 비율 계산
        mana_ratio = calculate_non_black_pixel_ratio(screenshot)
        print(f"마나 비율: {int(mana_ratio)}%")
        
        if mana_ratio < 50:  # 마나가 절반보다 적으면
            pyautogui.press('3')
            print("공력증강 스킬 사용")
        
        time.sleep(1)

def monitor_stop_key():
    global running
    keyboard.wait(stop_key)
    running = False
    print("매크로 종료")

if __name__ == "__main__":
    create_gui() 