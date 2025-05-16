import requests
import streamlit as st
import folium
from streamlit_folium import st_folium

SEARCH_URL = "https://bmtcmobileapi.karnataka.gov.in/WebAPI/SearchRoute_v2"
DETAILS_URL = "https://bmtcmobileapi.karnataka.gov.in/WebAPI/SearchByRouteDetails_v4"
FARE_ROUTES_URL = "https://bmtcmobileapi.karnataka.gov.in/WebAPI/GetFareRoutes"

def get_route_suggestions(query):
    headers = {"Content-Type": "application/json", "lan": "en"}
    body = {"routetext": query}
    res = requests.post(SEARCH_URL, json=body, headers=headers)
    print("[DEBUG] SearchRoute_v2 response:", res.status_code, res.json())
    return res.json().get("data", [])

def get_route_data(route_id):
    headers = {"lan": "en", "deviceType": "WEB"}
    body = {"routeid": route_id, "servicetypeid": 0}
    res = requests.post(DETAILS_URL, json=body, headers=headers)
    print("[DEBUG] SearchByRouteDetails_v4. Code", res.status_code)
    return res.json().get("up", {}).get("data", []), res.json().get("up", {}).get("mapData", [])

def get_routes_through_station(station_id):
    headers = {"Content-Type": "application/json"}
    body = {"fromStationId": station_id, "toStationId": station_id}
    res = requests.post(FARE_ROUTES_URL, json=body, headers=headers)
    print(f"[DEBUG] GetFareRoutes for station {station_id} response:", res.status_code, res.json())
    return res.json().get("data", [])

def render_map(center, stops, buses):
    m = folium.Map(location=center, zoom_start=st.session_state.get("zoom", 13))

    for stop in stops:
        folium.Marker(
            [stop['centerlat'], stop['centerlong']],
            popup=folium.Popup(
                html=f"<b>Stop:</b> {stop['stationname']}",
                max_width=250
            ),
            tooltip=stop['stationname'],
            icon=folium.Icon(color='blue', icon='bus', prefix='fa')
        ).add_to(m)

    for bus in buses:
        folium.Marker(
            [bus['centerlat'], bus['centerlong']],
            popup=(
                f"Bus: {bus['vehiclenumber']}<br>"
                f"Last Updated: {bus.get('lastrefreshon', 'N/A')}<br>"
                f"Service Type: {bus.get('servicetype', 'Unknown')}"
            ),
            icon=folium.Icon(color='red', icon='road', prefix='fa')
        ).add_to(m)

    return m

def main():
    st.set_page_config(page_title="BMTC Route Visualizer", layout="wide")
    st.title("BMTC Route Explorer")

    if "selected_route" not in st.session_state:
        st.session_state.selected_route = None
    if "stops" not in st.session_state:
        st.session_state.stops = []
    if "buses" not in st.session_state:
        st.session_state.buses = []
    if "zoom" not in st.session_state:
        st.session_state.zoom = 13
    if "map_center" not in st.session_state:
        st.session_state.map_center = None
    if "ready" not in st.session_state:
        st.session_state.ready = False
    if "routes_at_stop" not in st.session_state:
        st.session_state.routes_at_stop = []

    with st.form("route_form"):
        route_query = st.text_input("Enter bus route number", key="route_query")
        suggestions = get_route_suggestions(route_query) if route_query else []
        options = [f"{r['routeno']} (ID: {r['routeparentid']})" for r in suggestions]
        selected_option = st.selectbox("Matching Routes", options, key="route_select")
        submitted = st.form_submit_button("Go!")

    if submitted and selected_option:
        index = options.index(selected_option)
        selected_route = suggestions[index]
        st.session_state.selected_route = selected_route
        route_id = selected_route["routeparentid"]
        stops, buses = get_route_data(route_id)
        st.session_state.stops = stops
        st.session_state.buses = buses
        st.session_state.ready = True
        if stops:
            st.session_state.map_center = [stops[0]['centerlat'], stops[0]['centerlong']]

    if st.session_state.ready and st.session_state.stops:
        st.subheader(f"Map for Route: {st.session_state.selected_route['routeno']}")

        map_obj = render_map(
            st.session_state.map_center or [12.9716, 77.5946],
            st.session_state.stops,
            st.session_state.buses
        )

        map_data = st_folium(map_obj, key="bmtcmap", width=1200, height=700, returned_objects=[])

        refresh = st.button("🔄 Refresh Bus Positions")
        if refresh:
            route_id = st.session_state.selected_route["routeparentid"]
            _, buses = get_route_data(route_id)
            st.session_state.buses = buses
            st.session_state.ready = True

        clicked_name = map_data.get("last_object_clicked_tooltip")
        if clicked_name:
            for stop in st.session_state.stops:
                if stop["stationname"] == clicked_name:
                    clicked_id = stop["stationid"]
                    st.session_state.routes_at_stop = get_routes_through_station(clicked_id)
                    print(f"[DEBUG] User clicked on: {clicked_name} (ID: {clicked_id})")
                    break

    if st.session_state.routes_at_stop:
        st.subheader("Bus Routes Passing Through This Stop")
        route_names = list(set(r["routeno"] for r in st.session_state.routes_at_stop))
        selected_routes = st.multiselect("Select routes to explore on map:", sorted(route_names), max_selections=5)

        if selected_routes:
            for r in st.session_state.routes_at_stop:
                if r["routeno"] in selected_routes:
                    st.markdown(f"- **{r['routeno']}** — {r['routename']}")

if __name__ == "__main__":
    main()
