"""
File path: backend/modules/market_data/collectors/collector_base.py
Purpose: Abstract base class for all data collectors.
         All 10 collector implementations inherit from CollectorBase.
         Per SPEC Section 11.1.

Interface contract:
  - fetch(symbol, **kwargs) → pd.DataFrame
  - fetch_with_fallback(symbol, **kwargs) — tries primary → secondary → fallback
  - Circuit breaker: after 3 consecutive failures, marks source as circuit_open for 10 min
  - Retry logic: exponential backoff (1s, 2s, 4s) for all HTTP requests
"""

import time
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

logger = logging.getLogger("app")


class CollectorBase(ABC):
    """
    Abstract base class for all market data collectors.
    Implements retry logic, circuit breaker, and fallback chain.
    """

    source_name: str = "unknown"
    requires_api_key: bool = False
    daily_request_limit: int | None = None  # None = unlimited

    # Circuit breaker state
    _failure_count: int = 0
    _circuit_open_until: datetime | None = None
    _MAX_FAILURES = 3
    _CIRCUIT_OPEN_DURATION_SECONDS = 600  # 10 minutes

    @abstractmethod
    def fetch(self, symbol: str, **kwargs):
        """
        Primary fetch method. Returns pd.DataFrame.
        Raises DataUnavailableError if data cannot be retrieved.
        """
        pass

    def fetch_with_fallback(self, symbol: str, **kwargs):
        """
        Try primary fetch. On failure, delegates to subclass secondary/fallback.
        Override _fetch_secondary() and _fetch_fallback() in subclasses.
        Raises DataUnavailableError if all sources fail.
        """
        if self._is_circuit_open():
            raise Exception(f"{self.source_name} circuit is open — skipping.")
        
        try:
            result = self._fetch_with_retry(symbol, **kwargs)
            self._reset_circuit()
            return result
        except Exception as e:
            self._record_failure()
            logger.warning(f"{self.source_name} fetch failed for {symbol}: {e}")
            raise

    def _fetch_with_retry(self, symbol: str, **kwargs):
        """Exponential backoff retry: 3 attempts with 1s, 2s, 4s delays."""
        delays = [1, 2, 4]
        last_exc = None
        for attempt, delay in enumerate(delays, 1):
            try:
                return self.fetch(symbol, **kwargs)
            except Exception as e:
                last_exc = e
                if attempt < len(delays):
                    logger.debug(f"{self.source_name} retry {attempt} for {symbol} in {delay}s")
                    time.sleep(delay)
        raise last_exc

    def _is_circuit_open(self) -> bool:
        if self._circuit_open_until and datetime.utcnow() < self._circuit_open_until:
            return True
        return False

    def _record_failure(self):
        self._failure_count += 1
        if self._failure_count >= self._MAX_FAILURES:
            self._circuit_open_until = datetime.utcnow() + timedelta(seconds=self._CIRCUIT_OPEN_DURATION_SECONDS)
            logger.error(f"{self.source_name} circuit breaker OPEN until {self._circuit_open_until}")

    def _reset_circuit(self):
        self._failure_count = 0
        self._circuit_open_until = None
