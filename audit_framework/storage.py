import hashlib
import json
import os
from pathlib import Path
import tempfile


def atomic_write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".writing-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def save_json(path, data):
    atomic_write(Path(path), json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fingerprint(data):
    """Stable experiment/input identity prevents mixed-protocol resume."""
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


class OutputLock:
    """A process lock prevents two CLIs from paying for the same auditor."""
    def __init__(self, output):
        self.path = Path(output) / ".run.lock"

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open("a+b")
        self.file.seek(0, 2)
        if self.file.tell() == 0:
            self.file.write(b"0")
            self.file.flush()
        self.file.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.file.close()
            raise RuntimeError("Another process is using this output directory") from None
        return self

    def __exit__(self, *args):
        self.file.close()  # OS also releases the lock if the process crashes.
