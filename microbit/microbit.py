"""
------------------------------------------------------------------------------
The MIT License (MIT)

Copyright (c) 2016 Newcastle University

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.import time

------------------------------------------------------------------------------
Author
Nick Cook, School of Computing Science, Newcastle University
------------------------------------------------------------------------------
Acknowledgement

This Python module is based on the microbit API defined as part of the BBC
microbit micropython project.

See: https://github.com/bbcmicrobit/micropython for the project repository and
licensing.

This project is an implementation of the API in order to test microbit Python
scripts without the need to execute them on the physical BBC microbit.

There is no assertion of copyright over the microbit API (represented by the
relevant class and function definitions, as opposed to their implementation).
------------------------------------------------------------------------------
"""
import array
import json
import random
import time

STATE_FILE_DEFAULT = 'microbit_state.json'
try:
    from microbit_settings import state_file
except ImportError:
    state_file = STATE_FILE_DEFAULT


__all__ = [ 'panic', 'reset', 'running_time', 'sleep', 
            'Accelerometer', 'accelerometer',
            'compass',
            'button_a', 'button_b',
            'display',
            'Image',
            'i2c',
            'pin0', 'pin1', 'pin2', 'pin3', 'pin4', 'pin5', 'pin6', 'pin7',
            'pin8', 'pin9', 'pin10', 'pin11', 'pin12', 'pin13', 'pin14',
            'pin15', 'pin16', 'pin19', 'pin20',
            'uart', 
            'state',
        ]


""" State ---------------------------------------------------------------- """
""" This is for the emulation not part of the microbit module ------------ """
class State:
    """Represents the state of the microbit buttons and pins.
    
    This is for emulation purposes - State is not part of the microbit API.
    There is a single state object. It is used to manage state during 
    emulation. It can also be used to programmatically manipulate microbit
    state in a test program.
    """
    __VALUE_MIN = 0
    __VALUE_MAX = 1023
    __RUNTIME_MAX_INCR = 100
    __STATE_FILE_KEY = 'state_file'
    __POWER_KEY = 'power'
    __ACCELEROMETER_KEYS = ['accelerometer_x','accelerometer_y',
                                'accelerometer_z']
    __PRESSES_KEYS = ['button_a_presses', 'button_b_presses']
    
    def __init__(self):
        self.__running_time = 0 # not part of persistent state
        self.__data = {
            "accelerometer_x": 0, 
            "accelerometer_y": 0, 
            "accelerometer_z": 0, 
            "button_a": 0, 
            "button_a_presses": 0,
            "button_b": 0,
            "button_b_presses": 0,
            "state_file": state_file,
            "pin0": 0,
            "pin1": 0,
            "pin2": 0,
            "pin3": 0,
            "pin4": 0,
            "pin5": 0,
            "pin6": 0,
            "pin7": 0,
            "pin8": 0,
            "pin9": 0,
            "pin10": 0,
            "pin11": 0,
            "pin12": 0,
            "pin13": 0,
            "pin14": 0,
            "pin15": 0,
            "pin16": 0,
            "pin19": 0,
            "pin20": 0,
            "power": 1
        }

        self.load()

    def __get_runtime(self):
        return self.__running_time
        
    def __incr_runtime(self, ms, randomise = False):
        if ms >= 0:
            if randomise:
                ms = random.randint(ms, State.__RUNTIME_MAX_INCR)
            
            self.__running_time = self.__running_time + ms
        
    def __valid_value(self, key, value):
        return key in State.__ACCELEROMETER_KEYS \
                or (value >= State.__VALUE_MIN \
                    and (key in State.__PRESSES_KEYS \
                            or value <= State.__VALUE_MAX))
        
    def get(self, key):
        """Returns the state associated with the named key. 
        
        The key string can be one of:
        accelerometer_x, accelerometer_z, accelerometer_y
        buton_a, button_a_presses, button_b, button_b_presses
        state_file,
        pin0 to pin16, pin19, pin20
        power
        
        If there is no state associated with the key, 0 is returned
        (note, 0 may be a valid value for the given key)

        This method is usually used through one of the corresponding, 
        higher-level microbit objects (e.g. accelerometer, button, etc.).        
        """
        return self.__data.get(key.lower(), State.__VALUE_MIN)
        
    def set(self, key, value):
        """Sets the state associated with the named key to the given value.
        
        The key string can be one of:
        accelerometer_x, accelerometer_z, accelerometer_y
        buton_a, button_a_presses, button_b, button_b_presses
        state_file,
        pin0 to pin16, pin19, pin20
        power
        
        This method has no effect if the key is unknown.   

        The value is checked for validity: state_file can have any value, 
        accelerometer values can be any integer, all other values must be
        positive and all but the button_presses values must be less than 
        or equal to 1023.
 
        This method is usually used through one of the corresponding, 
        higher-level microbit objects (e.g. accelerometer, button, etc.). 

        It can also be used to update state in a test program.    
        
        """
        key = key.lower()
        if key in self.__data:
            self.load()

            if key != State.__STATE_FILE_KEY:
                if not self.__valid_value(key, value):
                    raise ValueError(
                            'invalid value {0} for key {1}'.format(value, key))
                            
                value = int(value)

            self.__data[key] = value

            self.dump()

    def press(self, input):
        """Emulates pressing down on a button. 
        
        This method will set the value for the named input to 1 and 
        increment any associated presses counter.
        
        For a button press, the input can be either button_a or button_b. 
        If the input is another valid state key, this method will set the 
        associated value to 1.
        """
        presses = input + '_presses'
        self.set(input, 1)
        self.set(presses, self.get(presses) + 1)
        
    def release(self, input):
        """Emulates releasing a button. 
        
        This method will set the value for the named input to 0.
        
        For a button release, the input can be either button_a or button_b. 
        If the input is another valid state key, this method will set the 
        associated value to 0.
        """
        self.set(input, 0)
        
    def press_and_release(self, input, delay=50):
        """Emulates pressing then releasing the named input with the given
        millisecond delay following press and release.
        
        This method will set the value for the named input to 1 and then 
        to 0 with the given delay following both press and release.
        
        For a button, the input can be either button_a or button_b. 
        If the input is another valid state key, this method will set the 
        associated value to 1 then to 0.
        """
        self.press(input)
        sleep(delay)
        self.release(input)
        sleep(delay)
        
    def power_on(self):
        """Emulates switching power off (meaning there will be output to the 
        display).
        """
        self.set(State.__POWER_KEY, 1)
    
    def power_off(self):
        """Emulates switching power off (meaning there will be no output to
        display).
        
        Note: unlike the real microbit, "powering off" does not stop the
        microbit stub program running. It is more a way of "silencing" the
        microbit stub program during the tests.
        """
        self.__running_time = 0
        self.set(State.__POWER_KEY, 0)
        
    def is_on(self):
        """Returns True if power is on, False otherwise.
        """
        return self.get(State.__POWER_KEY) > 0
    
    def load(self):
        """Load state from the current json format state file.
        
        The state file name is initialised from a microbit_settings.py 
        file, if one exists. Otherwise the file microbit_state.json is used
        as the initial state file.

        Errors and exceptions during loading are ignored. This method has 
        no effect if the state file is empty, has an invalid format, does
        not exist etc.
        """
        try:
            with open(self.__data[State.__STATE_FILE_KEY]) as f:
                data = json.load(f)
                self.__data = data
        except:
            pass
    
    def dump(self):
        """Dump state to the current json format state file.
        
        The state file name is initialised from a microbit_settings.py 
        file, if one exists. Otherwise the file microbit_state.json is used
        as the initial state file.
        
        Errors and exceptions during dumping are ignored. This method has 
        no effect if the state file is empty, has an invalid format, does
        not exist etc.
        """
        try:
            with open(self.__data[State.__STATE_FILE_KEY], 'w') as f:
                json.dump(self.__data, f, sort_keys=True, indent=4,
                            ensure_ascii=False)
        except OSError:
            pass
                            
    def reset(self):
        """Reset all state values and dump to the current state file.
        
        Reset values are 0 keys except for power, which is reset to 1, and 
        state_file, which is set as the current state file name.
        """
        filename = self.__data[State.__STATE_FILE_KEY]
        self.__data = { k:0 for k in self.__data.keys() }
        self.__data[State.__STATE_FILE_KEY] = filename
        self.__data[State.__POWER_KEY] = 1
        self.dump()
        
    def __str__(self):
        return '\n'.join([str(k) + ':' \
                + str(self.__data[k]) for k in sorted(self.__data.keys())])

