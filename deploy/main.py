import win32gui
import win32ui
import win32con
import win32api
import cv2
import numpy as np
import configparser
import threading
import time
import tkinter as tk
from tkinter import simpledialog, messagebox

# 설정 파일 관리
CONFIG_FILE = "settings.ini"
config = configparser.ConfigParser()

# 설정 파일 불러오기
def load_settings():
    """설정 파일 불러오기"""
    global custom_keyboard_macro, moving_delay, custom_delay, image_search_delay
    try:
        config.read(CONFIG_FILE)
        custom_keyboard_macro = config.get("Macros", "custom_macro", fallback="tab,tab,1,2,enter").split(",")
        moving_delay["down"] = float(config.get("Delays", "moving_down_delay", fallback=0.02))
        moving_delay["up"] = float(config.get("Delays", "moving_up_delay", fallback=0.02))
        custom_delay["down"] = float(config.get("Delays", "custom_down_delay", fallback=0.02))
        custom_delay["up"] = float(config.get("Delays", "custom_up_delay", fallback=0.02))
        custom_delay["interval"] = float(config.get("Delays", "custom_interval", fallback=0.02))
        image_search_delay = float(config.get("Delays", "image_search_delay", fallback=0.5))
    except Exception as e:
        print(f"설정을 불러오는 중 오류 발생: {e}")

def find_window(window_title):
    """창 제목으로 핸들을 찾는 함수"""
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd == 0:
        raise Exception(f"창 '{window_title}'을(를) 찾을 수 없습니다.")
    return hwnd

# 설정 파일 저장하기
def save_settings():
    """설정 파일 저장하기"""
    config["Macros"] = {
        "custom_macro": ",".join(custom_keyboard_macro)
    }
    config["Delays"] = {
        "moving_down_delay": str(moving_delay["down"]),
        "moving_up_delay": str(moving_delay["up"]),
        "custom_down_delay": str(custom_delay["down"]),
        "custom_up_delay": str(custom_delay["up"]),
        "custom_interval": str(custom_delay["interval"]),
        "image_search_delay": str(image_search_delay),
    }
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)

# 초기 설정값
custom_keyboard_macro = ["tab", "tab", "1", "2", "enter"]
moving_delay = {"down": 0.02, "up": 0.02}
custom_delay = {"down": 0.02, "up": 0.02, "interval": 0.02}
image_search_delay = 0.5
load_settings()

# 특정 창 캡처
def capture_window(hwnd):
    """특정 창의 화면을 캡처"""
    try:
        left, top, right, bot = win32gui.GetWindowRect(hwnd)
        width, height = right - left, bot - top
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(save_bitmap)
        save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

        # Bitmap을 numpy 배열로 변환
        bmpinfo = save_bitmap.GetInfo()
        bmpstr = save_bitmap.GetBitmapBits(True)
        img = np.frombuffer(bmpstr, dtype=np.uint8)
        img.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)

        # 리소스 정리
        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)

        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # OpenCV BGR 이미지 반환
    except Exception as e:
        print(f"창 캡처 중 오류 발생: {e}")
        return None

# 이미지 서치
def image_search_in_window(hwnd, template_path, threshold=0.8):
    """비활성 창 내부에서 이미지 서치"""
    screenshot = capture_window(hwnd)
    if screenshot is None:
        return None

    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        return max_loc  # 탐지된 좌표 반환
    return None

# 매크로 동작 플래그
image_macro_running = False
moving_macro_running = False
custom_macro_running = False

# 이미지 서치 매크로
def image_macro(hwnd, template_path, threshold=0.8):
    """이미지 서치 매크로"""
    global image_macro_running
    while image_macro_running:
        position = image_search_in_window(hwnd, template_path, threshold)
        if position:
            x, y = position
            # 마우스 클릭 시뮬레이션
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, None, (y << 16) | x)
            time.sleep(0.1)
            win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, (y << 16) | x)
        time.sleep(image_search_delay)

def start_stop_image_macro(hwnd, template_path):
    """이미지 서치 매크로 시작/중지"""
    global image_macro_running
    if image_macro_running:
        image_macro_running = False
    else:
        image_macro_running = True
        threading.Thread(target=image_macro, args=(hwnd, template_path), daemon=True).start()
    update_gui()

# GUI 업데이트
def update_gui():
    """GUI 상태 업데이트"""
    image_status = "실행" if image_macro_running else "중지"
    moving_status = "실행" if moving_macro_running else "중지"
    custom_status = "실행" if custom_macro_running else "중지"

    image_label.config(text=f"[이미지 서치 매크로: 현재 상태 ({image_status})]")
    moving_label.config(text=f"[무빙혼힐 매크로: 현재 상태 ({moving_status})]")
    custom_label.config(text=f"[사용자 지정 매크로: 현재 상태 ({custom_status})]")

# GUI 생성
def create_gui():
    """GUI 생성"""
    global image_label, moving_label, custom_label

    # 창 이름 입력
    window_title = simpledialog.askstring("창 이름 입력", "매크로를 실행할 창 이름을 입력하세요:")
    if not window_title:
        messagebox.showerror("오류", "창 이름이 입력되지 않았습니다.")
        return

    try:
        hwnd = find_window(window_title)
    except Exception as e:
        messagebox.showerror("오류", str(e))
        return

    root = tk.Tk()
    root.title("매크로 관리자")

    image_label = tk.Label(root, text="[이미지 서치 매크로: 현재 상태 (중지)]", font=("Arial", 12))
    image_label.pack(pady=10)

    moving_label = tk.Label(root, text="[무빙혼힐 매크로: 현재 상태 (중지)]", font=("Arial", 12))
    moving_label.pack(pady=10)

    custom_label = tk.Label(root, text="[사용자 지정 매크로: 현재 상태 (중지)]", font=("Arial", 12))
    custom_label.pack(pady=10)

    # 버튼
    tk.Button(root, text="이미지 서치 매크로 시작/중지", command=lambda: start_stop_image_macro(hwnd, "./img/emerald.png")).pack(pady=5)
    tk.Button(root, text="무빙혼힐 매크로 시작/중지", command=lambda: start_stop_moving_macro(hwnd)).pack(pady=5)
    tk.Button(root, text="사용자 지정 매크로 시작/중지", command=lambda: start_stop_custom_macro(hwnd)).pack(pady=5)

    root.mainloop()

# 프로그램 실행
if __name__ == "__main__":
    create_gui()
    save_settings()
