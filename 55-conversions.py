#!/usr/bin/env python3

import ctypes

print(ctypes.c_char_p(None))
print(ctypes.c_char_p("Test".encode("utf-8")))