state = State()
    

""" ---------------------------------------------------------------------- """    
""" The microbit module emulation ---------------------------------------- """


""" ---------------------------------------------------------------------- """    
""" Buttons -------------------------------------------------------------- """
class Button:
    """Button class represents buttons A and B.
    
    There are 2 buttons:
    button_a
    button_b
    with methods to test whether a button has been pressed and how many times
    """

    def __init__(self, name=''):
        self.__prev_presses = 0
        self.name = name.lower()
        self.__presses_key = self.name + '_presses'

    def is_pressed(self):
        """If the button is pressed down, is_pressed() is True, else False.
        """
        return state.get(self.name) > 0
            
    def was_pressed(self):
        """True if the button was pressed since the last time was_pressed()
        was called, else False.
        """
        temp_presses = self.__prev_presses
        self.__prev_presses = self.get_presses()
        
        return self.__prev_presses > temp_presses
    
    def get_presses(self):
        """Returns the running total of button presses.
        """
        return state.get(self.__presses_key)
    
    def reset_presses(self):
        """Reset the running total of button presses to zero.
        """
        self.__prev_presses = 0
        self.__local_presses = 0
        state.set(self.__presses_key, 0)

button_a = Button('button_a')
button_b = Button('button_b')


""" ---------------------------------------------------------------------- """    
""" Images --------------------------------------------------------------- """
class Image:
    """Represents an image that can be displayed on the microbit screen.
    """
    __SEP = ':'
    __WIDTH_DEFAULT = 5
    __HEIGHT_DEFAULT = 5
    __PAD = '0'
    __PIX_MAX = 9
    __PIX_MIN = 0
        
    def __fromsize(args):
        width = args[0]
        height = args[1]
        
        if width < 0 or height < 0:
            raise ValueError('image is incorrect size')
        
        return [[Image.__PIX_MIN for x in range(width)] for y in range(height)]
        
    def __default(args):
        return Image.__fromsize([Image.__WIDTH_DEFAULT, Image.__HEIGHT_DEFAULT])
                                
    def __fromstring(args):
        s = args[0]
        if type(s) is not str:
            raise TypeError('Image(s) takes a string')
        
        if not s:
            return []
            
        t = s.replace(':', '')
        
        if not t:
            return Image.__default(args)
            
        if not t.isdigit():
            raise ValueError('Unexpected character in Image definition')
        
        rows = s.rstrip(Image.__SEP).split(Image.__SEP)
        width = max([len(r) for r in rows])

        return [[int(char) for char in r.ljust(width,Image.__PAD)] 
                                for r in rows]
    def __frombuffer(args):
        width = args[0]
        height = args[1]
        buffer = args[2]
        
        if buffer is None or type(buffer) is not array.array:
            raise TypeError('(array) object with buffer protocol required')
            
        if len(buffer) != width*height:
            raise ValueError('image data is incorrect size')
            
        if not buffer:
            return []

        if buffer.typecode != 'b' and buffer.typecode != 'B':
            raise ValueError('image data is incorrect size')
        
        return [[min(Image.__PIX_MAX, max(Image.__PIX_MIN, buffer[x])) 
                            for x in range(width*y, width*(y+1))] 
                            for y in range(height)]

    __CREATE_IMAGE = [__default, __fromstring, __fromsize, __frombuffer]
    
    def __init__(self, *args):
        """Initialise with a string s or a buffer of width x height pixels or 
        with a width and height.
        
        E.g.:
        Image('00000:11111:00000:11111:00000')
        Image(2, 2, array.array('b', [0,1,0,1])
        Image(3, 3)
        
        If no arguments are provided, initialise with 5x5 image of 0s
        """
        idx = len(args)
        
        if idx > 3:
            raise TypeError('function expected at most 3 arguments, got ' + l)
        
        self.__image = Image.__CREATE_IMAGE[idx](args)
        
    def width(self):
        """Returns the width of the image (usually 5).
        """
        return 0 if (not self.__image) else len(self.__image[0])
    
    def height(self):
        """Returns the height of the image (usually 5).
        """
        return len(self.__image)
        
    def set_pixel(self, x, y, value):
        """Set the pixel at position (x,y) to value.
        
        value must be between 0 and 9.
        """
        if y < 0 or x < 0:
            raise ValueError('index out of bounds')
            
        if value < Image.__PIX_MIN or value > Image.__PIX_MAX:
            raise ValueError('brightness out of bounds')
            
        self.__image[y][x] = value
    
    def get_pixel(self, x, y):
        """Return the value of the pixel at position (x, y).
        
        The value will be between 0 and 9.
        """
        if y < 0 or x < 0:
            raise ValueError('index out of bounds')
            
        return self.__image[y][x]

    def shift_left(self, n):
        """Returns a new image created by shifting the image left n times.
        """
        if n < 0:
            return self.shift_right(-n)
            
        width = self.width()
            
        img = Image(width, self.height())
        
        if n < width:
            img.__image = [row[n:len(row)] + [0 for i in range(n)] 
                            for row in self.__image]
        
        return img

    def shift_right(self, n):
        """Returns a new image created by shifting the image right n times.
        """
        if n < 0:
            return self.shift_left(-n)
            
        width = self.width()
            
        img = Image(width, self.height())
        
        if n < width:
            img.__image = [[0 for i in range(n)] + row[0:len(row)-n]  
                            for row in self.__image]
        
        return img

    def shift_up(self, n):
        """Returns a new image created by shifting the image up n times.
        """
        if n < 0:
            return self.shift_down(-n)
        
        width = self.width()
        height = self.height()
        
        img = Image(width, height)
        
        if n < height:
            img.__image = [[x for x in row] for row in self.__image[n:height]] \
                        + [[Image.__PIX_MIN for x in range(width)]
                            for y in range(n)]
                                            
        return img

    def shift_down(self, n):
        """Returns a new image created by shifting the image down n times.
        """
        if n < 0:
            return self.shift_up(-n)
        
        width = self.width()
        height = self.height()

        img = Image(width, height)
        
        if n < height:
            img.__image = [[Image.__PIX_MIN for x in range(width)]
                            for y in range(n)] \
                            + [[x for x in row] 
                                for row in self.__image[0:height-n]]
                                                                        
        return img

    def __repr__(self):
        """String representation that can be eval'ed to recreate image object.
        
        E.g.:
        Image('90009:09090:00900:09090:90009:')
        """
        
        if self.__image:
            return "Image('{0}:')".format(':'.join([''.join(str(r) for r in row) 
                                        for row in self.__image]))
        else:
            return "Image('')"

    __HORI_BORDER = '-' * (__WIDTH_DEFAULT + 2)
    __VERT_BORDER = '|'
    __BODY_BORDER = __VERT_BORDER + '\n' + __VERT_BORDER
    __STR_FORMAT = '{0}\n' + __VERT_BORDER + '{1}' + __VERT_BORDER + '\n{0}'
    
    def __str__(self):
        """String representation of image.
        
        Screen top and bottom border are dashes '-'. 
        Each row starts and ends with a colon ':'.
        The row of pixels is the pixel brightness with 0 replaced by a space.
        E.g.:
        -------
        |9   9|
        | 9 9 |
        |  9  |
        | 9 9 |
        |9   9|
        -------
        is the string representation of Image('90009:09090:00900:09090:90009:')
        Images too small for the 5x5 display are padded with zeroes 
        to right and bottom, e.g. the string representation of Image('111:111:')
        is
        -------
        |111  |
        |111  |
        |     |
        |     |
        |     |
        -------
        Images bigger than the screen are "truncated", e.g. the string
        representation of Image('333:4444:55555:666666:7777777:88888888') is:
        -------
        |333  |
        |4444 |
        |55555|
        |66666|
        |77777|
        -------
        """
        
        rows = [''.join(str(e) for e in row)[:Image.__WIDTH_DEFAULT]
                    for row in self.__image[:Image.__HEIGHT_DEFAULT]]
        
        rows = [r.replace('0', ' ').ljust(Image.__WIDTH_DEFAULT, ' ')
                for r in rows] 
                    
        vpad = Image.__HEIGHT_DEFAULT - self.height()
        
        if vpad > 0:
            rows = rows + vpad * [' ' * Image.__WIDTH_DEFAULT] 

        return Image.__STR_FORMAT.format(Image.__HORI_BORDER,
                                            Image.__BODY_BORDER.join(rows))

    def __add__(self, other):
        """Adding two images returns a new image that is their superimposition.
        """
        width = self.width()
        height = self.height()
        
        if width != other.width() or height != other.height():
            raise ValueError('Images must be the same size.')

        buf = array.array('B', 
                [min(Image.__PIX_MAX, self.__image[j][i] + other.__image[j][i])
                    for i in range(width) for j in range(height)])
        
        return Image(width, height, buf)        
        
    def __mul__(self, other):
        """Returns a new image created by multiplying the brightness of each 
        pixel by n.
        """
        if other < 0:
            raise ValueError('Brightness multiplier must not be negative')
                            
        buf = array.array('B', [min(Image.__PIX_MAX, int(x * other)) 
                                for sublist in self.__image for x in sublist])
        
        return Image(self.width(), self.height(), buf)
        
    def __eq__(self, other):
        if self and other:
            return self.__image == other.__image
        else:
            return not self and not other
        
    def __ne__(self, other):
        return not self.__eq__(other)
    
