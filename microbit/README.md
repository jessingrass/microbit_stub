# microbit_stub
A version of microbit_stub that uses "microbit" as the module name.

The programs and related files here are essentially the same as for the [microbit_stub](../) module. The only difference is that they illustrate naming the module `microbit` as opposed to `microbit_stub`. This means you can use the following import statement:

```python
from microbit import *
```

and microbit micropython programs should run completely unchanged with this version of the `microbit` stub module in your Python search path.

The differences between the files in this directory and its parent are:

- `microbit_stub.py` is named `microbit.py` to allow import from `microbit`
- `bitcounter-range.py` and `happysad.py` import from `microbit` not `microbit_stub` and should run completely unchanged with this module or with the physical microbit
- `microbit_stub_settings.py` is named `microbit_settings.py`
- `pressbutton.py` and `pressbutton-withreset.py` import from `microbit` not `microbit_stub`. Note this programs are state change simiulators and not physical microbit programs.
- `test_microbit_stub.py` is named `test_microbit_stub.py` and imports from `microbit`
- `test_microbit_stub_display.txt` doctest file is named `test_microbit_display.txt` and imports from `microbit`

