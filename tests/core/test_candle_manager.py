from datetime import datetime, timedelta
from typing import List

import pytest
from hexital import Candle
from hexital.core.candle_manager import CandleManager
from hexital.utils.common import CalcMode
from test_candlestick import FakeType


class TestParseCandles:
    @pytest.mark.usefixtures("minimal_candles")
    def test_append_candle(self, minimal_candles):
        new_candle = minimal_candles[-1]
        manager = CandleManager()
        candles = manager._parse_candles(new_candle)

        assert candles == [
            Candle(
                open=2424,
                high=10767,
                low=13115,
                close=13649,
                volume=15750,
                indicators={"ATR": 2000, "NATR": {"nested": 2001}, "MinTR": 2002},
                sub_indicators={"SATR": 2010, "SSATR": {"nested": 2011}},
                timestamp=datetime(2023, 6, 1, 9, 19, 0),
            ),
        ]

    def test_append_list_nada(self):
        manager = CandleManager()
        candles = manager._parse_candles([])
        assert candles == []

    @pytest.mark.usefixtures("minimal_candles")
    def test_append_candle_list(self, minimal_candles):
        manager = CandleManager()
        candles = manager._parse_candles(minimal_candles)

        assert candles == minimal_candles

    @pytest.mark.usefixtures("minimal_candles")
    def test_append_candle_list_single(self, minimal_candles):
        manager = CandleManager()
        candles = manager._parse_candles([minimal_candles[-1]])

        assert candles == [
            Candle(
                open=2424,
                high=10767,
                low=13115,
                close=13649,
                volume=15750,
                indicators={"ATR": 2000, "NATR": {"nested": 2001}, "MinTR": 2002},
                sub_indicators={"SATR": 2010, "SSATR": {"nested": 2011}},
                timestamp=datetime(2023, 6, 1, 9, 19, 0),
            ),
        ]

    def test_append_dict(self):
        manager = CandleManager()
        candles = manager._parse_candles(
            {
                "open": 17213,
                "high": 2395,
                "low": 7813,
                "close": 3615,
                "volume": 19661,
                "timestamp": datetime(2023, 10, 3, 9, 0),
            }
        )

        assert candles == [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 0),
            )
        ]

    def test_append_dict_list(self):
        manager = CandleManager()
        candles = manager._parse_candles(
            [
                {
                    "open": 17213,
                    "high": 2395,
                    "low": 7813,
                    "close": 3615,
                    "volume": 19661,
                    "timestamp": datetime(2023, 10, 3, 9, 0),
                },
                {
                    "open": 1301,
                    "high": 3007,
                    "low": 11626,
                    "close": 19048,
                    "volume": 28909,
                    "timestamp": datetime(2023, 10, 3, 9, 5),
                },
            ]
        )

        assert candles == [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 0),
            ),
            Candle(
                1301,
                3007,
                11626,
                19048,
                28909,
                timestamp=datetime(2023, 10, 3, 9, 5),
            ),
        ]

    def test_append_list(self):
        manager = CandleManager()
        candles = manager._parse_candles(
            [datetime(2023, 10, 3, 9, 0), 17213, 2395, 7813, 3615, 19661]
        )

        assert candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 0))
        ]

    def test_append_list_list(self):
        manager = CandleManager()
        candles = manager._parse_candles(
            [
                [datetime(2023, 10, 3, 9, 0), 17213, 2395, 7813, 3615, 19661],
                [datetime(2023, 10, 3, 9, 5), 1301, 3007, 11626, 19048, 28909],
            ]
        )

        assert candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 0)),
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 5)),
        ]

    def test_append_invalid(self):
        manager = CandleManager()
        with pytest.raises(TypeError):
            manager._parse_candles(["Fuck", 2, 3])