""" Built-in images and character map """
Image.ANGRY = Image('90009:09090:00000:99999:90909:')
Image.ASLEEP = Image('00000:99099:00000:09990:00000:')
Image.BUTTERFLY = Image('99099:99999:00900:99999:99099:')
Image.CHESSBOARD = Image('09090:90909:09090:90909:09090:')
Image.CONFUSED = Image('00000:09090:00000:09090:90909:')
Image.COW = Image('90009:90009:99999:09990:00900:')
Image.DIAMOND = Image('00900:09090:90009:09090:00900:')
Image.DIAMOND_SMALL = Image('00000:00900:09090:00900:00000:')
Image.DUCK = Image('09900:99900:09999:09990:00000:')
Image.FABULOUS = Image('99999:99099:00000:09090:09990:')
Image.GHOST = Image('99999:90909:99999:99999:90909:')
Image.GIRAFFE = Image('99000:09000:09000:09990:09090:')
Image.HAPPY = Image('00000:09090:00000:90009:09990:')
Image.HEART = Image('09090:99999:99999:09990:00900:')
Image.HEART_SMALL = Image('00000:09090:09990:00900:00000:')
Image.HOUSE = Image('00900:09990:99999:09990:09090:')
Image.MEH = Image('09090:00000:00090:00900:09000:')
Image.MUSIC_CROTCHET = Image('00900:00900:00900:99900:99900:')
Image.MUSIC_QUAVER = Image('00900:00990:00909:99900:99900:')
Image.MUSIC_QUAVERS = Image('09999:09009:09009:99099:99099:')
Image.NO = Image('90009:09090:00900:09090:90009:')
Image.PACMAN = Image('09999:99090:99900:99990:09999:')
Image.PITCHFORK = Image('90909:90909:99999:00900:00900:')
Image.RABBIT = Image('90900:90900:99990:99090:99990:')
Image.ROLLERSKATE = Image('00099:00099:99999:99999:09090:')
Image.SAD = Image('00000:09090:00000:09990:90009:')
Image.SILLY = Image('90009:00000:99999:00909:00999:')
Image.SKULL = Image('09990:90909:99999:09990:09990:')
Image.SMILE = Image('00000:00000:00000:90009:09990:')
Image.SNAKE = Image('99000:99099:09090:09990:00000:')
Image.SQUARE = Image('99999:90009:90009:90009:99999:')
Image.SQUARE_SMALL = Image('00000:09990:09090:09990:00000:')
Image.STICKFIGURE = Image('00900:99999:00900:09090:90009:')
Image.SURPRISED = Image('09090:00000:00900:09090:00900:')
Image.SWORD = Image('00900:00900:00900:09990:00900:')
Image.TARGET = Image('00900:09990:99099:09990:00900:')
Image.TORTOISE = Image('00000:09990:99999:09090:00000:')
Image.TRIANGLE = Image('00000:00900:09090:99999:00000:')
Image.TRIANGLE_LEFT = Image('90000:99000:90900:90090:99999:')
Image.TSHIRT = Image('99099:99999:09990:09990:09990:')
Image.UMBRELLA = Image('09990:99999:00900:90900:09900:')
Image.XMAS = Image('00900:09990:00900:09990:99999:')
Image.YES = Image('00000:00009:00090:90900:09000:')

