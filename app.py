import streamlit as st
import random
import numpy as np
import folium
import osmnx as ox
import networkx as nx
from geopy.distance import geodesic
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from streamlit_folium import st_folium
import os

# ==================== CẤU HÌNH WEB APP ====================
st.set_page_config(page_title="SGTRO - Hành Trình Di Sản Sài Gòn", page_icon="🚲", layout="wide")

# ==================== DATA ĐỊA ĐIỂM (Giữ nguyên) ====================
landmarks = {
    "Nhà thờ Đức Bà": (10.7798, 106.6990), "Bưu điện Trung tâm": (10.7796, 106.6993),
    "Dinh Độc Lập": (10.7769, 106.6953), "Chợ Bến Thành": (10.7725, 106.6980),
    "Phố đi bộ Nguyễn Huệ": (10.7740, 106.7030), "Nhà hát Thành phố": (10.7765, 106.7031),
    "Bến Bạch Đằng": (10.7723, 106.7065), "Bảo tàng Mỹ thuật": (10.7698, 106.6994),
    "Chợ Tân Định": (10.7885, 106.6896), "Thảo Cầm Viên": (10.7876, 106.7053),
    "Bùi Viện": (10.7675, 106.6935), "Takashimaya": (10.7735, 106.7009),
    "Bitexco": (10.7717, 106.7044), "Cầu Ba Son": (10.7820, 106.7090),
    "Công viên Tao Đàn": (10.7758, 106.6919),
    "Hồ Con Rùa": (10.7825, 106.6958), "Bảo tàng Chứng tích Chiến tranh": (10.7795, 106.6920), 
    "Nhà thờ Tân Định": (10.7888, 106.6890), "Chùa Vĩnh Nghiêm": (10.7915, 106.6853),
    "Ga Sài Gòn": (10.7828, 106.6775), "Chợ Nguyễn Văn Trỗi": (10.7865, 106.6800),
    "Chợ Bình Tây": (10.7517, 106.6519), "Chùa Bà Thiên Hậu": (10.7540, 106.6510), 
    "Phố lồng đèn": (10.7530, 106.6600), "The Garden Mall": (10.7545, 106.6582),
    "Bệnh viện Chợ Rẫy": (10.7570, 106.6565), "Chùa Ôn Lăng": (10.7535, 106.6620),
    "Chợ hoa Hồ Thị Kỷ": (10.7670, 106.6745), "Việt Nam Quốc Tự": (10.7710, 106.6715), 
    "Vạn Hạnh Mall": (10.7715, 106.6690), "ĐH Bách Khoa": (10.7723, 106.6570),
    "SVĐ Thống Nhất": (10.7638, 106.6615), "Công viên Lê Thị Riêng": (10.7820, 106.6640),
    "Landmark 81": (10.7952, 106.7218), "Cầu Thủ Thiêm": (10.7870, 106.7175), 
    "KDL Văn Thánh": (10.8030, 106.7167), "Chợ Bà Chiểu": (10.8038, 106.7056),
    "Lăng Ông Bà Chiểu": (10.8025, 106.6970)
}

tours = {
    "Ký Ức Vương Cung & Dinh Độc Lập": {"en": "Memories of the Basilica & Palace", "points": ["Nhà thờ Đức Bà", "Bưu điện Trung tâm", "Dinh Độc Lập"], "price": 180000},
    "Gió Lộng Bến Bạch Đằng": {"en": "Breeze of Bach Dang Pier", "points": ["Nhà hát Thành phố", "Phố đi bộ Nguyễn Huệ", "Bến Bạch Đằng"], "price": 180000},
    "Sài Gòn Phố Thị Không Ngủ": {"en": "Sleepless Saigon Metropolis", "points": ["Chợ Bến Thành", "Bùi Viện", "Bitexco"], "price": 200000},
    "Sắc Màu Mỹ Thuật Cổ": {"en": "Colors of Fine Arts", "points": ["Bảo tàng Mỹ thuật", "Chợ Bến Thành", "Dinh Độc Lập"], "price": 190000},
    "Bóng Cây Di Sản": {"en": "Heritage Tree Shadows", "points": ["Công viên Tao Đàn", "Dinh Độc Lập", "Bưu điện Trung tâm"], "price": 180000},
    "Dấu Ấn Phồn Hoa": {"en": "Marks of Prosperity", "points": ["Takashimaya", "Phố đi bộ Nguyễn Huệ", "Bitexco"], "price": 200000},
}

