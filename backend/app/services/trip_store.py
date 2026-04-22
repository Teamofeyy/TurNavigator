from datetime import UTC, datetime
from itertools import count

from app.schemas.planning import TripRequestCreate, TripRequestResponse

_trip_id_sequence = count(1)
_trip_requests: dict[int, TripRequestResponse] = {}


def create_trip_request(payload: TripRequestCreate) -> TripRequestResponse:
    trip_request_id = next(_trip_id_sequence)
    trip_request = TripRequestResponse(
        id=trip_request_id,
        created_at=datetime.now(UTC),
        **payload.model_dump(),
    )
    _trip_requests[trip_request_id] = trip_request
    return trip_request


def get_trip_request(trip_request_id: int) -> TripRequestResponse | None:
    return _trip_requests.get(trip_request_id)
