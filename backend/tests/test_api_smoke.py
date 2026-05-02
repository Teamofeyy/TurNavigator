from __future__ import annotations


def test_api_planning_flow(client):
    cities_response = client.get("/cities")
    assert cities_response.status_code == 200
    cities = cities_response.json()
    assert cities

    city_id = cities[0]["id"]

    profile_response = client.post(
        "/profiles",
        json={
            "interests": ["history", "food", "culture"],
            "budget_level": "medium",
            "max_budget": 15000,
            "pace": "moderate",
            "max_walking_distance_km": 8,
            "preferred_transport": "walking",
            "explanation_level": "detailed",
            "goals": ["discover_local_culture"],
            "must_have": ["coffee_break"],
            "avoid": ["stairs"],
            "compromise_strategy": "balanced",
            "trust_level": "medium",
            "accessibility_needs": ["rest_breaks"],
            "preferred_time_windows": ["morning", "evening"],
        },
    )
    assert profile_response.status_code == 201
    profile = profile_response.json()

    hotels_response = client.get(
        f"/cities/{city_id}/pois",
        params={"category": "accommodation", "limit": 20},
    )
    assert hotels_response.status_code == 200
    hotels = hotels_response.json()
    selected_hotel = hotels[0]
    hotel_location = {
        "address": selected_hotel["address"],
        "latitude": selected_hotel["latitude"],
        "longitude": selected_hotel["longitude"],
        "name": selected_hotel["name"],
        "poi_id": selected_hotel["id"],
    }

    trip_response = client.post(
        "/trip-requests",
        json={
            "city_id": city_id,
            "profile_id": profile["id"],
            "days_count": 2,
            "daily_time_limit_hours": 8,
            "selected_interests": ["history", "food", "culture"],
            "constraints": {
                "include_accommodation": False,
                "return_to_start": True,
            },
            "start_location": hotel_location,
            "end_location": hotel_location,
        },
    )
    assert trip_response.status_code == 201
    trip_request = trip_response.json()
    assert trip_request["profile_id"] == profile["id"]
    assert trip_request["start_location"]["poi_id"] == selected_hotel["id"]

    recommendations_response = client.post(
        "/recommendations/generate",
        json={
            "trip_request_id": trip_request["id"],
            "limit": 6,
            "include_accommodation": False,
            "include_categories": None,
            "exclude_categories": [],
        },
    )
    assert recommendations_response.status_code == 200
    recommendations = recommendations_response.json()
    assert recommendations["recommendation_run_id"] > 0
    assert recommendations["recommendations"]

    route_response = client.post(
        "/routes/build",
        json={
            "trip_request_id": trip_request["id"],
            "poi_ids": [item["poi_id"] for item in recommendations["recommendations"][:4]],
            "max_points": 4,
            "optimize_order": True,
            "strict_constraints": True,
            "start_location": hotel_location,
            "end_location": hotel_location,
        },
    )
    assert route_response.status_code == 201
    route = route_response.json()
    assert route["start_location"]["poi_id"] == selected_hotel["id"]
    assert route["end_location"]["poi_id"] == selected_hotel["id"]
    assert route["return_leg_travel_minutes"] >= 0

    feedback_response = client.post(
        "/feedback",
        json={
            "route_id": route["id"],
            "rating": 4,
            "comment": "Маршрут выглядит реалистично.",
        },
    )
    assert feedback_response.status_code == 201
    feedback = feedback_response.json()
    assert feedback["route_id"] == route["id"]

    decision_logs_response = client.get("/decision-logs", params={"limit": 10})
    assert decision_logs_response.status_code == 200
    decision_logs = decision_logs_response.json()
    assert len(decision_logs) >= 4
    assert {entry["event_type"] for entry in decision_logs} >= {
        "trip_request_created",
        "recommendations_generated",
        "route_built",
        "feedback_received",
    }
