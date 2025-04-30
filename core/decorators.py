import random
import time

import allure

from core.logger import Logger

logger = Logger(debug=True).get_logger(name="api_client")


def retry_on_failure(
        max_retries: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        retry_statuses: tuple = (500, 502, 503, 504),
):
    """
    Retry decorator for API request methods.

    Retries a failed request if the response status code is in the given retryable statuses.
    Uses exponential backoff with jitter.

    :param max_retries: Maximum number of retry attempts before giving up.
    :param delay: Initial delay in seconds before the first retry.
    :param backoff_factor: Multiplier to apply after each retry (controls backoff rate).
    :param retry_statuses: HTTP status codes that should trigger a retry.
    :return: Wrapped function with retry logic applied.
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            retries = 0
            current_delay = delay

            while True:
                response = func(self, *args, **kwargs)

                # Return response immediately if not in retryable statuses
                if response.status not in retry_statuses:
                    return response

                retries += 1
                if retries > max_retries:
                    logger.error(
                        f"Maximum retries {max_retries} exhausted for {func.__name__}"
                    )
                    break

                # Log retry attempt
                logger.warning(
                    f"Received status {response.status} on {func.__name__}, "
                    f"retrying {retries}/{max_retries}, waiting {current_delay:.2f} seconds..."
                )

                # Attach retry details to Allure report
                allure.attach(
                    body=(
                        f"Retry {retries}/{max_retries}: status {response.status}, "
                        f"retrying after {current_delay:.2f} seconds"
                    ),
                    name=f"Retry attempt {retries}",
                    attachment_type=allure.attachment_type.TEXT,
                )

                # Wait before next retry with jitter
                time.sleep(current_delay)
                current_delay *= backoff_factor * (1 + random.uniform(0, 0.1))

            return response  # Final (failed) response

        return wrapper

    return decorator
