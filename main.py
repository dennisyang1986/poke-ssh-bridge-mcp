from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(__file__)
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from poke_mcp_ssh_bridge.server import main

if __name__ == "__main__":
    main()
