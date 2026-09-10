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

# 메인 타이틀 및 소개
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("""
이 앱은 **KOBIS 일별 박스오피스 데이터(1년치)**를 활용하여 영화 시장의 시간에 따른 흐름과 경향성을 시각화한 도감입니다.  
""")

st.divider()

# ==========================================
# [섹션 1] 개별 영화 날짜별 일관객 변화
# ==========================================
st.header("📌 Section 1. 개별 영화 날짜별 일관객 변화")

movie_list = df.groupby('영화명')['일관객'].sum().sort_values(ascending=False).index.tolist()

selected_movie = st.selectbox(
    "📊 분석할 영화를 선택하세요:",
    options=movie_list,
    index=0
)

movie_df = df[df['영화명'] == selected_movie].sort_values(by='날짜')

fig1 = px.line(
    movie_df,
    x='날짜',
    y='일관객',
    title=f"<b>[{selected_movie}]</b> 날짜별 일관객 추이",
    labels={'날짜': '날짜', '일관객': '일일 관객 수(명)'},
    markers=True
)

fig1.update_traces(
    hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>관객수:</b> %{y:,.0f}명<extra></extra>",
    line_color="#E50914",
    line_width=2.5
)

fig1.update_layout(
    xaxis_title="날짜",
    yaxis_title="일일 관객 수",
    hovermode="x unified",
    template="plotly_white",
    height=450
)

st.plotly_chart(fig1, use_container_width=True)

st.info(f"💡 **이 그래프로 알 수 있는 것:** 개별 영화('{selected_movie}')의 개봉 이후 관객수 증감 흐름과 주말/평일 주기에 따른 일일 관객 수의 변동 패턴 및 흥행 유효 기간을 파악할 수 있습니다.")

st.divider()

# ==========================================
# [섹션 2] 기간 내 일관객 합계 TOP 5 영화 추이 비교
# ==========================================
st.header("📌 Section 2. 일관객 합계 TOP 5 영화의 날짜별 추이 비교")

top5_movies = df.groupby('영화명')['일관객'].sum().nlargest(5).index.tolist()
top5_df = df[df['영화명'].isin(top5_movies)].sort_values(by=['날짜', '영화명'])

fig2 = px.line(
    top5_df,
    x='날짜',
    y='일관객',
    color='영화명',
    title="<b>기간 내 일관객 합계 TOP 5 영화 날짜별 관객수 비교</b>",
    labels={'날짜': '날짜', '일관객': '일일 관객 수(명)', '영화명': '영화 제목'},
    markers=True
)

fig2.update_traces(
    hovertemplate="<b>%{fullData.name}</b><br>날짜: %{x|%Y-%m-%d}<br>관객수: %{y:,.0f}명<extra></extra>"
)

