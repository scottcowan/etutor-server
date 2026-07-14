import sys
from pathlib import Path

# Ensure worktree root is in sys.path so api.* modules are importable
root = str(Path(__file__).parent.parent.parent)
if root not in sys.path:
    sys.path.insert(0, root)
