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
"""
import array
import doctest
import random
import unittest

from microbit import *
from microbit import Button, Pin, STATE_FILE_DEFAULT, State

def init(full_init):
    print()
    if full_init:
        state.power_off()
        reset()

""" ---------------------------------------------------------------------- """    
""" state tests -----------------===-------------------------------------- """
class TestState(unittest.TestCase):
    keys = [key for key in state._State__data.keys() 
                if key != State._State__STATE_FILE_KEY]    

    def assert_state(self, value, power):
        for key in self.keys:
            if key != 'power':
                self.assertEqual(state._State__data[key], value)
            else:
                self.assertEqual(state._State__data[key], power)
                
    def setUp(self):
        init(True)

    def test_get_set(self):
        state.power_off()
        self.assert_state(0, 0)
        
        for key in self.keys:
            state.set(key, 1)
            self.assertEqual(state.get(key), 1)
             
        self.assertEqual(state.get('unknown'), 0)
        
        state.set('unknown', 1)
        self.assertEqual(state.get('unknown'), 0)
        
        limited_keys = [ key for key in self.keys
                            if key not in State._State__ACCELEROMETER_KEYS
                            and key not in State._State__PRESSES_KEYS]

        for key in limited_keys:
            with self.assertRaises(ValueError):
                state.set(key, -1)
        
            with self.assertRaises(ValueError):
                state.set(key, 1024)

            state.set(key, 1023)
            self.assertEqual(state.get(key), 1023)

        for key in State._State__PRESSES_KEYS:
            with self.assertRaises(ValueError):
                state.set(key, -1)

            state.set(key, 1023)
            self.assertEqual(state.get(key), 1023)
            state.set(key, 1024)
            self.assertEqual(state.get(key), 1024)
            state.set(key, 10240)
            self.assertEqual(state.get(key), 10240)
            
        for key in State._State__ACCELEROMETER_KEYS:
            state.set(key, -1)
            self.assertEqual(state.get(key), -1)
            state.set(key, -1023)
            self.assertEqual(state.get(key), -1023)
            state.set(key, -1024)
            self.assertEqual(state.get(key), -1024)
            state.set(key, -10240)
            self.assertEqual(state.get(key), -10240)
            state.set(key, 1023)
            self.assertEqual(state.get(key), 1023)
            state.set(key, 1024)
            self.assertEqual(state.get(key), 1024)
            state.set(key, 10240)
            self.assertEqual(state.get(key), 10240)
        

        state.power_off()
        state.reset()
                
    def test_state_file(self):
        # test with file and without ('')
        self.assert_state(0, 1)
        
        for key in self.keys:
            state.set(key, 1)
        
        self.assert_state(1, 1)
        
        state.set(State._State__STATE_FILE_KEY, '')   
        self.assertEqual(state.get(State._State__STATE_FILE_KEY), '')
        state.reset()
        self.assert_state(0, 1)
        
        state._State__data[State._State__STATE_FILE_KEY] = STATE_FILE_DEFAULT
        state.load()
        self.assert_state(1, 1)
        
        state.reset()
        self.assert_state(0, 1)
        
    def test_press(self):
        for button in [button_a, button_b]:
            state.press(button.name)
            self.assertTrue(button.is_pressed())
            self.assertEqual(button.get_presses(), 1)
        
        button_c = Button('button_c')
        
        state.press('button_c')
        self.assertFalse(button_c.is_pressed())
        self.assertEqual(button_c.get_presses(), 0)
    
    def test_release(self):
        for button in [button_a, button_b]:
            state.press(button.name)
            self.assertTrue(button.is_pressed())
            self.assertEqual(button_a.get_presses(), 1)
            state.release(button.name.upper())
            self.assertFalse(button.is_pressed())
            self.assertEqual(button_a.get_presses(), 1)
    
    def test_press_and_release(self):
        for button in [button_a, button_b]:
            state.press_and_release(button.name)
            self.assertFalse(button.is_pressed())
            self.assertEqual(button_a.get_presses(), 1)
        
    def test_power(self):
        self.assertTrue(state.is_on())
        state.power_off()
        self.assertFalse(state.is_on())
        state.power_on()
        self.assertTrue(state.is_on())
        
    def test_load(self):
        state.load()
        self.assert_state(0, 1)
        
        for key in self.keys:
            state._State__data[key] = state._State__data[key] + 1
        
        self.assert_state(1, 2)
            
        state.load()
        self.assert_state(0, 1)

    def test_dump(self):
        self.assert_state(0, 1)
        for key in self.keys:
            state._State__data[key] = state._State__data[key] + 1

        self.assert_state(1, 2)
        state.dump()
        state.load()
        
        self.assert_state(1, 2)
    
    def test_reset(self):
        for key in self.keys:
            state.set(key, 1)
            self.assertEqual(state.get(key), 1)
        
        state.reset()
        
        self.assert_state(0, 1)
        self.assertEqual(state.get('state_file'), STATE_FILE_DEFAULT)


""" ---------------------------------------------------------------------- """    
""" reset test ----------------------------------------------------------- """
class TestReset(unittest.TestCase):        
    def setUp(self):
        init(True)
        
    def test_reset(self):
        # power off statements below are to prevent display output
        # which is tested elsewhere
        state_check = TestState()
        
        state_check.assert_state(0, 1)
        
        for key in state_check.keys:
            state.set(key, 1)
        
        state_check.assert_state(1, 1)

        state.power_off()

        state_check.assert_state(1, 0)

        reset()

        state_check.assert_state(0, 1)        

        self.assertEqual(button_a.get_presses(), 0)
        self.assertEqual(button_b.get_presses(), 0)
        
        for button in [button_a, button_b]:
            for i in range(4):
                state.press(button.name)
                self.assertEqual(button.get_presses(), i + 1)
        
        state.power_off()
        reset()
        
        self.assertEqual(button_a.get_presses(), 0)
        self.assertEqual(button_b.get_presses(), 0)
        
        state.power_off()
        display.show(Image.HAPPY)
        self.assertEqual(display.image, Image.HAPPY)
        
        reset()

        self.assertEqual(display.image, Image())


""" ---------------------------------------------------------------------- """    
""" running_time test ---------------------------------------------------- """
class TestRunningTime(unittest.TestCase):        
    def setUp(self):
        init(True)

    
    def test_running_time(self):
        print('... running time test - be patient! ...')

        state.power_off()
        prev = state._State__get_runtime()
        self.assertEqual(prev, 0)
        
        delay = 10
        
        for i in range(1, 1000):
            sleep(delay)
            curr = running_time()
            diff = curr - prev
            self.assertTrue(diff > delay)
            self.assertTrue(diff <= State._State__RUNTIME_MAX_INCR + delay)
            prev = curr
        
        state.power_off()
        prev = state._State__get_runtime()
        self.assertEqual(prev, 0)
        curr = running_time()
        diff = curr - prev
        self.assertTrue(diff > delay)
        self.assertTrue(diff <= State._State__RUNTIME_MAX_INCR + delay)
        

""" ---------------------------------------------------------------------- """    
""" panic test ----------------------------------------------------------- """
class TestPanic(unittest.TestCase):        
    def setUp(self):
        init(True)
        
    def test_panic(self):
        state.power_off()
        panic(0)
        self.assertEqual(display.image, Image.SAD)
        panic(100)
        self.assertEqual(display.image, Image.SAD)
        panic(-100)
        self.assertEqual(display.image, Image.SAD)

        with self.assertRaises(TypeError):
            panic('a')        
                    
                
""" ---------------------------------------------------------------------- """        
""" button tests --------------------------------------------------------- """
class TestButton(unittest.TestCase):
    def setUp(self):
        init(True)
        
    def test_is_pressed(self):
        for button in [button_a, button_a]:
            self.assertFalse(button.is_pressed())
            state.press(button.name)
            self.assertTrue(button.is_pressed())
            state.release(button.name)
            self.assertFalse(button.is_pressed())
        
    def test_was_pressed(self):
        for button in [button_a, button_a]:
            self.assertFalse(button.was_pressed())
            state.press(button.name)
            self.assertTrue(button.was_pressed())
            self.assertFalse(button.was_pressed())
            state.release(button.name)
            self.assertFalse(button.was_pressed())
            button.reset_presses()
            self.assertFalse(button.was_pressed())               
    
    def test_get_presses(self):
        for button in [button_a, button_b]:
            self.assertEqual(button.get_presses(), 0)
            for i in range(4):
                state.press(button.name)
            
            self.assertEqual(button.get_presses(), 4)
    
    def test_reset_presses(self):
        for button in [button_a, button_b]:
            for i in range(4):
                state.press(button.name)
            
            self.assertTrue(button.was_pressed())        
            self.assertFalse(button.was_pressed())        
            self.assertEqual(button.get_presses(), 4)
            button.reset_presses()
            self.assertEqual(button.get_presses(), 0)
            
            self.assertFalse(button.was_pressed())     
            
""" ---------------------------------------------------------------------- """    
""" image tests --------------------------------------------------------- """
class TestImage(unittest.TestCase):
    def setUp(self):
        init(False)
    
    def checksum(self, image, **kwargs):
        sum = 0
        if 'pixels' in kwargs:
            pixels = kwargs['pixels']
            for pix in pixels:
                self.assertEqual(image.get_pixel(pix[0], pix[1]), pix[2])
                sum = sum + pix[2]
        else:
            sum = kwargs['sum']
        
        for y in range(image.height()):
            for x in range(image.width()):
                sum = sum - image.get_pixel(x, y)
        
        self.assertEqual(sum, 0)

    def test_init_default(self):
        image = Image()
        self.assertEqual(image, Image('00000:00000:00000:00000:00000:'), 0)
        self.checksum(image, sum=0)
            
    def test_init_fromstring(self):
        image = Image('90009:09090:00900:09090:90009')
        self.checksum(image, 
                pixels=[(0,0,9),(4,0,9),(1,1,9),(3,1,9),(2,2,9),(1,3,9),(3,3,9),(0,4,9),(4,4,9)])
       
        image = Image('')
        self.assertEqual(image.width(), 0)
        self.assertEqual(image.height(), 0)
        self.checksum(image, sum=0)

        image = Image('123')
        self.checksum(image, pixels=[(0,0,1),(1,0,2),(2,0,3)])
        
        image = Image(':')
        self.assertEqual(image, Image())
        
        image = Image(':123:')
        self.assertEqual(image, Image('000:123:'))
        self.checksum(image, pixels=[(0,1,1),(1,1,2),(2,1,3)])
        
        image = Image(':123')
        self.assertEqual(image, Image('000:123:'))
        self.checksum(image, pixels=[(0,1,1),(1,1,2),(2,1,3)])
       
        with self.assertRaises(TypeError):
            image = Image(None)
        
        with self.assertRaises(ValueError):
            image = Image('rubbish')
            
    def test_init_frombuffer(self):
        image = Image(3, 2, array.array('B', [0,0,0,1,1,1]))
        self.assertEqual(image, Image('000:111:'))
        self.checksum(image, pixels=[(0,1,1),(1,1,1),(2,1,1)])
        
        image = Image(0, 0, array.array('B', []))
        self.assertEqual(image, Image(''))
        self.checksum(image, sum=0)

        with self.assertRaises(TypeError):
            image = Image(6, 6, None)
        
        with self.assertRaises(ValueError):
            image = Image(2, 2, array.array('B', [0, 0]))
            
        with self.assertRaises(ValueError):
            image = Image(2, 2, array.array('B', [0, 0, 0, 0, 0, 0]))
        
        image = Image(2, 2, array.array('B', [0, 0, 0, 0]))
        self.assertEqual(image, Image('00:00:'))
        self.checksum(image, sum=0)

    def test_init_fromsize(self):
        image = Image(4, 5)
        self.assertEqual(image, Image('0000:0000:0000:0000:0000:'))
        self.checksum(image, sum=0)
        
        image = Image(0, 0)
        self.assertEqual(image, Image(''))
        self.checksum(image, sum=0)
        
        with self.assertRaises(ValueError):
            image = Image(-1, -1)
        
    def test_width(self):
        image = Image(3, 2)
        self.assertEqual(image.width(), 3)
        
        image = Image('000:000:0000:00000:')
        self.assertEqual(image.width(), 5)
        
        image = Image('')
        self.assertEqual(image.width(), 0)
    
    def test_height(self):
        image = Image(3, 2)
        self.assertEqual(image.height(), 2)
        
        image = Image('000:000:0000:00000:')
        self.assertEqual(image.height(), 4)
        
        image = Image('')
        self.assertEqual(image.height(), 0)
        
    def test_set_pixel(self):
        image = Image()
        
        for y in range(5):
            for x in range(5):
                image.set_pixel(x, y, 1)
                self.assertEqual(image.get_pixel(x, y), 1)
                
        self.assertEqual(image, Image('11111:11111:11111:11111:11111:'))
        self.checksum(image, sum=25)
        
        with self.assertRaises(ValueError):
            image.set_pixel(0, 0, -1)
            
        with self.assertRaises(ValueError):
            image.set_pixel(0, 0, 10)
            
        with self.assertRaises(IndexError):
            image.set_pixel(5, 5, 1)
        
        with self.assertRaises(IndexError):
            image = Image('')
            image.set_pixel(0, 0, 1)
    
    def test_get_pixel(self):
        image = Image()
        
        for y in range(5):
            for x in range(5):
                self.assertEqual(image.get_pixel(x, y), 0)
                image.set_pixel(x, y, 1)
                self.assertEqual(image.get_pixel(x, y), 1)
    
    def checkshift(self, shift, pos_images, neg_images):
        for i in range(len(pos_images)):
            self.assertEqual(shift(i), pos_images[i])
        
        for i in range(len(neg_images)):
            self.assertEqual(shift(-i), neg_images[i])
            
    def test_shifts(self):
        image = Image()
        for shift in [image.shift_left, image.shift_right, 
                        image.shift_up, image.shift_down]:
            self.assertEqual(shift(1), Image('00000:00000:00000:00000:00000:'))

        image = Image('')
        for shift in [image.shift_left, image.shift_right, 
                        image.shift_up, image.shift_down]:
            self.assertEqual(shift(1), Image(''))
    
        image = Image('10000:01000:00100:00010:00001:')
        left_down_images = [image,
                        Image('00000:10000:01000:00100:00010:'),
                        Image('00000:00000:10000:01000:00100:'),
                        Image('00000:00000:00000:10000:01000:'), 
                        Image('00000:00000:00000:00000:10000:'), 
                        Image('00000:00000:00000:00000:00000:'), 
                        Image('00000:00000:00000:00000:00000:'),
                        ]

        right_up_images = [image,
                        Image('01000:00100:00010:00001:00000:'),
                        Image('00100:00010:00001:00000:00000:'),
                        Image('00010:00001:00000:00000:00000:'),
                        Image('00001:00000:00000:00000:00000:'),
                        Image('00000:00000:00000:00000:00000:'),
                        Image('00000:00000:00000:00000:00000:'),
                        ]

        self.checkshift(image.shift_left, left_down_images, right_up_images)        
        self.checkshift(image.shift_right, right_up_images, left_down_images)
        self.checkshift(image.shift_up, right_up_images, left_down_images)
        self.checkshift(image.shift_down, left_down_images, right_up_images)
        
    def test_repr(self):
        for image in [Image(), Image(''), Image('10000:01000:00100:00010:00001:')]:
            self.assertEqual(image, eval(repr(image)))
        
    def test_str(self):
        image_str = '11111\n22222\n33333\n44444\n55555'
        image = Image(image_str.replace('\n', ':'))
        image_str = image_str.replace('\n', '|\n|')
        image_str = '-------\n|' + image_str + '|\n-------'
        self.assertEqual(image_str, str(image))
        
        for i in [1, 2, 3, 4, 5]:
            image_str = image_str.replace(str(i), ' ')
        
        self.assertEqual(image_str, str(Image()))
        
        image_str = '-------\n' + '|     |\n'* 5 + '-------' 
        self.assertEqual(image_str, str(Image('')))
        
    def test_add(self):
        image1 = Image('11111:00000:11111:00000:11111:')
        image2 = image1 + Image('00000:11111:00000:11111:00000:')

        self.assertEqual(image1, Image('11111:00000:11111:00000:11111:'))
        self.assertEqual(image2, Image('11111:11111:11111:11111:11111:'))        
        self.assertEqual(image2 + image2, Image('22222:22222:22222:22222:22222:'))
        self.assertEqual(image2, Image('11111:11111:11111:11111:11111:'))
        
        self.assertEqual(Image('000:111:222:') + Image('999:888:777'), 
            Image('999:999:999'))
        
        self.assertEqual(Image('999:999:999:') + Image('111:111:111'), 
            Image('999:999:999'))
            
        with self.assertRaises(ValueError):
            image = Image('111:222:') + Image('22:33:44:')
        
    def test_mul(self):
        image = Image()
        
        self.assertEqual(image * 0, image)
        self.assertEqual(image * 1, image)
        self.assertEqual(image * 2, image)
        
        image = Image('')
        
        self.assertEqual(image * 0, image)
        self.assertEqual(image * 1, image)
        self.assertEqual(image * 2, image)

        image = Image('11111:22222:33333:44444:55555:')
        
        self.assertEqual(image * 0, Image())
        self.assertEqual(image * 1, image)
        self.assertEqual(image * 2, Image('22222:44444:66666:88888:99999:'))
        self.assertEqual(image * 3, Image('33333:66666:99999:99999:99999:'))
        self.assertEqual(image * 4, Image('44444:88888:99999:99999:99999:'))
        self.assertEqual(image * 5, Image('55555:99999:99999:99999:99999:'))
        self.assertEqual(image * 6, Image('66666:99999:99999:99999:99999:'))
        self.assertEqual(image * 7, Image('77777:99999:99999:99999:99999:'))
        self.assertEqual(image * 8, Image('88888:99999:99999:99999:99999:'))
        self.assertEqual(image * 9, Image('99999:99999:99999:99999:99999:'))
        self.assertEqual(image * 10, Image('99999:99999:99999:99999:99999:'))
        
        with self.assertRaises(ValueError):
            image = image * -1
            
""" ---------------------------------------------------------------------- """    
""" display tests -------------------------------------------------------- """
class TestDisplay(unittest.TestCase):
    __DOCTEST_FILE = 'test_microbit_display.txt'

    def setUp(self):
        init(True)

    def test__init__(self):
        self.assertEqual(display.image, Image())

    def test_get_pixel(self):
        for y in range(display.image.height()):
            for x in range(display.image.width()):
                self.assertEqual(display.image.get_pixel(x,  y), 0)
                display.image.set_pixel(x, y, x)
                self.assertEqual(display.image.get_pixel(x, y), x)
    
    def test_set_pixel(self):
        for y in range(display.image.height()):
            for x in range(display.image.width()):
                display.image.set_pixel(x, y, x+y)
                self.assertEqual(display.image.get_pixel(x,  y), x+y)
                
        with self.assertRaises(ValueError):
            display.image.set_pixel(0, 0, -1)
        
        with self.assertRaises(ValueError):
            display.image.set_pixel(0, 0, 10)
        
    def test_clear(self):
        state.power_off()
        self.assertEqual(display.image, Image())
        display.clear()
        self.assertEqual(display.image, Image())
        
        for y in range(display.image.height()):
            for x in range(display.image.width()):
                display.image.set_pixel(x, y, x+y)
        
        self.assertEqual(display.image, Image('01234:12345:23456:34567:45678:'))
        
        display.clear()
        
        self.assertEqual(display.image, Image())
           
    def test_show(self):
        state.power_off()
        display.show(Image('11111:11111:11111:11111:11111:'), clear=False)
        self.assertEqual(display.image, Image('11111:11111:11111:11111:11111:'))
        display.show(Image('11111:11111:11111:11111:11111:'), clear=True)
        self.assertEqual(display.image, Image())
        display.show([])
        self.assertEqual(display.image, Image())
        display.show('')
        self.assertEqual(display.image, Image())

        with self.assertRaises(TypeError):
            display.show(None)
            
    def test_doctest_show_scroll(self):
        print('... display show and scroll doctests - be patient! ...')
        doctest.testfile(TestDisplay.__DOCTEST_FILE)
        
    def test_scroll(self):
        state.power_off()
        display.show('notcleared')
        self.assertEqual(display.image, Image.CHARACTER_MAP['d'])
        display.scroll('cleared')
        self.assertEqual(display.image, Image())
        
""" ---------------------------------------------------------------------- """    
""" pin tests ------------------------------------------------------------ """
class TestPin(unittest.TestCase):
    __pins = [pin0, pin1, pin2, pin3, pin4, pin5, pin6, pin7, pin8, pin9, pin10,
                pin11, pin12, pin13, pin14, pin15, pin16, pin19, pin20]

    def setUp(self):
        init(True)
        
    def test_read_write_digital(self):
        for pin in TestPin.__pins:
            self.assertEqual(pin.read_digital(), 0)
            pin.write_digital(1)
            self.assertEqual(pin.read_digital(), 1)
            pin.write_digital(0)
            self.assertEqual(pin.read_digital(), 0)
            pin.write_digital(True)
            self.assertEqual(pin.read_digital(), 1)
            pin.write_digital(False)
            self.assertEqual(pin.read_digital(), 0)
            
            with self.assertRaises(ValueError):
                pin.write_digital(-1)

            with self.assertRaises(ValueError):
                pin.write_digital(2)

            with self.assertRaises(TypeError):
                pin.write_digital('a')
                   
        # unknown pin
        pin17 = Pin('pin17')
        pin17.write_digital(1)
        self.assertEqual(pin17.read_digital(), 0)      
        
    def test_read_write_analog(self):
        for pin in TestPin.__pins:
            self.assertEqual(pin.read_analog(), 0)
            pin.write_analog(1)
            self.assertEqual(pin.read_analog(), 1)
            pin.write_analog(0)
            self.assertEqual(pin.read_analog(), 0)
            pin.write_analog(1023)
            self.assertEqual(pin.read_analog(), 1023)
            pin.write_analog(1.5)
            self.assertEqual(pin.read_analog(), 1)
            pin.write_analog(0.5)
            self.assertEqual(pin.read_analog(), 0)
           
            with self.assertRaises(ValueError):
                pin.write_analog(-1)

            with self.assertRaises(ValueError):
                pin.write_analog(1024)

            with self.assertRaises(TypeError):
                pin.write_analog('a')
                   
        # unknown pin
        pin17 = Pin('pin17')
        pin17.write_analog(1)
        self.assertEqual(pin17.read_analog(), 0)      

    def test_is_touched(self):
        for pin in TestPin.__pins:
            self.assertFalse(pin.is_touched())
            pin.write_digital(1)
            self.assertTrue(pin.is_touched())
            pin.write_digital(0)
            self.assertFalse(pin.is_touched())
            
    def test_set_analog_period(self):
        pin0.set_analog_period(0)    # nothing to do
        
    def test_set_analog_period_microseconds(self):
        pin0.set_analog_period_microseconds(0)    # nothing to do
                   
""" ---------------------------------------------------------------------- """    
""" accelerometer tests -------------------------------------------------- """
class TestAccelerometer(unittest.TestCase):
    __axes = { 'accelerometer_x':accelerometer.get_x,
                'accelerometer_y':accelerometer.get_y,
                'accelerometer_z':accelerometer.get_z,
            }
    
    def setUp(self):
        init(True)

    def axisTest(self, axis):
        self.assertEqual(TestAccelerometer.__axes[axis](), 0)
        val = random.randint(-1000, 1000)
        state.set(axis, val)
        self.assertEqual(TestAccelerometer.__axes[axis](), val)
        state.set(axis, 0)
        self.assertEqual(TestAccelerometer.__axes[axis](), 0)
        
    def test_get_x(self):
        self.axisTest('accelerometer_x')
             
    def test_get_y(self):
        self.axisTest('accelerometer_y')
        
    def test_get_z(self):
        self.axisTest('accelerometer_z')
        
    def test_current_gesture(self):
        self.assertIn(accelerometer.current_gesture(), accelerometer.gestures)
    
    def test_get_gestures(self):
        for g in accelerometer.get_gestures():
            self.assertIn(g, Accelerometer.gestures)
        
        self.assertNotIn('unknown', Accelerometer.gestures)
        
    def test_is_gesture(self):
        self.assertFalse(accelerometer.is_gesture('unknown'))
                
    def test_was_gesture(self):
        self.assertFalse(accelerometer.was_gesture('unknown'))
        
    def test_reset_gestures(self):
        accelerometer.reset_gestures()

""" ---------------------------------------------------------------------- """    
""" compass tests -------------------------------------------------------- """
class TestCompass(unittest.TestCase):
    def setUp(self):
        init(False)

    def test_calibration(self):
        self.assertFalse(compass.is_calibrated())
        compass.calibrate()
        self.assertTrue(compass.is_calibrated())
        compass.clear_calibration()
        self.assertFalse(compass.is_calibrated())


    def test_heading(self):
        for i in range(1000):
            h = compass.heading()
            self.assertTrue(h > -1 and h < 361)
 
    def test_get_field_strength(self):
        for i in range(1000):
            fs = compass.get_field_strength()
            self.assertTrue(fs > -1001 and fs < 1001)
            
""" ---------------------------------------------------------------------- """    
""" I2C tests ------------------------------------------------------------ """
class TestI2C(unittest.TestCase):
    """I2C is not emulated - tests just pass.
    """
    def setUp(self):
        init(False)

    def test_read(self):
        pass
    
    def test_write(self):
        pass

""" ---------------------------------------------------------------------- """    
""" UART tests ----------------------------------------------------------- """
class TestUART(unittest.TestCase):
    """UART is not emulated tests just pass.
    """
    def setUp(self):
        init(False)

    def test_init(self):
        pass
    
    def test_any(self):
        pass
    
    def test_read(self):
        pass
    
    def test_readall(self):
        pass
        
    def test_readline(self):
        pass
        
    def test_readinto(self):
        pass
        
    def test_write(self):
        pass
    
""" ---------------------------------------------------------------------- """    

if __name__ == '__main__':
    unittest.main()