translations = {
    "vi": {
        "title": "SGTRO - Hành Trình Di Sản Sài Gòn",
        "select_tour": "📍CHỌN LỘ TRÌNH KHÁM PHÁ:",
        "select_vehicle": "🚲PHƯƠNG TIỆN TRẢI NGHIỆM:",
        "btn_calc": "XÁC NHẬN ĐẶT TOUR & KHỞI HÀNH",
        "btn_loading": "Đang phân tích đường đi...",
        "route": "📍Lộ trình:", "distance": "🛣 Cung đường:", "time": "⏱ Thời gian dự kiến:",
        "weather": "🌤 Thời tiết:", "traffic": "🚦Giao thông:", "total": "TỔNG",
        "note": "(Bao gồm phụ phí điều kiện môi trường tự động)",
        "v1": "Xích lô cung đình", "v2": "Xe đạp cổ Pháp", "v3": "Xe lam Sài Gòn",
        "hr": "giờ", "min": "phút"
    },
    "en": {
        "title": "SGTRO - Saigon Heritage Journey",
        "select_tour": "📍SELECT DISCOVERY ROUTE:",
        "select_vehicle": "🚲CHOOSE YOUR VEHICLE:",
        "btn_calc": "CONFIRM BOOKING & DEPART",
        "btn_loading": "Analyzing route...",
        "route": "📍Route:", "distance": "🛣 Distance:", "time": "⏱ Est. Time:",
        "weather": "🌤 Weather:", "traffic": "🚦 Traffic:", "total": "TOTAL",
        "note": "(Includes dynamic environmental surcharges)",
        "v1": "Imperial Cyclo", "v2": "Classic French Bicycle", "v3": "Saigon Lambro",
        "hr": "hrs", "min": "mins"
    }
}

# ==================== FUZZY LOGIC ====================
weather_in = ctrl.Antecedent(np.arange(0, 11, 1), 'weather')
traffic_in = ctrl.Antecedent(np.arange(0, 11, 1), 'traffic')
multiplier_out = ctrl.Consequent(np.arange(1.0, 2.1, 0.1), 'multiplier')
weather_in.automf(3, names=['xau', 'binh_thuong', 'dep'])
traffic_in.automf(3, names=['ket', 'dong', 'thoang'])
multiplier_out.automf(3, names=['thap', 'vua', 'cao'])
r1 = ctrl.Rule(weather_in['xau'] | traffic_in['ket'], multiplier_out['cao'])
r2 = ctrl.Rule(weather_in['dep'] & traffic_in['thoang'], multiplier_out['thap'])
r3 = ctrl.Rule(weather_in['binh_thuong'], multiplier_out['vua'])
pricing_sim = ctrl.ControlSystemSimulation(ctrl.ControlSystem([r1, r2, r3]))

def get_random_conditions(lang):
    if lang == "vi":
        weathers = ["Nắng nhẹ", "Nắng gắt ☀", "Nhiều mây ☁", "Âm u", "Mưa rào nhẹ", "Mưa to dông lốc ⛈"]
        traffics = ["Kẹt xe nghiêm trọng", "Đông đúc, di chuyển chậm", "Thông thoáng"]
    else:
        weathers = ["Light Sun", "Scorching Sun ☀", "Cloudy ☁", "Overcast", "Light Rain", "Thunderstorm ⛈"]
        traffics = ["Severe Traffic Jam", "Crowded, Slow Moving", "Clear & Smooth"]

    rand_w = random.choice(weathers)
    if "Nắng" in rand_w or "Sun" in rand_w: 
        w_score = random.randint(7, 10); temp = random.randint(32, 36)
    elif "Mưa" in rand_w or "Rain" in rand_w or "Thunder" in rand_w: 
        w_score = random.randint(1, 4); temp = random.randint(24, 27)
    else: 
        w_score = random.randint(5, 7); temp = random.randint(28, 31)

    t_score = random.randint(2, 9)
    if t_score <= 3: t_desc = traffics[0]; color = "red"
    elif t_score <= 6: t_desc = traffics[1]; color = "orange"
    else: t_desc = traffics[2]; color = "green"
    
    return w_score, t_score, temp, rand_w, t_desc, color

# ==================== CACHE OSMNX GRAPH ====================
# Tải bản đồ ngầm 1 lần duy nhất để web không bị đơ
@st.cache_resource
def load_map_graph():
    ox.settings.log_console = False
    ox.settings.use_cache = True
    return ox.graph_from_point((10.7769, 106.6953), dist=5000, network_type='drive')

