import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from ai_helper import ask_ai
import json
import os

# 페이지 설정
st.set_page_config(page_title="Weather App", layout="wide")

# 제목
st.title("🌍 Weather App")
st.markdown("지도를 통해 지역별 날씨를 확인하세요")

# 데이터 로드 함수
@st.cache_data
def load_data():
    # 현재 스크립트의 디렉토리 기준으로 CSV 파일 경로 설정
    csv_path = os.path.join(os.path.dirname(__file__), "datalog.csv")
    try:
        # UTF-8로 먼저 시도
        df = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        # UTF-8 실패시 cp949로 시도
        df = pd.read_csv(csv_path, encoding='cp949')
    return df

# 데이터 로드
df = load_data()

# 공항 코드 - 좌표 매핑 (METAR 데이터 기반)
airport_coords = {
    'KYNG': (37.2429, 127.1296, '양평'),  # Korea
    'PTRO': (-33.9461, 151.1777, 'Port Macquarie'),  # Australia
    'LSZH': (47.4647, 8.5492, 'Zurich'),  # Switzerland
    'LSZB': (46.9142, 7.4974, 'Bern'),  # Switzerland
    'LSZA': (46.8182, 8.1275, 'Altenrhein'),  # Switzerland
    'LSGG': (46.2381, 6.1092, 'Geneva'),  # Switzerland
    'KRYY': (33.2354, -95.2000, 'Rusk'),  # USA
    'KLAL': (28.5244, -81.3092, 'Lakeland'),  # USA
    'EFVA': (63.2472, 26.9023, 'Vaasa'),  # Finland
    'EFTU': (60.5242, 22.2656, 'Turku'),  # Finland
    'EFTP': (60.1699, 24.9384, 'Tampere'),  # Finland
    'EFRO': (61.1235, 28.3228, 'Savonlinna'),  # Finland
    'EFOU': (62.7592, 26.9484, 'Oulu'),  # Finland
    'EFMA': (61.8868, 25.1833, 'Mikkeli'),  # Finland
    'EFIV': (63.8688, 27.7075, 'Ivalo'),  # Finland
    'EFHK': (60.3172, 24.9633, 'Helsinki'),  # Finland
    'YMML': (-37.6733, 144.8411, 'Melbourne'),  # Australia
    'PASC': (60.4845, -152.6039, 'Anchorage'),  # USA
}

# 탭 생성
tab1, tab2, tab3, tab4 = st.tabs(["지도", "데이터", "통계", "AI 분석"])

# 탭1: 지도
with tab1:
    st.subheader("🗺️ 날씨 지도")

    # 지도 생성
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="OpenStreetMap")

    # 각 공항별로 마커 추가
    for airport_code, data in df.groupby('발표공항'):
        if airport_code in airport_coords:
            lat, lon, name = airport_coords[airport_code]
            latest = data.iloc[0]

            # 날씨 정보 추출
            temp = latest.get('온도', 'N/A')
            wind_speed = latest.get('풍속', 'N/A')
            weather = latest.get('현재일기-1', 'Clear')
            visibility = latest.get('우시정', 'Good')

            # 팝업 텍스트
            popup_text = f"""
            <b>{name} ({airport_code})</b><br>
            온도: {temp}°C<br>
            풍속: {wind_speed} KT<br>
            날씨: {weather}<br>
            시정: {visibility}
            """

            # 마커 색상 결정 (날씨에 따라)
            if pd.notna(weather) and weather in ['RA', '-RA', '+RA']:  # 강우
                color = 'blue'
            elif pd.notna(weather) and weather in ['SN', '-SN']:  # 눈
                color = 'gray'
            else:
                color = 'green'

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=color, icon='cloud'),
                tooltip=f"{name}: {temp}°C"
            ).add_to(m)

    st_folium(m, width=1200, height=600)

