#!/usr/bin/env python3

from neopixel import *
from time import sleep
from random import randint
from argparse import ArgumentParser

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

    def __init__(self, color=(90,0,200), color_cycle=False, num_souls=1, base_color=(5,0,10), offset=10):

        # Create NeoPixel object with appropriate configuration.
        self.strip          = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.usable         = list(range(offset, LED_COUNT))
        self.souls          = [Soul(self.strip, self.usable, color=color, base_color=base_color) for s in range(num_souls)]
        self.offset         = offset
        self.bright_color   = color
        self.base_color     = base_color

        self._color_cycle    = color_cycle

        self._stop          = False


    def run(self):

        # Intialize the library (must be called once before other functions).
        self.strip.begin()

        self.clear()

        if self._color_cycle:
            self.color_cycle()
        else:
            self.soul_dance()


    def color_cycle(self):

        while not self._stop:
            for j in range(128):
                for i in range(self.strip.numPixels())[self.offset:]:
                    self.strip.setPixelColor(i, self.wheel((i+j) & 127))
                self.strip.show()
                sleep(.1)

            sleep(randint(1,2000) / 2000)
    

    def soul_dance(self):

        # set all pixels to base color
        for i in range(self.strip.numPixels())[self.offset:]:
            self.strip.setPixelColor(i, Color(*self.base_color))
        self.strip.show()

        # loop infinitely
        while not self._stop:
            for soul in self.souls:
                roll = randint(0,5)
                if roll == 0:
                    soul.dart()
                else:
                    soul.float()


    def wheel(self, pos, variation=10):

        half = int(variation / 2)
        divisor = 64 / variation

        base_red = self.bright_color[0] / 3
        base_blue = self.bright_color[2] / 3

        if pos < 64:

            red = base_red-half + (variation - int(pos/divisor))
            blue = base_blue+half - (variation - int(pos/divisor))
            return Color(*validate([red, 0, blue]))

        else:

            pos = min(255, max(0, pos - 64))
            red = base_red+half - (variation - int(pos/divisor))
            blue = base_blue-half + (variation - int(pos/divisor))
            return Color(*validate([red, 0, blue]))


    def stop(self):

        self._stop = True
        self.clear()


    def clear(self):

        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0,0,0))
        self.strip.show()




class Soul():

    def __init__(self, strip, usable, color, base_color=(0,0,0), color_variation=5, circumference=5):

        self.strip              = strip
        self.usable             = usable
        self.color              = color
        self.base_color         = base_color
        self.color_variation    = color_variation
        self.circ               = circumference
        self.cur_pixel          = randint(0, strip.numPixels())


    def float(self, ms=4000):

        self.move_random(ms=ms)


    def dart(self, length=2, ms=1000):
        
        for i in range(length):
            self.move_random(ms=ms)


    def move_random(self, ms=1000):

        new_pixel = self._get_random_nearby()
        while new_pixel == self.cur_pixel:
            new_pixel = self._get_random_nearby()

        new_color = self.shift_color()

        pixelFade(self.strip, self.cur_pixel, new_pixel, new_color, self.base_color, ms)
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
        except [ValueError, IndexError]:
            return nearby[0]

        return new_pixel


    def _get_nearby(self):

        nearby = []

        for i in [self.cur_pixel-self.circ, self.cur_pixel, self.cur_pixel+self.circ]:

            adjacent = [i-1, i, i+1]
            for a in adjacent:
                if a in self.usable and a not in nearby and a != self.cur_pixel:
                    nearby.append(a)

        return nearby



def pixelFade(strip, pixel1, pixel2, new_color, base_color, ms=500, num_steps=80):

    step_ms = ms / num_steps

    p1_color = [c for c in new_color]
    p2_color = [c for c in base_color]

    steps = []
    for n in range(1, num_steps+1):
        step = []
        for c in range(3):
            step.append( base_color[c] + ((p1_color[c] - p2_color[c]) / num_steps) * n )
        steps.append(step)


    for step in range(len(steps)):

        p1_color = validate(steps[-(step+1)])
        p2_color = validate(steps[step])

        strip.setPixelColor(pixel1, Color(*p1_color))
        strip.setPixelColor(pixel2, Color(*p2_color))

        strip.show()
        sleep(step_ms / 1000.0)

    strip.setPixelColor(pixel1, Color(*base_color))
    strip.setPixelColor(pixel2, Color(*new_color))
    strip.show()



def validate(precise_color):

    return [min(255, max(0, int(c))) for c in precise_color]




if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-c', '--color-cycle', action='store_true', help="Simple color cycle")
    parser.add_argument('-s', '--soul-dance', action='store_true', help="Small light that slowly moves around (default)")

    options = parser.parse_args()

    try:

        print ('Press Ctrl-C to quit.')

        soulgem = SoulGem(color_cycle=options.color_cycle)
        soulgem.run()

    except KeyboardInterrupt:
        print('[+] Stopping...')

    finally:
        soulgem.stop()
            