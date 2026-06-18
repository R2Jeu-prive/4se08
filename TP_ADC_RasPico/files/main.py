from machine import Pin,SPI,PWM,Timer, Pin, ADC
from ST7735 import LCD_0inch96
import framebuf
import time

#color is BGR
RED = 0x00F8
GREEN = 0xE007
BLUE = 0x1F00
WHITE = 0xFFFF
BLACK = 0x0000

SAMPLE_RATE_HZ = 100
SAMPLE_PERIOD_MS = 1000 // SAMPLE_RATE_HZ
BUFFER_PERIOD_MS = 2000
BUFFER_SAMPLE_COUNT = BUFFER_PERIOD_MS // SAMPLE_PERIOD_MS

VARIANCE_WINDOW_SIZE = 5
VARIANCE_TRIGGER_THRESHOLD = 1

adc = ADC(Pin(26, mode=Pin.IN))

raw_buffer = [0] * BUFFER_SAMPLE_COUNT
bpm_buffer = [0.0] * VARIANCE_WINDOW_SIZE
time_buffer = [time.ticks_us()] * VARIANCE_WINDOW_SIZE

screen_scan_progress = 0

def adc_handler(_):
    global lcd, screen_scan_progress
    raw_buffer.append(adc.read_u16())

    min_pixel = 52
    max_pixel = 76
    min_adc = 35_000
    max_adc = 45_000

    previous_t = (raw_buffer[-1-12] - min_adc) / (max_adc - min_adc)
    previous_t = max(0.0, min(1.0, previous_t))
    previous_pixel_value = int(min_pixel + (1-previous_t) * (max_pixel - min_pixel))
    t = (raw_buffer[-1] - min_adc) / (max_adc - min_adc)
    t = max(0.0, min(1.0, t))
    pixel_value = int(min_pixel + (1-t) * (max_pixel - min_pixel))
    
    screen_scan_progress += 1
    if screen_scan_progress % 12 == 0:
        lcd.line((screen_scan_progress // 3) - 4, previous_pixel_value, screen_scan_progress // 3, pixel_value, RED)
        lcd.display()
    
    if screen_scan_progress >= 3 * 160:
        screen_scan_progress = 0
        lcd.rect(0, 48, 160, 32, BLACK, True)
        lcd.display()

    raw_buffer.pop(0)
    # print(adc.read_u16())


def pierrecorrelation(buffer: list[int]) -> list[float]:
    output = []

    for offset in range(0, len(buffer)):
        total_diff = 0
        for i in range(offset, len(buffer)):
            total_diff += abs(buffer[i] - buffer[i - offset])
            # total_diff += (buffer[i] - buffer[i - offset]) ** 2
        total_diff /= len(buffer) - offset
        output.append(total_diff)

    return output


def first_minimum_index(ys: list[float]) -> int:
    for i in range(1, len(ys) - 1):
        if ys[i - 1] > ys[i] and ys[i] < ys[i + 1]:
            if i >= 15 and all(ys[j] > ys[j + 1] for j in range(i - 20, i)):
                return i
    return -1


def offset_to_bpm(offset: int, sample_rate: float) -> float:
    if offset <= 0:
        return 0.0
    period = offset / sample_rate  # in seconds
    bpm = 60.0 / period
    return bpm


def push_bpm(bpm):
    bpm_buffer.append(bpm)
    bpm_buffer.pop(0)


def push_time(time):
    time_buffer.append(time)
    time_buffer.pop(0)


def full_deltatime() -> int:
    return time.ticks_diff(time_buffer[-1], time_buffer[0]) * 10e-6


def calculate_variance(buffer: list[float]) -> float:
    mean = sum(buffer) / len(buffer)
    variance = sum((x - mean) ** 2 for x in buffer) / len(buffer)
    variance /= full_deltatime()
    return variance


triggered = 0


def compute_handler(_):
    global triggered

    push_time(time.ticks_us())

    frozen_buffer = raw_buffer.copy()
    corr = pierrecorrelation(frozen_buffer)
    min_offest = first_minimum_index(corr)
    bpm = offset_to_bpm(min_offest, sample_rate=SAMPLE_RATE_HZ)

    push_bpm(bpm)
    var = calculate_variance(bpm_buffer)
    if var >= VARIANCE_TRIGGER_THRESHOLD and triggered == 0:
        print(f"Correction de {bpm_buffer[-1]} en {bpm_buffer[-2]}")
        bpm_buffer[-1] = bpm_buffer[-2]
        triggered = VARIANCE_WINDOW_SIZE
    else:
        triggered = max(0, triggered - 1)

    lcd.rect(0, 13, 160, 32, BLACK, True)
    if bpm_buffer[-1] < 10:
        lcd.large_text(str(int(bpm_buffer[-1])), 64, 16, 4, GREEN)
    elif bpm_buffer[-1] < 100:
        lcd.large_text(str(int(bpm_buffer[-1])), 48, 16, 4, GREEN)
    else:
        lcd.large_text(str(int(bpm_buffer[-1])), 32, 16, 4, GREEN)
    lcd.display()
    print(f"BPM: {bpm_buffer[-1]} ({var:.2f})")


if __name__ == "__main__":
    print("Starting BPM detection...")
    lcd = LCD_0inch96()   #Initializing the screen
    lcd.fill(BLACK)       #clearing any exsiting diplay
    adc_timer = Timer(
        mode=Timer.PERIODIC, period=SAMPLE_PERIOD_MS, callback=adc_handler
    )
    while True:
        compute_handler(lcd)