# 탭2: 데이터
with tab2:
    st.subheader("📊 날씨 데이터")

    # 컬럼 필터
    col1, col2 = st.columns(2)

    with col1:
        selected_airport = st.selectbox(
            "공항 선택",
            options=df['발표공항'].unique(),
            key="airport_select"
        )

    with col2:
        # 선택한 공항의 데이터만 필터
        filtered_df = df[df['발표공항'] == selected_airport].copy()

        if selected_airport in airport_coords:
            st.info(f"📍 {airport_coords[selected_airport][2]} (위도: {airport_coords[selected_airport][0]}, 경도: {airport_coords[selected_airport][1]})")

    # 주요 정보만 표시
    display_columns = ['관측시각', '발표공항', '온도', '이슬점온도', '풍향', '풍속', '돌풍', '우시정', '현재일기-1', '기압']
    display_cols = [col for col in display_columns if col in filtered_df.columns]

    st.dataframe(
        filtered_df[display_cols],
        use_container_width=True,
        height=400
    )

    # 통계 정보
    st.subheader("통계")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_temp = pd.to_numeric(filtered_df['온도'], errors='coerce').mean()
        st.metric("평균 온도", f"{avg_temp:.1f}°C" if pd.notna(avg_temp) else "N/A")

    with col2:
        avg_wind = pd.to_numeric(filtered_df['풍속'], errors='coerce').mean()
        st.metric("평균 풍속", f"{avg_wind:.1f} KT" if pd.notna(avg_wind) else "N/A")

    with col3:
        max_pressure = pd.to_numeric(filtered_df['기압'], errors='coerce').max()
        st.metric("최고 기압", f"{max_pressure:.0f}" if pd.notna(max_pressure) else "N/A")

    with col4:
        data_count = len(filtered_df)
        st.metric("데이터 개수", f"{data_count}")

# 탭3: 통계
with tab3:
    st.subheader("📈 날씨 통계")

    col1, col2 = st.columns(2)

    with col1:
        # 온도 분포
        st.write("**온도 분포 (모든 공항)**")
        temp_data = pd.to_numeric(df['온도'], errors='coerce').dropna()
        st.bar_chart(temp_data.value_counts().sort_index())

    with col2:
        # 풍속 분포
        st.write("**풍속 분포 (모든 공항)**")
        wind_data = pd.to_numeric(df['풍속'], errors='coerce').dropna()
        st.bar_chart(wind_data.value_counts().sort_index().head(20))

    # 공항별 온도 비교
    st.write("**공항별 평균 온도**")
    airport_temps = []
    for airport in df['발표공항'].unique():
        temps = pd.to_numeric(df[df['발표공항'] == airport]['온도'], errors='coerce')
        avg_temp = temps.mean()
        if pd.notna(avg_temp):
            airport_name = airport_coords.get(airport, (0, 0, airport))[2]
            airport_temps.append({'공항': airport_name, '평균온도': avg_temp})

    if airport_temps:
        temp_df = pd.DataFrame(airport_temps).sort_values('평균온도', ascending=False)
        st.bar_chart(temp_df.set_index('공항'))

# 탭4: AI 분석
with tab4:
    st.subheader("🤖 AI 날씨 분석")

    if st.button("날씨 데이터 분석"):
        with st.spinner("AI가 분석 중입니다..."):
            # 현재 데이터 요약
            summary = f"""
            현재 관측 데이터 요약:
            - 총 관측소: {df['발표공항'].nunique()}개
            - 평균 온도: {pd.to_numeric(df['온도'], errors='coerce').mean():.1f}°C
            - 평균 풍속: {pd.to_numeric(df['풍속'], errors='coerce').mean():.1f} KT
            - 최고 온도: {pd.to_numeric(df['온도'], errors='coerce').max()}°C
            - 최저 온도: {pd.to_numeric(df['온도'], errors='coerce').min()}°C

            이 데이터를 바탕으로 현재 전 지구적 날씨 패턴과 특징을 분석해주세요.
            """

            analysis = ask_ai(summary)
            st.success("분석 완료!")
            st.write(analysis)

# 사이드바
with st.sidebar:
    st.title("ℹ️ 정보")
    total_records = len(df)
    total_airports = df['발표공항'].nunique()

    st.markdown(f"""
    ### 프로젝트 설명
    - **목적**: 지도를 통해 전 세계 날씨 정보 확인
    - **데이터**: METAR 공항 관측 데이터
    - **기능**:
      - 🗺️ 인터랙티브 지도
      - 📊 상세 데이터 조회
      - 📈 통계 분석
      - 🤖 AI 기반 분석

    ### 데이터 정보
    - 관측 날짜: 2026-09-29
    - 총 관측 수: {total_records}건
    - 관측 공항: {total_airports}개

    ### 마커 색상
    - 🟢 초록색: 맑은 날씨
    - 🔵 파란색: 강우
    - ⚫ 회색: 눈
    """)
