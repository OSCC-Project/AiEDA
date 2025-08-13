__version__ = "0.1.dev"

import sys
import os
current_dir = os.path.split(os.path.abspath(__file__))[0]
root = current_dir.rsplit('/', 1)[0]
sys.path.append(root)

from .data import *
from .eda import *
from .flows import *
from .workspace import *
from .analysis import *
from .ai import *