import atexit
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any


class BoundedExecutor:
    """A ThreadPoolExecutor wrapper that limits total in-flight work via Semaphore.

    The semaphore is sized as ``max_workers + queue_size``. When the semaphore
    cannot be acquired, ``submit()`` raises ``RuntimeError`` instead of
    unboundedly queueing work.

    Defaults: max_workers=2, queue_size=10 (12 concurrent tasks max).
    """

    def __init__(self, max_workers: int = 2, queue_size: int = 10):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._semaphore = threading.Semaphore(max_workers + queue_size)

    def submit(self, fn: Callable, /, *args: Any, **kwargs: Any):
        """Submit a task to the executor.

        Raises RuntimeError if the semaphore is already saturated.
        """
        if not self._semaphore.acquire(blocking=False):
            raise RuntimeError("BoundedExecutor queue full")
        future = self._executor.submit(self._run_and_release, fn, *args, **kwargs)
        return future

    def _run_and_release(self, fn: Callable, /, *args: Any, **kwargs: Any):
        """Run the callable, then release the semaphore slot."""
        try:
            return fn(*args, **kwargs)
        finally:
            self._semaphore.release()

    def shutdown(self, wait: bool = True):
        """Shut down the underlying executor."""
        self._executor.shutdown(wait=wait)


# Backward-compatible global executor: 2 workers + 10 queue slots = 12 max.
background_executor = BoundedExecutor(max_workers=2, queue_size=10)


def shutdown_executor():
    """Apaga el executor global de manera segura."""
    background_executor.shutdown(wait=True)


atexit.register(shutdown_executor)
