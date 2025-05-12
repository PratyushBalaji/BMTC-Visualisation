import requests
import streamlit as st
import folium
from streamlit_folium import st_folium

SEARCH_URL = "https://bmtcmobileapi.karnataka.gov.in/WebAPI/SearchRoute_v2"
DETAILS_URL = "https://bmtcmobileapi.karnataka.gov.in/WebAPI/SearchByRouteDetails_v4"

def get_route_suggestions(query):
    headers = {"Content-Type": "application/json", "lan": "en"}
    body = {"routetext": query}
    res = requests.post(SEARCH_URL, json=body, headers=headers).json()
    return res.get("data", [])

def get_route_data(route_id):
    headers = {"lan": "en", "deviceType": "WEB"}
    body = {"routeid": route_id, "servicetypeid": 0}
    res = requests.post(DETAILS_URL, json=body, headers=headers).json()
    return res.get("up", {}).get("data", []), res.get("up", {}).get("mapData", [])

def render_map(center, stops, buses):
    m = folium.Map(location=center, zoom_start=st.session_state.get("zoom", 13))

    for stop in stops:
        folium.Marker(
            [stop['centerlat'], stop['centerlong']],
            popup=f"Stop: {stop['stationname']}",
            icon=folium.Icon(color='blue', icon='bus', prefix='fa')
        ).add_to(m)

    for bus in buses:
        folium.Marker(
            [bus['centerlat'], bus['centerlong']],
            popup=(
                f"Bus: {bus['vehiclenumber']}<br>"
                f"ETA: {bus.get('eta', 'N/A')}<br>"
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
    if "map_state" not in st.session_state:
        st.session_state.map_state = None

    route_query = st.text_input("Enter bus route number", key="route_query")

    if route_query:
        suggestions = get_route_suggestions(route_query)
        options = [f"{r['routeno']} (ID: {r['routeparentid']})" for r in suggestions]
        selected_option = st.selectbox("Matching Routes", options, key="route_select")

        if st.button("Go!"):
            index = options.index(selected_option)
            selected_route = suggestions[index]
            st.session_state.selected_route = selected_route

            route_id = selected_route["routeparentid"]
            stops, buses = get_route_data(route_id)
            st.session_state.stops = stops
            st.session_state.buses = buses

    if st.session_state.stops:
        st.subheader(f"Map for Route: {st.session_state.selected_route['routeno']}")
        center = [st.session_state.stops[0]['centerlat'], st.session_state.stops[0]['centerlong']]

        map_obj = render_map(center, st.session_state.stops, st.session_state.buses)

        map_data = st_folium(map_obj, key="bmtcmap", width=1200, height=700)

        if map_data and "center" in map_data:
            st.session_state.zoom = map_data.get("zoom", 13)
            st.session_state.map_center = [map_data["center"]["lat"], map_data["center"]["lng"]]

        if st.button("🔄 Refresh Bus Positions"):
            route_id = st.session_state.selected_route["routeparentid"]
            _, buses = get_route_data(route_id)
            st.session_state.buses = buses
            st.experimental_rerun()

if __name__ == "__main__":
    main()