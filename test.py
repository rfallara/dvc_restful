from typing import List
from datetime import datetime
from models import Trip


def test(d: datetime, l: List, trip: Trip) -> int:
    d.strftime("%Y-%m-%d")
    l.append(d)
    trip.notes = l
    return 0


test(datetime.today(), {}, "hello")


