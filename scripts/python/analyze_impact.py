#!/usr/bin/env python3
from knowledge_control_plane import main
if __name__ == "__main__":
    import sys
    raise SystemExit(main(["impact-analyze", *sys.argv[1:]]))
