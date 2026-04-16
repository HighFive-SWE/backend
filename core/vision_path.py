import sys
from pathlib import Path

# the /vision module is a sibling dir, not a published package. adding the repo
# root to sys.path lets us `import vision` without turning the monorepo into a
# pip project. done once at import-time — no runtime cost per request.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