class TestCandleAppend:
    @pytest.mark.usefixtures("minimal_candles")
    def test_append(self, minimal_candles):
        manager = CandleManager()
        new_candle = minimal_candles[-1]
        manager.append(new_candle)

        expected = Candle(
            open=2424,
            high=10767,
            low=13115,
            close=13649,
            volume=15750,
            timestamp=datetime(2023, 6, 1, 9, 19),
        )

        assert manager.candles == [expected]

    @pytest.mark.usefixtures("minimal_candles")
    def test_append_with_aggregation(self, minimal_candles):
        manager = CandleManager()
        new_candle = minimal_candles.pop()
        new_candle.aggregation_factor = 5
        manager.append(new_candle)

        expected = Candle(
            open=2424,
            high=10767,
            low=13115,
            close=13649,
            volume=15750,
            timestamp=datetime(2023, 6, 1, 9, 19),
        )
        expected.aggregation_factor = 5

        assert manager.candles == [expected]


class TestCandleTimeframeAppend:
    def test_default(self):
        manager = CandleManager()
        manager.append(
            [
                Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
                Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
            ]
        )
        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_default_timeframe(self):
        manager = CandleManager(timeframe=timedelta(minutes=5))
        manager.append(
            [
                Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
                Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
            ]
        )
        assert manager.candles == [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 5),
                timeframe=timedelta(minutes=5),
            ),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_candle_timeframe_append(self):
        manager = CandleManager(
            [Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5))],
        )
        manager.append(
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        )
        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_candle_timeframe_append_same(self):
        manager = CandleManager(
            [Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5))],
            timeframe=timedelta(minutes=5),
        )
        manager.append(
            Candle(
                14842,
                14842,
                14831,
                14835,
                540,
                timestamp=datetime(2023, 10, 3, 9, 10),
                timeframe=timedelta(minutes=5),
            ),
        )
        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_candle_timeframe_append_up(self):
        manager = CandleManager(
            [Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5))],
            timeframe=timedelta(minutes=5),
        )
        manager.append(
            Candle(
                14842,
                14842,
                14831,
                14835,
                540,
                timestamp=datetime(2023, 10, 3, 9, 6),
                timeframe=timedelta(minutes=1),
            ),
        )
        assert manager.candles == [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 5),
                timeframe=timedelta(minutes=5),
            ),
            Candle(
                14842,
                14842,
                14831,
                14835,
                540,
                timestamp=datetime(2023, 10, 3, 9, 10),
            ),
        ]

    def test_candle_timeframe_append_up_two(self):
        manager = CandleManager(
            [Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5))],
            timeframe=timedelta(minutes=5),
        )
        manager.append(
            Candle(
                14842,
                14842,
                14831,
                15000,
                540,
                timestamp=datetime(2023, 10, 3, 9, 6),
                timeframe=timedelta(minutes=1),
            ),
        )
        manager.append(
            Candle(
                15000,
                16000,
                14831,
                16000,
                540,
                timestamp=datetime(2023, 10, 3, 9, 7),
                timeframe=timedelta(minutes=1),
            ),
        )

        expected = [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 5),
                timeframe=timedelta(minutes=5),
            ),
            Candle(
                14842,
                16000,
                14831,
                16000,
                1080,
                timestamp=datetime(2023, 10, 3, 9, 10),
                timeframe=timedelta(minutes=5),
            ),
        ]
        expected[0].aggregation_factor, expected[1].aggregation_factor = 1, 2
        assert manager.candles == expected

    def test_candle_timeframe_append_higher(self):
        manager = CandleManager(
            [Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5))],
            timeframe=timedelta(minutes=5),
        )
        manager.append(
            Candle(
                14842,
                14842,
                14831,
                14835,
                540,
                timestamp=datetime(2023, 10, 3, 9, 15),
                timeframe=timedelta(minutes=10),
            ),
        )
        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
        ]

    def test_append_filler(self):
        manager = CandleManager(timeframe_fill=True, timeframe=timedelta(minutes=5))
        manager.append(
            [
                Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            ]
        )
        manager.append(
            [Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 15))]
        )

        expected = [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 5),
                timeframe=timedelta(minutes=5),
            ),
            Candle(
                3615,
                3615,
                3615,
                3615,
                0,
                timestamp=datetime(2023, 10, 3, 9, 10),
                timeframe=timedelta(minutes=5),
            ),
            Candle(
                14842,
                14842,
                14831,
                14835,
                540,
                timestamp=datetime(2023, 10, 3, 9, 15),
                timeframe=timedelta(minutes=5),
            ),
        ]

        expected[1].aggregation_factor = 0

        assert manager.candles == expected


