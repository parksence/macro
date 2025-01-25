import pymem
import pymem.process

process_name = "msw.exe"

def find_dynamic_address(pm, base_address, search_range=(0x00000000, 0x7FFFFFFF), value_type="float", expected_value=None):
    """
    메모리를 스캔하여 동적 주소를 찾는 함수.
    - pm: Pymem 객체
    - base_address: 베이스 주소
    - search_range: 검색 범위
    - value_type: 검색 값 유형 (float, int 등)
    - expected_value: 검색할 예상 값
    """
    start, end = search_range
    current_address = base_address + start

    while current_address < base_address + end:
        try:
            # 지정된 데이터 유형에 따라 값 읽기
            if value_type == "float":
                value = pm.read_float(current_address)
            elif value_type == "int":
                value = pm.read_int(current_address)
            else:
                raise ValueError("Unsupported value type.")

            # 값이 예상 값과 일치하면 주소 반환
            if expected_value is not None and value == expected_value:
                return current_address

            # 디버그 출력 (필요하면 활성화)
            # print(f"Address: {hex(current_address)}, Value: {value}")

        except:
            pass  # 읽기 불가능한 메모리 구간 무시

        # 다음 메모리 주소로 이동
        current_address += 4  # 데이터 타입 크기에 따라 조정 (float: 4 bytes, int: 4 bytes)

    return None  # 검색 실패


try:
    # 프로세스 연결
    pm = pymem.Pymem(process_name)
    print(f"프로세스 '{process_name}'에 연결되었습니다.")

    # 베이스 주소 가져오기
    base_address = pymem.process.module_from_name(pm.process_handle, process_name).lpBaseOfDll
    print(f"베이스 주소: {hex(base_address)}")

    # 예상 x 좌표 (Cheat Engine에서 확인한 초기 값 입력)
    initial_x = 100.0  # 예시 값
    initial_y = 200.0  # 예시 값

    # x 좌표의 메모리 주소 검색
    x_address = find_dynamic_address(pm, base_address, value_type="float", expected_value=initial_x)
    y_address = find_dynamic_address(pm, base_address, value_type="float", expected_value=initial_y)

    if x_address and y_address:
        print(f"x 좌표 주소: {hex(x_address)}")
        print(f"y 좌표 주소: {hex(y_address)}")

        # 동적 주소에서 값 읽기
        x_value = pm.read_float(x_address)
        y_value = pm.read_float(y_address)
        print(f"현재 x 좌표: {x_value}, y 좌표: {y_value}")
    else:
        print("x, y 좌표를 찾을 수 없습니다.")

except pymem.exception.ProcessNotFound:
    print(f"프로세스 '{process_name}'를 찾을 수 없습니다.")
except Exception as e:
    print(f"오류 발생: {e}")