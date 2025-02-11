import pygetwindow as gw
import pyautogui
import time

def move_left_in_msw():
    # 정확한 창 제목으로 수정
    windows = gw.getWindowsWithTitle('MapleStory Worlds-옛날바람')
    if windows:
        msw_window = windows[0]
        msw_window.activate()  # 창 활성화

    else:
        print("창을 찾을 수 없습니다.")

def list_all_windows():
    windows = gw.getAllTitles()
    for title in windows:
        print(title)

if __name__ == "__main__":
    move_left_in_msw()
    list_all_windows() 