G = load_map_graph()

# ==================== GIAO DIỆN WEB ====================
if 'lang' not in st.session_state:
    st.session_state.lang = 'vi'

def toggle_language():
    st.session_state.lang = "en" if st.session_state.lang == "vi" else "vi"

t = translations[st.session_state.lang]

# Chia layout 1 bên Menu, 1 bên Bản đồ
st.sidebar.button("󰑜 Tiếng Việt / English", on_click=toggle_language)
if os.path.exists("logo1.png"):
    st.sidebar.image("logo1.png", use_container_width=True)

st.sidebar.markdown(f"**{t['select_tour']}**")
tour_list = list(tours.keys())
tour_display = [k if st.session_state.lang == "vi" else tours[k]["en"] for k in tour_list]
selected_tour_name = st.sidebar.selectbox("Tour", tour_display, label_visibility="collapsed")
selected_tour_key = tour_list[tour_display.index(selected_tour_name)]

st.sidebar.markdown(f"**{t['select_vehicle']}**")
veh_options = [t["v1"], t["v2"], t["v3"]]
selected_veh = st.sidebar.selectbox("Vehicle", veh_options, label_visibility="collapsed")
vehicle_idx = veh_options.index(selected_veh)

if st.sidebar.button(t["btn_calc"], use_container_width=True, type="primary"):
    with st.spinner(t["btn_loading"]):
        tour = tours[selected_tour_key]
        coords = [landmarks[p] for p in tour["points"]]
        dist = round(sum(geodesic(coords[i], coords[i+1]).km for i in range(len(coords)-1)), 2)
        
        speed = 15 if vehicle_idx == 2 else 8
        total_mins = int((dist / speed) * 60 + len(tour["points"]) * 15)
        time_str = f"{total_mins // 60} {t['hr']} {total_mins % 60} {t['min']}" if total_mins >= 60 else f"{total_mins} {t['min']}"
        
        w_sc, t_sc, temp, w_desc, t_desc, color = get_random_conditions(st.session_state.lang)
        pricing_sim.input['weather'] = w_sc
        pricing_sim.input['traffic'] = t_sc
        pricing_sim.compute()
        fuzzy_mult = pricing_sim.output['multiplier']
        
        per_km_fee = 25000 if vehicle_idx == 2 else 15000
        raw_price = tour['price'] + (dist * per_km_fee)
        final_price = int((raw_price * fuzzy_mult) / 1000) * 1000 

        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"<h3 style='color: #8B2520;'>{selected_tour_name.upper()}</h3>", unsafe_allow_html=True)
            st.write(f"**{t['route']}** {' ➔ '.join(tour['points'])}")
            st.write(f"**{t['distance']}** {dist} km")
            st.write(f"**{t['time']}** {time_str}")
            
            st.info(f"**{t['weather']}** {w_desc} ({temp}°C)\n\n**{t['traffic']}** {t_desc}")
            
            st.markdown(f"<h3 style='color: #123C42;'>{t['total']}: {final_price:,} VNĐ</h3>", unsafe_allow_html=True)
            st.caption(t['note'])

        with col2:
            full_route = []
            try:
                for i in range(len(coords) - 1):
                    orig = ox.distance.nearest_nodes(G, coords[i][1], coords[i][0])
                    dest = ox.distance.nearest_nodes(G, coords[i+1][1], coords[i+1][0])
                    route = nx.shortest_path(G, orig, dest, weight="length")
                    if route: full_route += route[:-1]
                full_route.append(dest)
                route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in full_route]
            except nx.NetworkXNoPath:
                route_coords = coords

            m = folium.Map(location=coords[0], zoom_start=14)
            for i, name in enumerate(tour["points"]):
                icon_color = "green" if i==0 else "red" if i==len(tour["points"])-1 else "blue"
                folium.Marker(
                    landmarks[name], 
                    popup=folium.Popup(f"<b>{name}</b>", max_width=200), 
                    icon=folium.Icon(color=icon_color, icon="info-sign")
                ).add_to(m)
                
            folium.PolyLine(route_coords, color=color, weight=7, opacity=0.85).add_to(m)
            
            # Thêm returned_objects=[] để chặn bản đồ gửi tín hiệu gây reset app
            st_folium(m, width=700, height=500, returned_objects=[])
else:
    st.title(t["title"])
    st.write("👈 Hãy chọn tour bên menu trái để bắt đầu tính toán lộ trình!")