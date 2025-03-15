import requests
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# Mapping city name to airport code
CITY_TO_AIRPORT = {
    "hà nội": "HAN",
    "ha noi": "HAN",
    "hanoi": "HAN",
    "tp.hcm": "SGN",
    "hồ chí minh": "SGN",
    "ho chi minh": "SGN",
    "sài gòn": "SGN",
    "sai gon": "SGN",
    "đà nẵng": "DAD",
    "da nang": "DAD",
    "nha trang": "CXR",
    # Add more mappings as needed
}

class ActionSearchFlight(Action):
    def name(self) -> Text:
        return "action_search_flight"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Retrieve slots
        dep_city = tracker.get_slot("departure_city")
        arr_city = tracker.get_slot("arrival_city")
        dep_date = tracker.get_slot("departure_date")
        ticket_class = tracker.get_slot("ticket_class")
        adults = tracker.get_slot("number_adults")
        children = tracker.get_slot("number_children")
        infants = tracker.get_slot("number_infants")

        print(f"Departure City: {dep_city}, Arrival City: {arr_city}, Departure Date: {dep_date}, number of Adults: {adults}, Number of Children: {children}, Number of Infants: {infants}")

        # Validate city codes
        dep_code = CITY_TO_AIRPORT.get(dep_city.lower(), None) if dep_city else None
        arr_code = CITY_TO_AIRPORT.get(arr_city.lower(), None) if arr_city else None
        if not dep_code:
            dispatcher.utter_message(response="utter_ask_departure_city")
            return []
        if not arr_code:
            dispatcher.utter_message(response="utter_ask_arrival_city")
            return []
        if not dep_date:
            dispatcher.utter_message(response="utter_ask_departure_date")
            return []
        if not ticket_class:
            dispatcher.utter_message(response="utter_ask_ticket_class")
            return []
        if not adults:
            dispatcher.utter_message(response="utter_ask_number_adults")
            return []
        if not children:
            dispatcher.utter_message(response="utter_ask_number_children")
            return []
        if not infants:
            dispatcher.utter_message(response="utter_ask_number_infants")
            return []
        
        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(dep_date, "%Y-%m-%d")
        except ValueError:
            dispatcher.utter_message(text="Ngày khởi hành không hợp lệ. Vui lòng nhập lại.")
            return []
        

        # Prepare API request
        url = "https://api.dcwizard.net/flight_api/flight/search_flight/"
        payload = {
            "departure_airport_code": dep_code,
            "arrival_airport_code": arr_code,
            "departure_time": dep_date,
            "ticket_classes": ticket_class,
            "number_adults": adults,
            "number_children": children,
            "number_infants": infants
        }

        try:
            resp = requests.post(url, json=payload, timeout=10)
            flights = resp.json().get("data", [])
            if not flights:
                dispatcher.utter_message(text="Không tìm thấy chuyến bay phù hợp.")
                return []
            # Sort by departure_time and pick nearest
            flights_sorted = sorted(flights, key=lambda x: x.get("departure_time", ""))
            nearest = flights_sorted[0]
            info = (
                f"Chuyến bay gần nhất: {nearest.get('flight_number', '')} "
                f"(hãng {nearest.get('airline', '')}) khởi hành lúc {nearest.get('departure_time', '')}, "
                f"giá {nearest.get('price', '')}"
            )
            dispatcher.utter_message(response="utter_flight_result", flight_info=info)
        except Exception:
            dispatcher.utter_message(text="Có lỗi khi tìm chuyến bay. Vui lòng thử lại sau.")
        return []