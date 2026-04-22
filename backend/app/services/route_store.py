from itertools import count

from app.schemas.route import RoutePlanResponse

_route_id_sequence = count(1)
_routes: dict[int, RoutePlanResponse] = {}


def save_route(route: RoutePlanResponse) -> RoutePlanResponse:
    route_id = next(_route_id_sequence)
    saved_route = route.model_copy(update={"id": route_id})
    _routes[route_id] = saved_route
    return saved_route


def get_route(route_id: int) -> RoutePlanResponse | None:
    return _routes.get(route_id)