class TestCandlePrepend:
    def test_default(self):
        manager = CandleManager(
            [Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10))]
        )

        manager.prepend(
            [Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5))]
        )
        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]


class TestCandleTimeframePrepend:
    def test_default(self):
        manager = CandleManager()
        manager.append(
            [
                Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
            ]
        )
        manager.prepend(
            [Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5))]
        )
        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_default_timeframe(self):
        manager = CandleManager(
            candles=[
                Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10))
            ],
            timeframe=timedelta(minutes=5),
        )
        manager.prepend(
            [Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5))]
        )
        assert manager.candles == [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 5),
                timeframe=timedelta(minutes=5),
            ),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_candle_timeframe_prepend_resample(self):
        manager = CandleManager(
            [
                Candle(
                    15000,
                    16000,
                    14831,
                    16000,
                    540,
                    timestamp=datetime(2023, 10, 3, 9, 7),
                    timeframe=timedelta(minutes=1),
                )
            ],
            timeframe=timedelta(minutes=5),
        )
        manager.prepend(
            Candle(
                14842,
                14842,
                14831,
                15000,
                540,
                timestamp=datetime(2023, 10, 3, 9, 6),
                timeframe=timedelta(minutes=1),
            ),
        )
        manager.prepend(
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 5),
                timeframe=timedelta(minutes=1),
            )
        )

        expected = [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 5),
                timeframe=timedelta(minutes=5),
            ),
            Candle(
                14842,
                16000,
                14831,
                16000,
                1080,
                timestamp=datetime(2023, 10, 3, 9, 10),
                timeframe=timedelta(minutes=5),
            ),
        ]
        expected[0].aggregation_factor, expected[1].aggregation_factor = 1, 2

        assert manager.candles == expected

    def test_candle_timeframe_prepend_resample_filler(self):
        manager = CandleManager(
            [
                Candle(
                    15000,
                    16000,
                    14831,
                    16000,
                    540,
                    timestamp=datetime(2023, 10, 3, 9, 7),
                    timeframe=timedelta(minutes=1),
                )
            ],
            timeframe=timedelta(minutes=5),
            timeframe_fill=True,
        )
        manager.prepend(
            Candle(
                14842,
                14842,
                14831,
                15000,
                540,
                timestamp=datetime(2023, 10, 3, 9, 6),
                timeframe=timedelta(minutes=1),
            ),
        )
        manager.prepend(
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 0),
                timeframe=timedelta(minutes=1),
            )
        )

        expected = [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 0),
                timeframe=timedelta(minutes=5),
            ),
            Candle(
                3615,
                3615,
                3615,
                3615,
                0,
                timestamp=datetime(2023, 10, 3, 9, 5),
                timeframe=timedelta(minutes=5),
            ),
            Candle(
                14842,
                16000,
                14831,
                16000,
                1080,
                timestamp=datetime(2023, 10, 3, 9, 10),
                timeframe=timedelta(minutes=5),
            ),
        ]
        (
            expected[0].aggregation_factor,
            expected[1].aggregation_factor,
            expected[2].aggregation_factor,
        ) = 1, 0, 2
        assert manager.candles == expected


class TestCandleInsert:
    def test_default(self):
        manager = CandleManager(
            [Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10))]
        )

        manager.insert(
            [Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5))]
        )
        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    @pytest.mark.usefixtures("candles")
    def test_insert_mix(self, candles):
        manager = CandleManager([])

        split_one = [candles[i] for i in range(0, len(candles), +2)]
        manager.insert(split_one)

        split_two = [candles[i] for i in range(1, len(candles), +2)]
        manager.insert(split_two)
        assert manager.candles == candles


