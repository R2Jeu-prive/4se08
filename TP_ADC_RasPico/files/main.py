from machine import Timer , Pin , ADC

SAMPLE_RATE_HZ = 500
SAMPLE_PERIOD_MS = 1000 // SAMPLE_RATE_HZ
WINDOW_PERIOD_MS = 2048
WINDOW_SAMPLE_COUNT = WINDOW_PERIOD_MS // SAMPLE_PERIOD_MS
BPM_TO_HZ = 1 / 60
led = Pin(25, Pin.OUT)
adc = ADC(Pin(26 , mode=Pin.IN))

raw_buffer = [0] * WINDOW_SAMPLE_COUNT

def adc_handler(_):
    raw_buffer.append(adc.read_u16())
    raw_buffer.pop(0)
    #print(adc.read_u16())

def compute_handler(_):

    min_sample = min(raw_buffer)
    max_sample = max(raw_buffer)
    threshold = (min_sample + max_sample) // 2

    rising_edges = []

    for i in range(WINDOW_SAMPLE_COUNT - 1):
        if raw_buffer[i] < threshold and raw_buffer[i + 1] >= threshold:
            rising_edges.append(i)
    
    nb_rising_edges = len(rising_edges)
    if nb_rising_edges < 2:
        return

    current_rising_edge_index = 0
    next_rising_edge_index = 1

    while next_rising_edge_index < nb_rising_edges:
        period_samples = rising_edges[next_rising_edge_index] - rising_edges[current_rising_edge_index]
        bpm = 30_000 // period_samples
        if bpm >= 50 and bpm < 200:
            print("BPM:", bpm)
            current_rising_edge_index = next_rising_edge_index
            next_rising_edge_index = current_rising_edge_index + 1
        else:
            next_rising_edge_index += 1

if __name__ == "__main__":
    adc_timer = Timer(
        mode=Timer.PERIODIC,
        period=SAMPLE_PERIOD_MS,
        callback=adc_handler
    )

    compute_timer = Timer(
        mode=Timer.PERIODIC,
        period=WINDOW_PERIOD_MS//8,
        callback=compute_handler
    )
