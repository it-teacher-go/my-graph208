import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

# 데이터 로드 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    df = pd.read_csv(url)
    
    # YYYYMMDD 형태의 날짜 컬럼을 진짜 datetime으로 변환
    df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    df = df.sort_values(by='날짜')
    
    # 수치형 컬럼 변환
    df['일관객'] = pd.to_numeric(df['일관객'], errors='coerce')
    df['누적관객'] = pd.to_numeric(df['누적관객'], errors='coerce')
    df['순위'] = pd.to_numeric(df['순위'], errors='coerce')
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 타이틀 및 소개
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("""
이 앱은 **KOBIS 일별 박스오피스 데이터(1년치)**를 활용하여 영화 시장의 시간에 따른 흐름을 시각화한 도감입니다.
""")

st.divider()

# ==========================================
# [섹션 1] 개별 영화 날짜별 일관객 변화
# ==========================================
st.header("📌 Section 1. 개별 영화 날짜별 일관객 변화")

# 드롭다운 영화 목록 (총 관객수 상위 순 정렬)
movie_list = df.groupby('영화명')['일관객'].sum().sort_values(ascending=False).index.tolist()

selected_movie = st.selectbox(
    "📊 분석할 영화를 선택하세요:",
    options=movie_list,
    index=0
)

# 데이터 필터링
movie_df = df[df['영화명'] == selected_movie].sort_values(by='날짜')

# 플롯리 선 그래프
fig = px.line(
    movie_df,
    x='날짜',
    y='일관객',
    title=f"<b>[{selected_movie}]</b> 날짜별 일관객 추이",
    labels={'날짜': '날짜', '일관객': '일일 관객 수(명)'},
    markers=True
)

# 툴팁(마우스 오버) 설정
fig.update_traces(
    hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>관객수:</b> %{y:,.0f}명<extra></extra>",
    line_color="#E50914",
    line_width=2.5
)

fig.update_layout(
    hovermode="x unified",
    template="plotly_white",
    height=450
)

st.plotly_chart(fig, use_container_width=True)

# 그래프 해설 문구 자릿값 (st.info 활용)
st.info(f"💡 **이 그래프로 알 수 있는 것:** 개별 영화('{selected_movie}')의 개봉 이후 관객수 증감 흐름과 주말/평일 주기에 따른 일일 관객 수의 변동 패턴 및 흥행 유효 기간을 파악할 수 있습니다.")

st.divider()

# ==========================================
# [섹션 2] (향후 그래프 추가용 예시 구역)
# ==========================================
st.header("📌 Section 2. 그래프 추가 예정 구역")
st.caption("🔒 *새로운 시각화 그래프가 이 구역에 지속적으로 추가될 예정입니다.*")