Image.ARROW_N = Image('00900:09990:90909:00900:00900:')
Image.ARROW_NE = Image('00999:00099:00909:09000:90000:')
Image.ARROW_E = Image('00900:00090:99999:00090:00900:')
Image.ARROW_SE = Image('90000:09000:00909:00099:00999:')
Image.ARROW_S = Image('00900:00900:90909:09990:00900:')
Image.ARROW_SW = Image('00009:00090:90900:99000:99900:')
Image.ARROW_W = Image('00900:09000:99999:09000:00900:')
Image.ARROW_NW = Image('99900:99000:90900:00090:00009:')

Image.CLOCK12 = Image('00900:00900:00900:00000:00000:')
Image.CLOCK1 = Image('00090:00090:00900:00000:00000:')
Image.CLOCK2 = Image('00000:00099:00900:00000:00000:')
Image.CLOCK3 = Image('00000:00000:00999:00000:00000:')
Image.CLOCK4 = Image('00000:00000:00900:00099:00000:')
Image.CLOCK5 = Image('00000:00000:00900:00090:00090:')
Image.CLOCK6 = Image('00000:00000:00900:00900:00900:')
Image.CLOCK7 = Image('00000:00000:00900:09000:09000:')
Image.CLOCK8 = Image('00000:00000:00900:99000:00000:')
Image.CLOCK9 = Image('00000:00000:99900:00000:00000:')
Image.CLOCK10 = Image('00000:99000:00900:00000:00000:')
Image.CLOCK11 = Image('09000:09000:00900:00000:00000:')

