"""
Tests for core/tasks.py — BoundedExecutor.

Strict TDD: tests written BEFORE production code.
"""
import pytest


class TestBoundedExecutor:
    """Unit tests for BoundedExecutor concurrency limiting."""

    def test_up_to_limit_tasks_succeed(self):
        """GIVEN BoundedExecutor(max_workers=2, queue_size=10)
        WHEN submitting ≤12 tasks THEN all complete without error."""
        from core.tasks import BoundedExecutor

        executor = BoundedExecutor(max_workers=2, queue_size=10)
        futures = []
        for i in range(12):
            f = executor.submit(lambda x: x, i)
            futures.append(f)
        results = [f.result() for f in futures]
        assert results == list(range(12))
        executor.shutdown(wait=True)

    def test_exceeding_limit_raises_runtime_error(self):
        """GIVEN BoundedExecutor(max_workers=1, queue_size=0)
        WHEN submitting 2nd task while 1st is still running
        THEN RuntimeError is raised."""
        from core.tasks import BoundedExecutor
        import time

        executor = BoundedExecutor(max_workers=1, queue_size=0)

        def block_and_return():
            time.sleep(10)  # Hold the single slot
            return "blocked"

        f1 = executor.submit(block_and_return)

        # Give the thread a moment to start
        time.sleep(0.1)

        with pytest.raises(RuntimeError, match="BoundedExecutor queue full"):
            executor.submit(lambda: 42)

        executor.shutdown(wait=False)
        # Don't wait for f1 — we're shutting down forcefully

    def test_executor_not_crash_on_overflow(self):
        """GIVEN BoundedExecutor with full queue
        WHEN submission raises RuntimeError THEN executor remains usable."""
        from core.tasks import BoundedExecutor
        import time

        executor = BoundedExecutor(max_workers=1, queue_size=1)
        # Saturate: 1 running + 1 queued = 2 total

        def slow_task():
            time.sleep(0.2)
            return "done"

        f1 = executor.submit(slow_task)
        f2 = executor.submit(slow_task)

        # Give threads time to start
        time.sleep(0.05)

        with pytest.raises(RuntimeError, match="BoundedExecutor queue full"):
            executor.submit(lambda: None)

        assert f1.result() == "done"
        assert f2.result() == "done"
        executor.shutdown(wait=True)

    def test_backward_compatible_background_executor(self):
        """GIVEN core.tasks module
        WHEN importing background_executor THEN it is a BoundedExecutor instance."""
        from core.tasks import background_executor

        from core.tasks import BoundedExecutor
        assert isinstance(background_executor, BoundedExecutor)
