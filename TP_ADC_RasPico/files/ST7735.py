from machine import Pin,SPI,PWM
import time
import framebuf

class LCD_0inch96(framebuf.FrameBuffer):
    def __init__(self):
    
        self.width = 160
        self.height = 80
        
        self.cs = Pin(9,Pin.OUT)
        self.rst = Pin(12,Pin.OUT)
#        self.bl = Pin(13,Pin.OUT)
        self.cs(1)
        # pwm = PWM(Pin(13))#BL
        # pwm.freq(1000)        
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,10000_000,polarity=0, phase=0,sck=Pin(10),mosi=Pin(11),miso=None)
        self.dc = Pin(8,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.Init()
        self.SetWindows(0, 0, self.width-1, self.height-1)
        
    def reset(self):
        self.rst(1)
        time.sleep(0.2) 
        self.rst(0)
        time.sleep(0.2)         
        self.rst(1)
        time.sleep(0.2) 
        
    def write_cmd(self, cmd):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))

    def write_data(self, buf):
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def backlight(self,value):#value:  min:0  max:1000
        pwm = PWM(Pin(13))#BL
        pwm.freq(1000)
        if value>=1000:
            value=1000
        data=int (value*65536/1000)       
        pwm.duty_u16(data)  
        
    def Init(self):
        self.reset() 
        self.backlight(10000)  
        
        self.write_cmd(0x11)
        time.sleep(0.12)
        self.write_cmd(0x21) 
        self.write_cmd(0x21) 

        self.write_cmd(0xB1) 
        self.write_data(0x05)
        self.write_data(0x3A)
        self.write_data(0x3A)

        self.write_cmd(0xB2)
        self.write_data(0x05)
        self.write_data(0x3A)
        self.write_data(0x3A)

        self.write_cmd(0xB3) 
        self.write_data(0x05)  
        self.write_data(0x3A)
        self.write_data(0x3A)
        self.write_data(0x05)
        self.write_data(0x3A)
        self.write_data(0x3A)

        self.write_cmd(0xB4)
        self.write_data(0x03)

        self.write_cmd(0xC0)
        self.write_data(0x62)
        self.write_data(0x02)
        self.write_data(0x04)

        self.write_cmd(0xC1)
        self.write_data(0xC0)

        self.write_cmd(0xC2)
        self.write_data(0x0D)
        self.write_data(0x00)

        self.write_cmd(0xC3)
        self.write_data(0x8D)
        self.write_data(0x6A)   

        self.write_cmd(0xC4)
        self.write_data(0x8D) 
        self.write_data(0xEE) 

        self.write_cmd(0xC5)
        self.write_data(0x0E)    

        self.write_cmd(0xE0)
        self.write_data(0x10)
        self.write_data(0x0E)
        self.write_data(0x02)
        self.write_data(0x03)
        self.write_data(0x0E)
        self.write_data(0x07)
        self.write_data(0x02)
        self.write_data(0x07)
        self.write_data(0x0A)
        self.write_data(0x12)
        self.write_data(0x27)
        self.write_data(0x37)
        self.write_data(0x00)
        self.write_data(0x0D)
        self.write_data(0x0E)
        self.write_data(0x10)

        self.write_cmd(0xE1)
        self.write_data(0x10)
        self.write_data(0x0E)
        self.write_data(0x03)
        self.write_data(0x03)
        self.write_data(0x0F)
        self.write_data(0x06)
        self.write_data(0x02)
        self.write_data(0x08)
        self.write_data(0x0A)
        self.write_data(0x13)
        self.write_data(0x26)
        self.write_data(0x36)
        self.write_data(0x00)
        self.write_data(0x0D)
        self.write_data(0x0E)
        self.write_data(0x10)

        self.write_cmd(0x3A) 
        self.write_data(0x05)

        self.write_cmd(0x36)
        self.write_data(0xA8)

        self.write_cmd(0x29) 
        
    def SetWindows(self, Xstart, Ystart, Xend, Yend):#example max:0,0,159,79
        Xstart=Xstart+1
        Xend=Xend+1
        Ystart=Ystart+26
        Yend=Yend+26
        self.write_cmd(0x2A)
        self.write_data(0x00)              
        self.write_data(Xstart)      
        self.write_data(0x00)              
        self.write_data(Xend) 

        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(Ystart)
        self.write_data(0x00)
        self.write_data(Yend)

        self.write_cmd(0x2C) 
        
    def display(self):
    
        self.SetWindows(0,0,self.width-1,self.height-1)       
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)        

    def _reverse(self, s: string) -> string:
        t = ""
        for i in range(0, len(s)):
            t += s[len(s) - 1 - i]
        return t

    def large_text(self, s, x, y, m, c: int = 1, r: int = 0, t=None):
        """
        large text drawing function uses the standard framebuffer font (8x8 pixel characters)
        writes text, s,
        to co-cordinates x, y
        size multiple, m (integer, eg: 1,2,3,4. a value of 2 produces 16x16 pixel characters)
        colour, c [optional parameter, default value c=1]
        optional parameter, r is rotation of the text: 0, 90, 180, or 270 degrees
        optional parameter, t is rotation of each character within the text: 0, 90, 180, or 270 degrees
        """
        colour = c
        smallbuffer = bytearray(8)
        letter = framebuf.FrameBuffer(smallbuffer, 8, 8, framebuf.MONO_HMSB)
        r = r % 360 // 90
        dx = 8 * m if r in (0, 2) else 0
        dy = 8 * m if r in (1, 3) else 0
        if r in (2, 3):
            s = self._reverse(s)
        t = r if t is None else t % 360 // 90
        a, b, c, d = 1, 0, 0, 1
        for i in range(0, t):
            a, b, c, d = c, d, -a, -b
        x0 = 0 if a + c > 0 else 7
        y0 = 0 if b + d > 0 else 7
        for character in s:
            letter.fill(0)
            letter.text(character, 0, 0, 1)
            for i in range(0, 8):
                for j in range(0, 8):
                    if letter.pixel(i, j) == 1:
                        p = x0 + a * i + c * j
                        q = y0 + b * i + d * j
                        if m == 1:
                            self.pixel(x + p, y + q, colour)
                        else:
                            self.fill_rect(x + p * m, y + q * m, m, m, colour)
            x += dx
            y += dy

    def circle(self, x0, y0, radius, c, f: bool = None):
        """
        Circle drawing function.  Will draw a single pixel wide circle with
        center at x0, y0 and the specified radius
        colour c
        fill if f is True
        """
        if f is None or f != True:
            g = 1 - radius
            ddG_x = 1
            ddG_y = -2 * radius
            x = 0
            y = radius
            self.pixel(x0, y0 + radius, c)
            self.pixel(x0, y0 - radius, c)
            self.pixel(x0 + radius, y0, c)
            self.pixel(x0 - radius, y0, c)
            while x < y:
                if g >= 0:
                    y -= 1
                    ddG_y += 2
                    g += ddG_y
                x += 1
                ddG_x += 2
                g += ddG_x
                self.pixel(x0 + x, y0 + y, c)
                self.pixel(x0 - x, y0 + y, c)
                self.pixel(x0 + x, y0 - y, c)
                self.pixel(x0 - x, y0 - y, c)
                self.pixel(x0 + y, y0 + x, c)
                self.pixel(x0 - y, y0 + x, c)
                self.pixel(x0 + y, y0 - x, c)
                self.pixel(x0 - y, y0 - x, c)
        else:
            self.vline(x0, y0 - radius, 2 * radius + 1, c)
            g = 1 - radius
            ddG_x = 1
            ddG_y = -2 * radius
            x = 0
            y = radius
            while x < y:
                if g >= 0:
                    y -= 1
                    ddG_y += 2
                    g += ddG_y
                x += 1
                ddG_x += 2
                g += ddG_x
                self.vline(x0 + x, y0 - y, 2 * y + 1, c)
                self.vline(x0 + y, y0 - x, 2 * x + 1, c)
                self.vline(x0 - x, y0 - y, 2 * y + 1, c)
                self.vline(x0 - y, y0 - x, 2 * x + 1, c)

    def triangle(self, x0, y0, x1, y1, x2, y2, c, f: bool = None):
        """
        Triangle drawing function.  Will draw a single pixel wide triangle
        around the points (x0, y0), (x1, y1), and (x2, y2)
        colour c
        fill if f is True
        """
        if f is None or f != True:
            self.line(x0, y0, x1, y1, c)
            self.line(x1, y1, x2, y2, c)
            self.line(x2, y2, x0, y0, c)
        else:
            if y0 > y1:
                y0, y1 = y1, y0
                x0, x1 = x1, x0
            if y1 > y2:
                y2, y1 = y1, y2
                x2, x1 = x1, x2
            if y0 > y1:
                y0, y1 = y1, y0
                x0, x1 = x1, x0
            a = 0
            b = 0
            last = 0
            if y0 == y2:
                a = x0
                b = x0
                if x1 < a:
                    a = x1
                elif x1 > b:
                    b = x1
                if x2 < a:
                    a = x2
                elif x2 > b:
                    b = x2
                self.hline(a, y0, b - a + 1, c)
                return
            dx01 = x1 - x0
            dy01 = y1 - y0
            dx02 = x2 - x0
            dy02 = y2 - y0
            dx12 = x2 - x1
            dy12 = y2 - y1
            if dy01 == 0:
                dy01 = 1
            if dy02 == 0:
                dy02 = 1
            if dy12 == 0:
                dy12 = 1
            sa = 0
            sb = 0
            y = y0
            if y0 == y1:
                last = y1 - 1
            else:
                last = y1
            while y <= last:
                a = x0 + sa // dy01
                b = x0 + sb // dy02
                sa += dx01
                sb += dx02
                if a > b:
                    a, b = b, a
                self.hline(a, y, b - a + 1, c)
                y += 1
            sa = dx12 * (y - y1)
            sb = dx02 * (y - y0)
            while y <= y2:
                a = x1 + sa // dy12
                b = x0 + sb // dy02
                sa += dx12
                sb += dx02
                if a > b:
                    a, b = b, a
                self.hline(a, y, b - a + 1, c)
                y += 1        
 
