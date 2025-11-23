import sys
import os
import inspect

sys.path.insert(0, os.getcwd())

try:
    import scripts.scripts
    print(scripts.scripts.__file__)
except Exception as e:
    print(f"Error: {e}")