fig2.update_layout(
    xaxis_title="날짜",
    yaxis_title="일일 관객 수",
    hovermode="x unified",
    template="plotly_white",
    height=500,
    legend=dict(
        title="🎬 영화 목록 (클릭하여 온/오프)",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig2, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 전체 기간 동안 가장 높은 총 관객 수를 기록한 TOP 5 흥행작들의 흥행 시기 중첩 여부, 개봉 당시의 최고 관객 수 스파이크, 상영 기간 비교 및 주말 흥행 대결 구도를 직관적으로 비교할 수 있습니다.")

st.divider()

# ==========================================
# [섹션 3] 날짜별 박스오피스 TOP 10 총 관객수 변화 (영역 그래프)
# ==========================================
st.header("📌 Section 3. 날짜별 박스오피스 TOP 10 총 관객수 변화")

daily_total = df.groupby('날짜')['일관객'].sum().reset_index()
top3_days = daily_total.nlargest(3, '일관객').sort_values(by='일관객', ascending=False)

fig3 = px.area(
    daily_total,
    x='날짜',
    y='일관객',
    title="<b>일별 박스오피스 TOP 10 관객수 총합 추이 및 Peak Day TOP 3</b>",
    labels={'날짜': '날짜', '일관객': 'TOP 10 총 관객 수(명)'}
)

fig3.update_traces(
    line_color="#2b5c8f",
    fillcolor="rgba(43, 92, 143, 0.3)",
    hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>TOP 10 총 관객수:</b> %{y:,.0f}명<extra></extra>"
)

colors = ['#d90429', '#f77f00', '#2a9d8f']
for idx, (_, row) in enumerate(top3_days.iterrows()):
    date_str = row['날짜'].strftime('%Y-%m-%d')
    audience = row['일관객']
    rank_label = f"<b>{idx+1}위 Peak: {date_str}</b><br>({audience:,.0f}명)"
    
    fig3.add_annotation(
        x=row['날짜'],
        y=audience,
        text=rank_label,
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor=colors[idx],
        ax=0,
        ay=-45 - (idx * 15),
        font=dict(size=12, color=colors[idx]),
        bgcolor="rgba(255, 255, 255, 0.85)",
        bordercolor=colors[idx],
        borderwidth=1.5,
        borderpad=4
    )

fig3.update_layout(
    xaxis_title="날짜",
    yaxis_title="TOP 10 총 관객 수",
    hovermode="x unified",
    template="plotly_white",
    height=500
)

st.plotly_chart(fig3, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 연중 전체 극장가(TOP 10 박스오피스)의 총 관객 규모 변화 흐름과 명절·성수기 연휴 및 대작 개봉일에 따른 시장 전체의 극장가 총 관객 피크 데이(Peak Day TOP 3)를 확인할 수 있습니다.")

st.divider()

# ==========================================
# [섹션 4] 기간 내 일관객 합계 TOP 10 영화 순위 (가로 막대 그래프)
# ==========================================
st.header("📌 Section 4. 기간 내 일관객 합계 TOP 10 영화 순위")

# 영화별 일관객 합계 및 10위권 차트인 날수(일수) 계산
top10_summary = df.groupby('영화명').agg(
    총관객수=('일관객', 'sum'),
    차트인일수=('날짜', 'nunique')
).reset_index()

# 관객 수 기준 상위 10개 영화 추출 및 Y축 위에서부터 오름차순 정렬
top10_summary = top10_summary.nlargest(10, '총관객수').sort_values(by='총관객수', ascending=True)

# 가로 막대 그래프 생성
fig4 = px.bar(
    top10_summary,
    x='총관객수',
    y='영화명',
    orientation='h',
    title="<b>기간 내 일관객 합계 TOP 10 영화 (10위권 유지 일수 포함)</b>",
    labels={'총관객수': '총 관객 수(명)', '영화명': '영화 제목'},
    color='총관객수',
    color_continuous_scale='Reds',
    text='총관객수'
)

fig4.update_traces(
    texttemplate='%{text:,.0f}명',
    textposition='outside',
    hovertemplate="<b>영화명: %{y}</b><br>총 관객수: %{x:,.0f}명<br>10위권 진입 일수: %{customdata}일<extra></extra>",
    customdata=top10_summary['차트인일수']
)

fig4.update_layout(
    xaxis_title="총 관객 수(명)",
    yaxis_title="영화 제목",
    template="plotly_white",
    height=500,
    coloraxis_showscale=False,
    xaxis=dict(range=[0, top10_summary['총관객수'].max() * 1.18])
)

st.plotly_chart(fig4, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 해당 기간 동안 가장 뛰어난 흥행 성적을 올린 TOP 10 영화들의 최종 총 관객수 순위와 함께, 각 영화가 일별 박스오피스 TOP 10 차트 내에 얼마나 오랜 기간(차트인 일수) 머물렀는지의 흥행 지속력을 비교할 수 있습니다.")

st.divider()

# ==========================================
# [섹션 5] (향후 그래프 추가용 예시 구역)
# ==========================================
st.header("📌 Section 5. 그래프 추가 예정 구역")
st.caption("🔒 *새로운 시각화 그래프가 이 구역에 지속적으로 추가될 예정입니다.*")

st.divider()

# 데이터 미리보기
with st.expander("📄 원본 데이터 미리보기"):
    st.dataframe(df.head(100), use_container_width=True)
