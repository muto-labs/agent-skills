"""Calculate exact quarter length and transparent weekly-target conversions."""
import argparse
from datetime import date, timedelta
import json
import math


def calculate(year, quarter, per_week=None):
    if quarter not in (1, 2, 3, 4):
        raise ValueError('Quarter must be 1-4')
    start = date(year, (quarter - 1) * 3 + 1, 1)
    after = date(year + 1, 1, 1) if quarter == 4 else date(year, quarter * 3 + 1, 1)
    days = (after - start).days
    result = {'year': year, 'quarter': quarter, 'start': start.isoformat(), 'end': (after - timedelta(days=1)).isoformat(), 'days': days, 'full_weeks': days // 7, 'extra_days': days % 7, 'week_equivalent': days / 7}
    if per_week is not None:
        if not math.isfinite(per_week) or per_week < 0:
            raise ValueError('Weekly frequency must be finite and nonnegative')
        value = days * per_week / 7
        result.update(per_week=per_week, exact_total=value, rounded_down=math.floor(value), rounded_up=math.ceil(value), decision='Choose a whole-number target with the user; rounding is not automatic acceptance.')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('year', type=int)
    parser.add_argument('quarter', type=int)
    parser.add_argument('--per-week', type=float)
    args = parser.parse_args()
    try:
        print(json.dumps(calculate(args.year, args.quarter, args.per_week), indent=2))
    except ValueError as exc:
        parser.exit(1, f'Calculation failed: {exc}\n')