Image.ALL_ARROWS = [
    Image.ARROW_N,
    Image.ARROW_NE,
    Image.ARROW_E,
    Image.ARROW_SE,
    Image.ARROW_S,
    Image.ARROW_SW,
    Image.ARROW_W,
    Image.ARROW_NW,
    ]

Image.ALL_CLOCKS = [
    Image.CLOCK12,
    Image.CLOCK1,
    Image.CLOCK2,
    Image.CLOCK3,
    Image.CLOCK4,
    Image.CLOCK5,
    Image.CLOCK6,
    Image.CLOCK7,
    Image.CLOCK8,
    Image.CLOCK9,
    Image.CLOCK10,
    Image.CLOCK11,
    ]

Image.CHARACTER_MAP = {
    ' ':Image('00000:00000:00000:00000:00000:'),
    '!':Image('09000:09000:09000:00000:09000:'),
    '"':Image('09090:09090:00000:00000:00000:'),
    '#':Image('09090:99999:09090:99999:09090:'),
    '$':Image('09990:99009:09990:90099:09990:'),
    '%':Image('99009:90090:00900:09009:90099:'),
    '&':Image('09900:90090:09900:90090:09909:'),
    "'":Image('09000:09000:00000:00000:00000:'),
    '(':Image('00900:09000:09000:09000:00900:'),
    ')':Image('09000:00900:00900:00900:09000:'),
    '*':Image('00000:09090:00900:09090:00000:'),
    '+':Image('00000:00900:09990:00900:00000:'),
    ',':Image('00000:00000:00000:00900:09000:'),
    '-':Image('00000:00000:09990:00000:00000:'),
    '.':Image('00000:00000:00000:09000:00000:'),
    '/':Image('00009:00090:00900:09000:90000:'),
    '0':Image('09900:90090:90090:90090:09900:'),
    '1':Image('00900:09900:00900:00900:09990:'),
    '2':Image('99900:00090:09900:90000:99990:'),
    '3':Image('99990:00090:00900:90090:09900:'),
    '4':Image('00990:09090:90090:99999:00090:'),
    '5':Image('99999:90000:99990:00009:99990:'),
    '6':Image('00090:00900:09990:90009:09990:'),
    '7':Image('99999:00090:00900:09000:90000:'),
    '8':Image('09990:90009:09990:90009:09990:'),
    '9':Image('09990:90009:09990:00900:09000:'),
    ':':Image('00000:09000:00000:09000:00000:'),
    ';':Image('00000:00900:00000:00900:09000:'),
    '<':Image('00090:00900:09000:00900:00090:'),
    '=':Image('00000:09990:00000:09990:00000:'),
    '>':Image('09000:00900:00090:00900:09000:'),
    '?':Image('09990:90009:00990:00000:00900:'),
    '@':Image('09990:90009:90909:90099:09900:'),
    'A':Image('09900:90090:99990:90090:90090:'),
    'B':Image('99900:90090:99900:90090:99900:'),
    'C':Image('09990:90000:90000:90000:09990:'),
    'D':Image('99900:90090:90090:90090:99900:'),
    'E':Image('99990:90000:99900:90000:99990:'),
    'F':Image('99990:90000:99900:90000:90000:'),
    'G':Image('09990:90000:90099:90009:09990:'),
    'H':Image('90090:90090:99990:90090:90090:'),
    'I':Image('99900:09000:09000:09000:99900:'),
    'J':Image('99999:00090:00090:90090:09900:'),
    'K':Image('90090:90900:99000:90900:90090:'),
    'L':Image('90000:90000:90000:90000:99990:'),
    'M':Image('90009:99099:90909:90009:90009:'),
    'N':Image('90009:99009:90909:90099:90009:'),
    'O':Image('09900:90090:90090:90090:09900:'),
    'P':Image('99900:90090:99900:90000:90000:'),
    'Q':Image('09900:90090:90090:09900:00990:'),
    'R':Image('99900:90090:99900:90090:90009:'),
    'S':Image('09990:90000:09900:00090:99900:'),
    'T':Image('99999:00900:00900:00900:00900:'),
    'U':Image('90090:90090:90090:90090:09900:'),
    'V':Image('90009:90009:90009:09090:00900:'),
    'W':Image('90009:90009:90909:99099:90009:'),
    'X':Image('90090:90090:09900:90090:90090:'),
    'Y':Image('90009:09090:00900:00900:00900:'),
    'Z':Image('99990:00900:09000:90000:99990:'),
    '[':Image('09990:09000:09000:09000:09990:'),
    '\\':Image('90000:09000:00900:00090:00009:'),
    ']':Image('09990:00090:00090:00090:09990:'),
    '^':Image('00900:09090:00000:00000:00000:'),
    '_':Image('00000:00000:00000:00000:99999:'),
    '`':Image('09000:00900:00000:00000:00000:'),
    'a':Image('00000:09990:90090:90090:09999:'),
    'b':Image('90000:90000:99900:90090:99900:'),
    'c':Image('00000:09990:90000:90000:09990:'),
    'd':Image('00090:00090:09990:90090:09990:'),
    'e':Image('09900:90090:99900:90000:09990:'),
    'f':Image('00990:09000:99900:09000:09000:'),
    'g':Image('09990:90090:09990:00090:09900:'),
    'h':Image('90000:90000:99900:90090:90090:'),
    'i':Image('09000:00000:09000:09000:09000:'),
    'j':Image('00090:00000:00090:00090:09900:'),
    'k':Image('90000:90900:99000:90900:90090:'),
    'l':Image('09000:09000:09000:09000:00990:'),
    'm':Image('00000:99099:90909:90009:90009:'),
    'n':Image('00000:99900:90090:90090:90090:'),
    'o':Image('00000:09900:90090:90090:09900:'),
    'p':Image('00000:99900:90090:99900:90000:'),
    'q':Image('00000:09990:90090:09990:00090:'),
    'r':Image('00000:09990:90000:90000:90000:'),
    's':Image('00000:00990:09000:00900:99000:'),
    't':Image('09000:09000:09990:09000:00999:'),
    'u':Image('00000:90090:90090:90090:09999:'),
    'v':Image('00000:90009:90009:09090:00900:'),
    'w':Image('00000:90009:90009:90909:99099:'),
    'x':Image('00000:90090:09900:09900:90090:'),
    'y':Image('00000:90009:09090:00900:99000:'),
    'z':Image('00000:99990:00900:09000:99990:'),
    '{':Image('00990:00900:09900:00900:00990:'),
    '|':Image('09000:09000:09000:09000:09000:'),
    '}':Image('99000:09000:09900:09000:99000:'),
    '~':Image('00000:00000:09900:00099:00000:'),
    }


