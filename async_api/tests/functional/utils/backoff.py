import time


def backoff(func):
    def inner(
        *args,
        sleep_time: float = 0.1,
        factor: int = 2,
        border_sleep_time: int = 10,
        **kwargs,
    ):
        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if (sleep_time := sleep_time * (2**factor)) >= border_sleep_time:
                    sleep_time = border_sleep_time
                time.sleep(sleep_time)

    return inner
