# Allow relative import
import os
import sys
module_path = os.path.abspath(os.path.join('../vendor'))
if module_path not in sys.path:
    sys.path.append(module_path)
