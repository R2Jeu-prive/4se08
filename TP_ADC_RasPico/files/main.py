import time

from machine import ADC, Pin, Timer

SAMPLE_RATE_HZ = 100
SAMPLE_PERIOD_MS = 1000 // SAMPLE_RATE_HZ
BUFFER_PERIOD_MS = 4000
BUFFER_SAMPLE_COUNT = BUFFER_PERIOD_MS // SAMPLE_PERIOD_MS

VARIANCE_WINDOW_SIZE = 5
VARIANCE_TRIGGER_THRESHOLD = 10

led = Pin(25, Pin.OUT)
adc = ADC(Pin(26, mode=Pin.IN))

raw_buffer = [0] * BUFFER_SAMPLE_COUNT
bpm_buffer = [0.0] * VARIANCE_WINDOW_SIZE
time_buffer = [time.ticks_us()] * VARIANCE_WINDOW_SIZE


def adc_handler(_):
    raw_buffer.append(adc.read_u16())
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

    print(f"BPM: {bpm_buffer[-1]} ({var:.2f})")


if __name__ == "__main__":
    adc_timer = Timer(
        mode=Timer.PERIODIC, period=SAMPLE_PERIOD_MS, callback=adc_handler
    )

    while True:
        compute_handler(None)