""" ---------------------------------------------------------------------- """    
""" The LED display ------------------------------------------------------ """
class Display:
    __DELAY_DEFAULT_IMG = 0
    __DELAY_DEFAULT_ITER = 400
    """Display class represents the 5x5 LED display. 
    
    There is a single display object that has an image.
    """
    def __init__(self):
        """Initialise the display.
        """
        self.image = Image()
        self.__last_image = None

    def get_pixel(self, x, y):
        """Gets the brightness of LED pixel (x,y).
    
        Brightness can be from 0 (LED is off) to 9 (maximum LED brightness).
        """
        return self.image.get_pixel(x, y)
    
    def set_pixel(self, x, y, val):
        """Set the dsplay at LED pixel (x,y) to brightness val. 
    
        b can be between 0 (off) and 9 (max brightness).
        """
        self.image.set_pixel(x, y, val)
        if state.is_on():
            print(self.image)

    def clear(self):
        """Clear the display.
        """
        self.image = Image()
        if state.is_on():
            print(self.image)
        
    def show(self, iterable, **kargs):
        """Show images or a string on the display.
        
        Shows the images an image at a time or a string a character at a time,
        with delay milliseconds between image/character.
        If loop is True, loop forever.
        If clear is True, clear the screen after showing.
        Usage:
        shows an image:
        display.show(image, delay=0, wait=True, loop=False, clear=False)
        show each image or letter in the iterable:
        display.show(iterable, delay=400, wait=True, loop=False, clear=False)
        """
        if iterable is None:
            raise TypeError('not iterable')
            
        if not iterable:
            return
            
        loop = 'loop' in kargs
        if loop:
            loop = kargs['loop']
        
        wait = 'wait' in kargs
        if wait:
            wait = kargs['wait']
        else:
            wait = True
        
        clear = 'clear' in kargs
        if clear:
            clear = kargs['clear']
        
        delay = 'delay' in kargs
        
        if isinstance(iterable, str):
            iterable = [Image.CHARACTER_MAP.get(c, Image.CHARACTER_MAP.get('?')) 
                        for c in iterable]
        
        if isinstance(iterable, Image):
            iterable = [iterable]
            if delay:
                delay = kargs['delay']
            else:
                delay = Display.__DELAY_DEFAULT_IMG
        elif delay:
            delay= kargs['delay']
        else:
            delay = Display.__DELAY_DEFAULT_ITER
            
        for img in iterable:
            if delay:
                sleep(delay)
            if state.is_on() and img != self.__last_image:
                print(img)
                self.__last_image = img

        if loop:
            show(self, iterable, delay=delay, wait=wait, loop=loop, clear=clear)
        
        if clear:
            self.clear()
        else:
            self.image = eval(repr(img))
            
    def scroll(self, string, delay=400):
        """Scroll the string across the display with given delay.
        
        In this emulation this is the same as showing the string and clearing
        the screen.
        """
        for c in string:
            if delay:
                sleep(delay)
            if state.is_on():
                print(Image.CHARACTER_MAP.get(c, Image.CHARACTER_MAP.get('?')))
        
        self.clear()
        
