from machine import Timer , Pin , ADC

SAMPLE_RATE_HZ = 100
SAMPLE_PERIOD_MS = 1000 // SAMPLE_RATE_HZ
led = Pin(25, Pin.OUT)
adc = ADC(Pin(26 , mode=Pin.IN))

def adc_handler(_):
    print(adc.read_u16())

if __name__ == "__main__":
    adc_timer = Timer(
        mode=Timer.PERIODIC,
        period=SAMPLE_PERIOD_MS,
        callback=adc_handler
    )
