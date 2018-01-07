#!/usr/bin/env python3

from neopixel import *
from time import sleep
from random import randint

# LED strip configuration:
LED_COUNT      = 60      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


class SoulGem():

    def __init__(self, color=(70,0,150), num_souls=1, offset=10):

        # Create NeoPixel object with appropriate configuration.
        self.strip      = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.usable     = list(range(offset, LED_COUNT))
        self.souls      = [Soul(self.strip, self.usable, color=color) for s in range(num_souls)]


    def run(self):

        # Intialize the library (must be called once before other functions).
        self.strip.begin()

        self.clear()

        while 1:
            for soul in self.souls:
                roll = randint(0,6)
                if roll == 0:
                    soul.dart()
                else:
                    soul.float()


    def stop(self):

        self.clear()


        
    def clear(self):

        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0,0,0))
        self.strip.show()




class Soul():

    def __init__(self, strip, usable, color, color_variation=5, circumference=5):

        self.strip              = strip
        self.usable             = usable
        self.color              = color
        self.color_variation    = color_variation
        self.circ               = circumference
        self.cur_pixel          = randint(0, strip.numPixels())


    def float(self, ms=5000):

        self.move_random(ms=ms)


    def dart(self, length=3, ms=750):
        
        for i in range(length):
            self.move_random(ms=ms)


    def move_random(self, ms=1000):

        new_pixel = self._get_random_nearby()
        while new_pixel == self.cur_pixel:
            new_pixel = self._get_random_nearby()

        new_color = self.shift_color()

        pixelFade(self.strip, self.cur_pixel, new_pixel, new_color, ms)
        self.cur_pixel = new_pixel


    def shift_color(self):

        new_color = [0,0,0]
        for c in range(3):
            new_color[c] = min(255, max(1, self.color[c] + randint(-self.color_variation,self.color_variation)))

        #print(new_color)
        return new_color



    def _get_random_nearby(self):

        #print('usable: {}'.format(str(self.usable)))
        nearby = self._get_nearby()
        #print('nearby: {}'.format(str(nearby)))
        try:
            new_pixel = nearby[randint(0, len(nearby)-1)]
        except ValueError:
            return nearby[0]

        return new_pixel


    def _get_nearby(self):

        nearby = []

        c = 0
        for i in [self.cur_pixel-self.circ, self.cur_pixel, self.cur_pixel+self.circ]:
            if c == 0 and randint(0,5) == 0:
                c += 1
                continue

            adjacent = [i-1, i, i+1]
            for a in adjacent:
                if a in self.usable and a not in nearby and a != self.cur_pixel:
                    nearby.append(a)

            c += 1

        return nearby




def theLonelyPixel(strip, color, wait_ms=50, reverse=False):

    old_pixel = 0

    for i in range(strip.numPixels() - 1):

        if reverse:
            i = strip.numPixels() - i

        # black out
        for j in range(strip.numPixels()):
            strip.setPixelColor(j, Color(0,0,0))

        strip.setPixelColor(i, color)
        strip.show()
        sleep(wait_ms/1000.0)


def getColor(strip, pixel):

    color = strip.getPixelColor(pixel)

    r = color & 0xFF0000 >> 16
    g = color & 0x00FF00 >> 8
    b = color & 0x0000FF

    assert all( [c >= 0 and c <= 255 for c in (r,g,b)] )

    return [r,g,b]


def pixelFade(strip, pixel1, pixel2, color, ms=1000, num_steps=60):

    step_ms = ms / num_steps

    p1_color = [c for c in color]
    #p1_color = getColor(strip, pixel1)
    #print('p1 color: {}'.format(str(p1_color)))
    p2_color = [0,0,0]

    #small_step = tuple( [ max(0.0, min(255.0, (c / num_steps) / 5)) for c in color ] )
    #large_step = tuple( [ max(0.0, min(255.0, c / num_steps)) for c in color ] )
    #print(small_step)
    #print(large_step)

    #print('fade start')

    for i in range(1, num_steps+1):

        multiplier = i / num_steps

        #print('fade {}'.format(i))

        p1_color = dim(color, multiplier)
        p2_color = brighten(color, multiplier)

        strip.setPixelColor(pixel1, Color(*p1_color))
        strip.setPixelColor(pixel2, Color(*p2_color))
        strip.show()
        sleep(step_ms / 1000.0)

    #print('fade finish')



def pixelTraverse(strip, color):

    for i in range(28, strip.numPixels()):
        pixelFade(strip, i, i+1, color)
    for i in range(0, 28):
        pixelFade(strip, strip.numPixels() - i, strip.numPixels() - i - 1, color)



def fadeCycle(strip, pixel, color, num_steps=20, wait_ms=200):

    step = tuple( [ max(0.0, min(255.0, c / num_steps)) for c in color ] )
    
    fading = [0,0,0]
    strip.setPixelColor(pixel, Color(0,0,0))
    for i in range(num_steps):
        brighten(fading, step)
        strip.setPixelColor(pixel, Color(*fading))
        strip.show()
        sleep(wait_ms / 1000.0)

    fading = [c for c in color]
    strip.setPixelColor(pixel, Color(*color))
    for i in range(num_steps):
        dim(fading, step)
        strip.setPixelColor(pixel, Color(*fading))
        strip.show()
        sleep(wait_ms / 1000.0)


def dim(color, multiplier):

    multiplier = 1 - multiplier

    new_color = [0,0,0]

    for c in range(3):
        new_color[c] = max(0, min(255, int(multiplier * color[c])))

    return new_color


def brighten(color, multiplier):

    new_color = [0,0,0]

    for c in range(3):
        new_color[c] = max(0, min(255, int(multiplier * color[c])))

    return new_color


'''
def dim_pixel(strip, pixel, color, percent):

    percent = (100 - percent) / 100.0
    new_color = tuple( [ max(0, min(255, int(c * percent))) for c in color ] )
    strip.setPixelColor(pixel, Color(*new_color))
    return new_color



def brighten_pixel(strip, pixel, color, percent):

    percent = (100 + percent) / 100.0
    new_color = tuple( [ max(0, min(255, int(c * percent))) for c in color ] )
    strip.setPixelColor(pixel, Color(*new_color))
    return new_color
'''


if __name__ == '__main__':

    try:

        print ('Press Ctrl-C to quit.')
        '''
        strip       = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        strip.begin()
        while True:
            pixelTraverse(strip, (100, 0, 255))
        '''

        soulgem = SoulGem()
        soulgem.run()

    except KeyboardInterrupt:
        '''
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0,0,0))
        strip.show()
        '''
        soulgem.stop()
            