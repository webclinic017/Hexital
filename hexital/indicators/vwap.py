from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional

from hexital.core.indicator import Indicator, Managed, NestedSource
from hexital.exceptions import InvalidConfiguration
from hexital.utils.timeframe import (
    TimeFrame,
    convert_timeframe_to_timedelta,
    round_down_timestamp,
    timedelta_to_str,
    timeframe_validation,
)


@dataclass(kw_only=True)
class VWAP(Indicator[float]):
    """Volume-Weighted Average Price - VWAP

    The volume-weighted average price is a technical analysis indicator
    used on intraday charts that resets at the start of every new trading session.

    Sources:
        https://www.investopedia.com/terms/v/vwap.asp

    Output type: `float`

    Args:
        anchor (Optional[str | TimeFrame | timedelta | int]): How to anchor VWAP, Depends on the index values, uses TimeFrame
    """

    _name: str = field(init=False, default="VWAP")
    anchor: Optional[str | TimeFrame | timedelta | int] = "D"

    def _generate_name(self) -> str:
        return f"{self._name}_{timedelta_to_str(self.anchor)}"

    def _validate_fields(self):
        if not timeframe_validation(self.anchor):
            raise InvalidConfiguration(f"Anchor is Invalid: {self.anchor}")

        self.anchor = convert_timeframe_to_timedelta(self.anchor)

    def _initialise(self):
        self.data = self.add_managed_indicator(Managed())

    def _calculate_reading(self, index: int) -> float:
        candle = self.candles[index]

        current_anchor = round_down_timestamp(self.reading("timestamp"), self.anchor).timestamp()
        prev_anchor = self.prev_reading(NestedSource(self.data, "active_anchor"))
        typical_price = (candle.high + candle.low + candle.close) / 3.0

        if prev_anchor != current_anchor:
            pv = 0
            vol = 0
        else:
            pv = self.prev_reading(NestedSource(self.data, "pv"), 0.0)
            vol = self.prev_reading(NestedSource(self.data, "vol"), 0.0)

        pv = pv + (candle.volume * typical_price)
        vol = vol + candle.volume

        self.data.set_reading({"pv": pv, "vol": vol, "active_anchor": current_anchor})

        return pv / vol
