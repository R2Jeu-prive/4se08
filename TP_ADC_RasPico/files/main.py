from machine import Timer , Pin , ADC

SAMPLE_RATE_HZ = 100
SAMPLE_PERIOD_MS = 1000 // SAMPLE_RATE_HZ
BUFFER_PERIOD_MS = 4000
BUFFER_SAMPLE_COUNT = BUFFER_PERIOD_MS // SAMPLE_PERIOD_MS
led = Pin(25, Pin.OUT)
adc = ADC(Pin(26 , mode=Pin.IN))

raw_buffer = [0] * BUFFER_SAMPLE_COUNT


def adc_handler(_):
    raw_buffer.append(adc.read_u16())
    raw_buffer.pop(0)
    #print(adc.read_u16())

def pierrecorrelation(buffer: list[float]) -> list[float]:
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
            return i
    return -1


def offset_to_bpm(offset: int, sample_rate: float) -> float:
    if offset <= 0:
        return 0.0
    period = offset / sample_rate  # in seconds
    bpm = 60.0 / period
    return bpm

def compute_handler(_):
    frozen_buffer = raw_buffer.copy()
    corr = pierrecorrelation(frozen_buffer)
    min_offest = first_minimum_index(corr)
    bpm = offset_to_bpm(min_offest, sample_rate=SAMPLE_RATE_HZ)
    print("BPM: ", bpm)

if __name__ == "__main__":
    adc_timer = Timer(
        mode=Timer.PERIODIC,
        period=SAMPLE_PERIOD_MS,
        callback=adc_handler
    )

    while True:
        compute_handler(None)
