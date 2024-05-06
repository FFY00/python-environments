import concurrent.futures
import dataclasses
import sys

from collections.abc import Collection
from typing import Any, Callable, Generic, Iterator, TypeVar


if sys.version_info < (3, 11):
    from exceptiongroup import ExceptionGroup


_T = TypeVar('_T')


@dataclasses.dataclass
class Task(Generic[_T]):
    userdata: _T
    fn: Callable[..., None]
    args: Collection[Any] = ()
    kwargs: dict[str, Any] = dataclasses.field(default_factory=dict)


def run_tasks(tasks: Task[_T], fast_fail: bool = True) -> Iterator[tuple[bool, Task[_T]]]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_task_map = {
            executor.submit(task.fn, *task.args, *task.kwargs): task
            for task in tasks
        }

        for future in concurrent.futures.as_completed(future_to_task_map):
            if future.exception():
                if fast_fail:
                    executor.shutdown(cancel_futures=True)
                yield False, future_to_task_map[future]
                if fast_fail:
                    break
            elif not future.cancelled():
                yield True, future_to_task_map[future]

    exceptions = [
        future.exception()
        for future in future_to_task_map
        if future.done() and not future.cancelled() and future.exception()
    ]
    if exceptions:
        raise ExceptionGroup('failed to run tasks', exceptions)