display = Display()


""" ---------------------------------------------------------------------- """    
""" Pins ----------------------------------------------------------------- """
class Pin:
    def __init__(self, name):
        self.__name = name.lower()
        
    def write_digital(self, value):
        """Write a value to the pin that must be either 0, 1, True  or False.
        """
        if value < 0 or value > 1:
            raise ValueError('value must be 0 or 1')

        state.set(self.__name, 1 if value else 0)
              
    def read_digital(self):
        """Return the pin's value, which will be either 1 or 0.
        """
        return 1 if state.get(self.__name) else 0
    
    def write_analog(self, value):
        """Write a value to the pin that must be between 0 and 1023.
        """
        state.set(self.__name, value)   # value check deferred to state
            
    def read_analog(self):
        """Returns the pin's value, which will be between 0 and 1023
        """
        return state.get(self.__name)
        

    def set_analog_period(self, int):
        """Set the period of the PWM output of the pin in milliseconds.
        
        See https://en.wikipedia.org/wiki/Pulse-width_modulation.
        This is a null operation for the emulation.
        """       
        pass
        
    def set_analog_period_microseconds(self, int):
        """Set the period of the PWM output of the pin in microseconds.
        
        See https://en.wikipedia.org/wiki/Pulse-width_modulation)
        This is a null operation for the emulation.
        """
        pass       

    def is_touched(self):
        """Return True if the pin is being touched, False otherwise.
        """
        return state.get(self.__name) > 0
        
pin0 = Pin('pin0')
pin1 = Pin('pin1')
pin2 = Pin('pin2')
pin3 = Pin('pin3')
pin4 = Pin('pin4')
pin5 = Pin('pin5')
pin6 = Pin('pin6')
pin7 = Pin('pin7')
pin8 = Pin('pin8')
pin9 = Pin('pin9')
pin10 = Pin('pin10')
pin11 = Pin('pin11')
pin12 = Pin('pin12')
pin13 = Pin('pin13')
pin14 = Pin('pin14')
pin15 = Pin('pin15')
pin16 = Pin('pin16')
pin19 = Pin('pin19')
pin20 = Pin('pin20')


