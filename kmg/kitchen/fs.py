import contextlib
import os
import tempfile
from pathlib import Path


@contextlib.contextmanager
def atomic_replace(target: Path, delete=True):
    with tempfile.NamedTemporaryFile(
        dir=target.parent,
        delete=False,
    ) as f:
        try:
            yield f
            os.replace(f.name, target)
        finally:
            f.close()
            if delete:
                os.remove(f.name)