class TestCandleSort:
    def test_sort_candles(self):
        manager = CandleManager(
            [
                Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
                Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
                Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
            ]
        )

        manager.sort_candles()

        assert manager.candles == [
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_sort_candles_timeframed(self):
        manager = CandleManager(
            [
                Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
                Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
                Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
            ],
            timeframe=timedelta(minutes=5),
        )

        manager.candles.append(
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 2))
        )
        manager.sort_candles()

        assert manager.candles == [
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 2)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_sort_candles_insert(self):
        manager = CandleManager()
        manager.insert(
            [
                Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
                Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
                Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
            ]
        )
        assert manager.candles == [
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_sort_candles_insert_timeframed(self):
        manager = CandleManager(
            [
                Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
                Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
                Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
            ],
            timeframe=timedelta(minutes=5),
        )

        manager.insert(
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 2))
        )
        expected = [
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
            Candle(1301, 3007, 7813, 3615, 48570, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]
        expected[1].aggregation_factor = 2
        assert manager.candles == expected

    def test_sort_candles_append_timeframed_on_untimeframed(self):
        manager = CandleManager([])

        manager.append(
            Candle(
                1301,
                3007,
                7813,
                3615,
                48570,
                timestamp=datetime(2023, 10, 3, 9, 5),
                timeframe=timedelta(minutes=5),
            )
        )

        assert manager.candles == [
            Candle(1301, 3007, 7813, 3615, 48570, timestamp=datetime(2023, 10, 3, 9, 5)),
        ]


class TestMergingCandlesTimeFrame:
    def test_resample_candles_timeframe_empty(self):
        manager = CandleManager([], timeframe=timedelta(minutes=10))
        assert manager.candles == []

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_first(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles, timeframe=timedelta(minutes=5))

        assert manager.candles[0] == candles_T5[0]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_second(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles, timeframe=timedelta(minutes=5))
        assert manager.candles[1] == candles_T5[1]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_last(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles, timeframe=timedelta(minutes=5))
        assert manager.candles[-1] == candles_T5[-1]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_t5(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles, timeframe=timedelta(minutes=5))
        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T10")
    def test_resample_candles_t10(self, candles: List[Candle], candles_T10: List[Candle]):
        manager = CandleManager(candles, timeframe=timedelta(minutes=10))
        assert manager.candles == candles_T10

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_t5_appended_mini(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        data_input = []
        data_input.append(candles_T5[0])
        data_input.append(candles_T5[1])
        data_input.append(candles[10])

        expected = data_input
        expected[-1].timestamp = datetime(2023, 10, 3, 9, 15)

        manager = CandleManager([data_input[0]], timeframe=timedelta(minutes=5))

        for candle in data_input[1:]:
            manager.append(candle)

        assert manager.candles == expected

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_t5_appended_gap_mini(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        data_input = []
        data_input.append(candles_T5[0])
        data_input.append(candles_T5[1])
        data_input.append(candles_T5[2])

        expected = data_input
        expected.append(candles[20])
        expected[-1].timestamp = datetime(2023, 10, 3, 9, 25)

        manager = CandleManager(data_input, timeframe=timedelta(minutes=5))
        manager.append(candles[20])

        assert manager.candles == expected

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_t5_appended(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager([candles[0]], timeframe=timedelta(minutes=5))
        for candle in candles[1:]:
            manager.append(candle)

        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T10")
    def test_resample_candles_t10_appended(self, candles: List[Candle], candles_T10: List[Candle]):
        manager = CandleManager([candles[0]], timeframe=timedelta(minutes=10))
        for candle in candles[1:]:
            manager.append(candle)

        assert manager.candles == candles_T10

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_t5_multiple_resample(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        manager = CandleManager(candles, timeframe=timedelta(minutes=5))
        assert manager.candles == candles_T5

        manager.resample_candles(CalcMode.INSERT)
        assert manager.candles == candles_T5

        manager.resample_candles(CalcMode.INSERT)
        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_t5_mixed_neat(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles[:10], timeframe=timedelta(minutes=5))
        assert manager.candles == candles_T5[:2]

        manager.append(candles[10:])
        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_t5_mixed_messy(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        manager = CandleManager(candles[:7], timeframe=timedelta(minutes=5))
        manager.append(candles[7:])
        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_t5_missing_section(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        cut_candles = candles[:5] + candles[-2:]
        manager = CandleManager(cut_candles, timeframe=timedelta(minutes=5))
        assert manager.candles == [candles_T5[0], candles_T5[-1]]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_t5_missing_section_two(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        cut_candles = candles[:5] + candles[10:15]
        manager = CandleManager(cut_candles, timeframe=timedelta(minutes=5))
        assert manager.candles == [candles_T5[0], candles_T5[2]]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_t5_missing_section_three(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        data_input = []
        data_input.append(candles_T5[0])
        data_input.append(candles_T5[1])
        data_input.append(candles_T5[2])
        data_input.append(candles[20])

        expected = data_input
        expected[-1].timestamp = datetime(2023, 10, 3, 9, 25)

        manager = CandleManager(data_input, timeframe=timedelta(minutes=5))

        assert manager.candles == expected

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_t5_missing_section_messy(self):
        data_input = [
            Candle(33419.3, 33419.3, 33410.8, 33410.8, 24, timestamp=datetime(2023, 10, 3, 1, 47)),
            Candle(33411.3, 33413.8, 33406.8, 33406.8, 16, timestamp=datetime(2023, 10, 3, 1, 47)),
            Candle(33399.3, 33401.3, 33397.8, 33399.8, 9, timestamp=datetime(2023, 10, 3, 2, 59)),
            Candle(33399.3, 33399.8, 33396.8, 33397.3, 5, timestamp=datetime(2023, 10, 3, 3, 00)),
        ]
        expected = [
            Candle(
                open=33419.3,
                high=33419.3,
                low=33406.8,
                close=33406.8,
                volume=40,
                timestamp=datetime(2023, 10, 3, 1, 50),
            ),
            Candle(
                open=33399.3,
                high=33401.3,
                low=33396.8,
                close=33397.3,
                volume=14,
                timestamp=datetime(2023, 10, 3, 3, 00),
            ),
        ]
        expected[0].aggregation_factor, expected[1].aggregation_factor = 2, 2
        manager = CandleManager(data_input, timeframe=timedelta(minutes=5))
        assert manager.candles == expected

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_resample_candles_t5_missing_section_messy_append(self):
        data_input = [
            Candle(33419.3, 33419.3, 33410.8, 33410.8, 24, timestamp=datetime(2023, 10, 3, 1, 47)),
            Candle(33411.3, 33413.8, 33406.8, 33406.8, 16, timestamp=datetime(2023, 10, 3, 1, 47)),
            Candle(33399.3, 33401.3, 33397.8, 33399.8, 9, timestamp=datetime(2023, 10, 3, 2, 59)),
            Candle(33399.3, 33399.8, 33396.8, 33397.3, 5, timestamp=datetime(2023, 10, 3, 3, 00)),
        ]
        expected = [
            Candle(
                open=33419.3,
                high=33419.3,
                low=33406.8,
                close=33406.8,
                volume=40,
                timestamp=datetime(2023, 10, 3, 1, 50),
            ),
            Candle(
                open=33399.3,
                high=33401.3,
                low=33396.8,
                close=33397.3,
                volume=14,
                timestamp=datetime(2023, 10, 3, 3, 00),
            ),
        ]
        expected[0].aggregation_factor, expected[1].aggregation_factor = 2, 2
        manager = CandleManager([], timeframe=timedelta(minutes=5))

        for candle in data_input:
            manager.append(candle)

        assert manager.candles == expected


@pytest.mark.usefixtures("candles", "candles_T5")
def test_resample_candles_t5_missing_section_fill(candles_T5: List[Candle]):
    cut_candles = [candles_T5[0]] + [candles_T5[2]]

    filler = Candle(
        candles_T5[0].close,
        candles_T5[0].close,
        candles_T5[0].close,
        candles_T5[0].close,
        0,
        timestamp=candles_T5[0].timestamp + timedelta(minutes=5),
    )
    filler.aggregation_factor = 0

    manager = CandleManager(cut_candles, timeframe=timedelta(minutes=5), timeframe_fill=True)
    assert manager.candles == [
        candles_T5[0],
        filler,
        candles_T5[2],
    ]


@pytest.mark.usefixtures("candles", "candles_T5")
def test_resample_candles_t5_missing_section_fill_all(candles_T5: List[Candle]):
    cut_candles = [candles_T5[0]] + [candles_T5[-1]]

    filler_candles = []
    for i in range(len(candles_T5) - 2):
        filler_candles.append(
            Candle(
                candles_T5[0].close,
                candles_T5[0].close,
                candles_T5[0].close,
                candles_T5[0].close,
                0,
                timestamp=candles_T5[0].timestamp + (timedelta(minutes=5) * (i + 1)),
            )
        )
        filler_candles[-1].aggregation_factor = 0

    manager = CandleManager(cut_candles, timeframe=timedelta(minutes=5), timeframe_fill=True)

    assert manager.candles == [candles_T5[0]] + filler_candles + [candles_T5[-1]]


@pytest.mark.usefixtures("candles", "candles_T5")
def test_resample_candles_t5_missing_section_fill_all_extra(
    candles: List[Candle], candles_T5: List[Candle]
):
    cut_candles = candles[:5] + candles[-2:]

    blank_candle = candles_T5[0].clean_copy()
    blank_candle.open = blank_candle.close
    blank_candle.high = blank_candle.close
    blank_candle.low = blank_candle.close
    blank_candle.volume = 0
    blank_candle.aggregation_factor = 0

    filler_candles = []
    for i in range(99):
        blank_candle.timestamp += timedelta(minutes=5)
        filler_candles.append(blank_candle.clean_copy())

    manager = CandleManager(cut_candles, timeframe=timedelta(minutes=5), timeframe_fill=True)

    assert manager.candles == [candles_T5[0]] + filler_candles + [candles_T5[-1]]


class TestCandleConversion:
    @pytest.mark.usefixtures("minimal_candles", "candles_candlesticks_T5_expected")
    def test_candlestick_timeframe(
        self, minimal_candles: List[Candle], candles_candlesticks_T5_expected: List[Candle]
    ):
        manager = CandleManager(
            minimal_candles, timeframe=timedelta(minutes=5), candlestick=FakeType()
        )

        assert manager.candles == candles_candlesticks_T5_expected

    @pytest.mark.usefixtures("minimal_candles", "candles_candlesticks_T5_expected")
    def test_candlestick_timeframe_multi_convert(
        self, minimal_candles: List[Candle], candles_candlesticks_T5_expected: List[Candle]
    ):
        manager = CandleManager(
            minimal_candles, timeframe=timedelta(minutes=5), candlestick=FakeType()
        )
        manager.candlestick_conversion(CalcMode.INSERT)
        manager.candlestick_conversion(CalcMode.INSERT)

        assert manager.candles == candles_candlesticks_T5_expected

    @pytest.mark.usefixtures("minimal_candles", "candles_candlesticks_T5_expected")
    def test_candlestick_timeframe_resample_messy(
        self, minimal_candles: List[Candle], candles_candlesticks_T5_expected: List[Candle]
    ):
        manager = CandleManager(
            minimal_candles[:3], timeframe=timedelta(minutes=5), candlestick=FakeType()
        )

        manager.append(minimal_candles[3:])

        assert manager.candles == candles_candlesticks_T5_expected