""" ---------------------------------------------------------------------- """    
""" The accelerometer ---------------------------------------------------- """
class Accelerometer:
    """Accelerometer class represents the accelerometer. 
    
    There is a single accelerometer object.
    x, y, z axes are set through State object or via state file.
    Gestures are generated randomly from a list.
    """
    gestures = ['', 'up', 'down', 'left', 'face up', 'face down', 'freefall', 
                '3g', '6g', '8g', 'shake']

    def __init__(self):
        pass
        
    def get_x(self):
        """Returns the X axis of the device, measure in milli-g.
        """
        return state.get('accelerometer_x')
        
    def get_y(self):
        """Returns the Y axis of the device, measure in milli-g.
        """
        return state.get('accelerometer_y')
        
    def get_z(self):
        """Returns the Z axis of the device, measure in milli-g.
        """
        return state.get('accelerometer_z')
        
    def get_values(self):
        """Returns all three X, Y and Z readings (in that order).
        """
        return (self.get_x(), self.get_y(), self.get_z())
    
    def current_gesture(self):
        """Return the name of the current gesture.
        
        In this emulation randomly selects a gestures from the list of gestures.
        """
        return random.choice(Accelerometer.gestures)
    
    def get_gestures(self):
        """Return a tuple of the gesture history, most recent is listed 
        last.
        
        In this emulation returns a sample of gestures
        """
        return tuple(random.sample(Accelerometer.gestures,
                        random.randint(1, len(Accelerometer.gestures))))
        
    def is_gesture(self, name):
        """Return True if the named gesture is active, False otherwise

        In this emulation returns True if the name is in a random sample of 
        gestures.
        """
        return name in self.get_gestures()
                
    def was_gesture(self, name):
        """Return True if the named gesture was active since the last call, 
        False otherwise.
        
        In this emulation returns True if the name is in a random sample of 
        gestures.
        """
        return self.is_gesture(name)
            
    def reset_gestures(self):
        """Clear the gesture history.
        
        A null operation.
        """
        pass

accelerometer = Accelerometer()

""" ---------------------------------------------------------------------- """    
""" The compass ---------------------------------------------------------- """
class Compass:
    """Compass class represents the compass. 
    
    There is a single compass object.
    
    Emulate position by generating random number for degrees offset
    from "north" and field strength by generating random number of microTeslas
    betweeo -1000 and 1000.
    Calibration just changes the calibration state from False to True.
    """
    __DEGREES_MIN = 0
    __DEGREES_MAX = 0
    __FIELD_MIN = -1000
    __FIELD_MAX = 1000
    
    def __init__(self):
        self.__calibrated = False
    
    def calibrate(self):
        """Calibrate the compass (this is needed for accurate readings).
        
        In this emulation simply records that calibrate has been called. 
        is_calibrated will return True after calibrate is called.
        """
        self.__calibrated = True

    def heading(self):
        """Return a numeric indication of degrees offset from "north".
        
        Returns a number from 0 to 360.
        """
        return random.randint(Compass.__DEGREES_MIN, Compass.__DEGREES_MAX)
    
    def get_field_strength(self):
        """Return a numeric indication of the strength of the magnetic field.
        
        Returns a number from -1000 to 1000.
        """
        return random.randint(Compass.__FIELD_MIN, Compass.__FIELD_MAX)
    
    def is_calibrated(self):
        """Returns True if the compass is calibrated (calibrate has been 
        called and not reset), returns False otherwise.
        """
        return self.__calibrated 
    
    def clear_calibration(self):
        """Reset the compass to a pre-calibration state (is_calibrated will 
        return False.
        """
        self.__calibrated = False
        
compass = Compass()

""" ---------------------------------------------------------------------- """    
""" I2C bus -------------------------------------------------------------- """
class I2C:
    """I2C is not emulated.
    """
    def __init__(self):
        pass
    
    def read(self, addr, n, repeat=False):
        """Not implemented """
        pass
    
    def write(self, addr, buf, repeat=False):
        """Not implemented """
        pass

i2c = I2C()

""" ---------------------------------------------------------------------- """    
""" UART ----------------------------------------------------------------- """
class UART:
    """UART is not emulated.
    """
    def __init__(self):
        """Not implemented """
        pass
    
    def init(self):
        """Not implemented """
        pass
    
    def any(self):
        """Not implemented """
        pass
    
    def read(self, n):
        """Not implemented """
        pass
    
    def readall(self):
        """Not implemented """
        pass
        
    def readline(self):
        """Not implemented """
        pass
        
    def readinto(self, buffer):
        """Not implemented """
        pass
        
    def write(self, buffer):
        """Not implemented """
        pass

uart = UART()

""" ---------------------------------------------------------------------- """    
""" Global functions - sleep, running_time, panic, reset ------------------"""

def sleep(ms):
    """sleep for the given number of milliseconds.
    
    For the emulation, state is reloaded after sleep.
    """
    if ms > 0:
        time.sleep(ms/1000)
        state._State__incr_runtime(ms)
    
    state.load()
    
def running_time():
    """returns the number of ms since the micro:bit was last switched on.
    
    Simply returns an int that takes account of the delays caused by 
    calls to sleep and a random increment to runing time of up to 100ms.
    """
    state._State__incr_runtime(1, True)
    
    return state._State__get_runtime()

def panic(error_code):
    """makes the micro:bit enter panic mode.
    
    This usually happens when the DAL runs out of memory, and causes a sad 
    face to be drawn on the display.
    The error_code can be any arbitrary integer value.
    On micro:bit the sad face and error code are displayed in an infinite loop
    In this emulation, show the sad face and the code twice, finishing with
    the sad face
    """
    if type(error_code) is not int:
        raise TypeError('error_code not an int')
        
    for i in range(2):
        display.show(Image.SAD)
        display.show(str(error_code))
    
    display.show(Image.SAD)

def reset():
    """resets the micro:bit.
    
    In the emulation the state is returned to 0 for all values except power,
    which is set to 1 (on)
    """
    button_a.reset_presses()
    button_b.reset_presses()
    display.clear()
    state.reset()
    











