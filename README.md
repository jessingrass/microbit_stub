# microbit_stub
A Python module that emulates the BBC microbit as defined by the microbit micropython API.

**Note:** any errors in the emulation are entirely due to errors in my program logic or in my understanding of the microbit module API and not the responsibility of the developers of the [microbit micropython API](https://microbit-micropython.readthedocs.io/en/latest/microbit_micropython_api.html "microbit API").

## Overview

This Python module is based on the [microbit micropython API](https://microbit-micropython.readthedocs.io/en/latest/microbit_micropython_api.html "microbit API") defined as part of the [BBC microbit project](https://www.microbit.co.uk/ "microbit").

See: https://github.com/bbcmicrobit/micropython for the microbit micropython project repository and licensing and https://microbit-micropython.readthedocs.io/en/latest/ for the microbit micropython documentation.

The aim of this project is to provide an implementation of the [microbit micropython API](https://microbit-micropython.readthedocs.io/en/latest/microbit_micropython_api.html "microbit API") that can be used to test a microbit micropython program without having to have a physcial microbit connected. This is similar to the in-browser microbit emulations for other programming languages provided at http://microbit.co.uk/.

The motivation is to provide an easy way to test microbit micropython programs. 

If a student develops using the Web based Python editor, then feedback with respect to bugs in their programs is via a Python error message scrolling across the physical microbit screen. These are quite difficult to read and could become a barrier to development. Development in Python is likely to lead to simple syntax errors (indentation etc.) that only become apparent when an error message is displayed on the microbit screen. The hope is that it will be easier for students to find and correct bugs if they have more readable error output.

The excellent offline [mu micropython editor](http://codewith.mu/ "mu") does have a REPL shell that, if connected to a microbit, will display error output from the current program in a more convenient form in the REPL window. In this case also, there may be some benefit to being able to trace and debug a program without connecting to the physical microbit.

This module supports disconnected mode of program development with an emulation of most microbit functionality (see the "What is emulated" section of this README for more details). Emulation output is text to the console, which means the module can be used in many programming environments. There is no attempt to do graphical emulation. Providing a graphical interface may be something for the future. It would have the advantage of providing an alternative mechanism for manipulating the emulated state (see the section of this `README` on emulating and changing state for how this is currently done). As it is the module allows testing of both syntax and logical errors in microbit micropython programs.

The name of the module is `microbit_stub` to distinguish it from the official microbit module

The idea is to be able to take a program written for the `microbit` module and simply change the relevant import statement to import `microbit_stub`. The program can then be tested in a standard Python development environment or at the console. Once the program has been tested it can be copied to the [Web based](https://www.microbit.co.uk/create-code "Web Python") or [mu](http://codewith.mu/ "mu") editor and uploaded to the microbit (after reinstating the `microbit` module import statement). For example, the following Python program developed [in the browser](https://www.microbit.co.uk/create-code "Web Python") or using [mu](http://codewith.mu/ "mu"):

```python
from microbit import *
display.scroll('hello world!')
```

will scroll `'hello world!'` across the microbit screen.

The following Python program using `microbit_stub`:

```python
from microbit_stub import *
display.scroll('hello world!')
```

will output a text emulation of scrolling `'hello world!'` across a microbit screen in a console window. That is a text representation of microbit display scrolling will be shown in the console - e.g. the IDLE shell or the terminal if running from the command line.

Apart from the change of module name, the program runs unchanged in either environment.

**Note:** it should be safe to rename this module `microbit` and not cause any conflict with the [Web based](https://www.microbit.co.uk/create-code "Web Python") or [mu](http://codewith.mu/ "mu") editor. On balance, I thought it better to use a different name to distinguish between the two. If you change the name of the `microbit_stub` module to `microbit` (by renaming `microbit_stub.py` to `microbit.py`) then you will not need to change import statements when switching programming environments.

## Usage

As shown above, to use the module simply replace the line: 

```python
from microbit import *
```

with 

```python
from microbit_stub import *
```

and run your pograms in IDLE or some other Python IDE or from the command line.

As with any other Python module, the `microbit_stub.py` file must be in your Python search path (this could be by including it in the same folder as the programs you are testing).

Documentation is included in the `microbit_stub` module file.

The distribution also includes:

`test_microbit_stub.py` (and `test_microbit_stub_display.txt`) - `unittest` and `doctest` tests of the module (type `python3 test_microbit_stub.py` at a terminal to run all tests, including the doctests of the display)

`happysad.py` - an example program that displays `Image.HAPPY` on button A press and `Image.SAD` otherwise. This program will also work with the physical microbit.

`bitcounter-range.py` - an example program that uses the microbit display to count up to 31 on button A presses and convert the current binary number to decimal on a button B press. This program will also work with the physical microbit.

`pressbutton.py` - a program to emulate pressing and releasing a button. It takes the button name (`button_a` or `button_b`) as a command line argument or uses button_a by default. This is not a microbit program but can be used to test programs that react to button presses (see information on emulating state below). It could be adapted to emulate changes to the state of pins.

`pressbutton_withreset.py` - this is similar to `pressbutton.py` but resets the state of the microbit and exists after 100 button presses. This is also for testing purposes.

Together, the above programs should give some idea of how to use the microbit_stub module.

*What is emulated*

The module provides an implementation of the following parts of the microbit micropython API:

```python
sleep
running_time
panic
reset

Button
Image   # including built-in images
Display
Pin
Accelerometer
Compass
```

The `I2C` and `UART` classes and methods are defined but the implementation of methods is simply to `pass`. Programs that use the `I2C` or `UART` classes should run (up to a point) but will not do anything interested.

Internally, images are stored as a list of list of 5x5 pixel values. The values are in the range 0 to 9 corresponding to the microbit pixel intensity values. 

The display of an image is a text border around 5 characters of text that represent each row of the microbit display. 0s are represented by a space and other pixel values by their digit. For example, the following program:

```python
from microbit_sbut import *
display.show('a')
```

prints:

```
-------
|     |
| 999 |
|9  9 |
|9  9 |
| 9999|
-------
```

to the console.

0s are represented by spaces to make the image clearer. They are 0s in the internal representation.

When using `display.show()` to show a string of charactes, they are printed vertically to the console. E.g.:

```python
from microbit_sbut import *
display.show('ab')
```

prints:

```
-------
|     |
| 999 |
|9  9 |
|9  9 |
| 9999|
-------
-------
|9    |
|9    |
|999  |
|9  9 |
|999  |
-------
```

**Note:** as with the physical microbit, showing a string with runs repeated characters results in superimposition. That is `display.show('hello')` superimposes the 2nd `l` on the first. Scrolling a string with repeated characters shows all characters. 

In addition to the implementation of the `microbit` classes and global functions such as `sleep`, `microbit_stub` extends the API with a `State` class and a single `state` instance that represents the state of buttons, pins, and accelerometer x, y and z values. For example, reading from a pin involves reading from a corresponding value of the `state` object. Writing to a pin, changes a corresponding value of the `state` object. See the next section for information on how to use the `state` instance to simulate state changes.

Accelerometer gestures are randomly generated, as are compass headings and field strengths. They are not emulated or stored as part of the `microbit_stub state`. Current image state is maintained by the `image` instance and is not stored as part of the `state` object.

## Emulating and changing microbit state (input/output)

The "state" of a physical microbit is determined by button presses, inputs and output to pins etc. The `microbit_stub` does not have these physical inputs and outputs. Instead, internally, the state of the emulated microbit is represented by a dictionary. In the normal case this state representation is loaded from and saved to one or more json files. This internal representation is managed by and manipulated through a `state` object.

It should be stressed that microbit micropython programs can be tested with the `microbit_stub` module without any direct interaction with `state` object. The exposure of the `state` object and the possibility of chaining underlying state files opens up the possibility of more extensive testing and simulation of input/output events.

The initial state is:

```json
{
    "accelerometer_x": 0,
    "accelerometer_y": 0,
    "accelerometer_z": 0,
    "button_a": 0,
    "button_a_presses": 0,
    "button_b": 0,
    "button_b_presses": 0,
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
    "power": 1,
    "state_file": "microbit_state.json"
}
```

There are entries for: 
- accelerometer x, y and z values,
- button A and B (which will be 1 if currently pressed) and to record a counts of button presses, 
- available pins (0 to 16 and 19 and 20)

In addition, there are entries for:

- microbit power. If power is 1, the microbit is on and display output will be printed. If power is 0, there is no output.
- the state file (`state_file`) - this allows chaining of state files to simulate state changes, allowing the possibility of cycling through a series of state files. The `state_file` entry can be thought of as a pointer to the next state of the microbit, contained in the specified `state_file`.

The `state` object provides controlled access to the representation of state, with validity checking of state changes.

The initial state file is specified in the `microbit_stub_settings.py` config file. This settings file is just another module that the `microbit_stub` module imports. If `microbit_stub_settings.py` cannot be found, the default state file is `microbit_state.json`. If a state file cannot be found or opened, then in-memory representation of state is used and it is not possible to manipulate microbit state from multiple processes.

The `microbit_stub` module is fail-silent with respect to reading from and writing to settings and state files and falls back to in-memory operation. This is behaviour that could conceivably be configured relatively minor changes to the module. As an initial release it was considered better to simply revert to something that works in-memory in the event of file access failures. It does mean that users must be aware that incorrect filenames or non-existent files or files with incorrect permissions may result in their tests not behaving as expected.

State is dumped to file after any state change (including on reset).

State is loaded on initialisation of the module, on wake up from a sleep, and before a state change is dumped (to include any other state changes).

There is no concurrency control on state file access because:

1. File locking is notoriously difficult to do cross platform and in any case is error-prone
2. it is unnecessary, the implication of concurrent access in this case is that a state change is missed - e.g. equivalent to missing a button press. Such missed updates are "normal" behaviour for a microbit.

There are essentially three ways to simulate state changes:

- invoke state object methods in a microbit program - this will work but has the disadvantage that the progrm is no longer a standard microbit progam and and any code invoking state methods must be removed or commented out before uploading to the microbit
- use separate program(s) to invoke state object methods - i.e. run the microbit program and one or more state changing programs that all operate on the same underlaying state file(s). An example of this approach is to run the `happysad.py` program in one terminal and the `pressbutton.py` program in another terminal using the same configuration. The pressbutton program should cause the happysad progarm to alternate between happy and sad faces.
- chain state files to simulate state changes. An example of this approach is to configure the initial state file to be `microbit_state_00.json` or `microbit_state_01.json`. In `microbit_state_00.json` the value for `button_a` is 0 and the value for `state_file` is `microbit_state_01.json`. In `microbit_state_01.json` the value for `button_a` is 1 and the value for `state_file` is `microbit_state_00.json`. This has the effect of alternating between each state file and, therefore, alternating between 1 (pressed) and 0 (not pressed) for `button_a`.

I realise the above may sound quite complex and stress two points:

1. some program testing can be done without the above manipulations of state (it is additional functionality)
2. the explanations may become clearer by inspection of and running the programs provide in the distribution (and by more documentation that may be provided at a later date if I get time)


