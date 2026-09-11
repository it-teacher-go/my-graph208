import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

# 앱 제목
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 데이터를 바탕으로 시간의 흐름에 따른 영화 관객 수 변화 및 추세를 시각화합니다.")

# ----------------------------------------------------
# 1. 데이터 불러오기 및 전처리
# ----------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    
    # 8자리 숫자 날짜(YYYYMMDD)를 실제 datetime 객체로 변환
    if '날짜' in df.columns:
        df['날짜'] = pd.to_datetime(df['날짜'].astype(str), format='%Y%m%d')
    
    # 수치형 데이터 변환
    for col in ['일관객', '누적관객', '스크린수', '상영횟수', '순위']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

try:
    df = load_data(DATA_URL)
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 사이드바 - 요약 정보
st.sidebar.header("📌 데이터 요약")
st.sidebar.markdown(f"**총 데이터 건수:** {len(df):,} 건")
st.sidebar.markdown(f"**조회 기간:** {df['날짜'].min().strftime('%Y-%m-%d')} ~ {df['날짜'].max().strftime('%Y-%m-%d')}")

# ----------------------------------------------------
# [구역 1] 영화별 일자별 일관객 변화 (단일 선택 선 그래프)
# ----------------------------------------------------
st.markdown("---")
st.header("1️⃣ 영화별 일자별 일관객 변화 추이")
st.write("관심 있는 영화를 선택하면 상영 기간 동안의 일자별 관객 수 변화를 확인할 수 있습니다.")

top_movies = df.groupby('영화명')['누적관객'].max().sort_values(ascending=False).index.tolist()
selected_movie = st.selectbox("🎬 영화를 선택하세요", top_movies, index=0)

movie_df = df[df['영화명'] == selected_movie].sort_values('날짜')

if not movie_df.empty:
    fig1 = px.line(
        movie_df,
        x='날짜',
        y='일관객',
        title=f"<b>[{selected_movie}]</b> 일별 관객 수 추이",
        labels={'날짜': '날짜', '일관객': '일일 관객 수(명)'},
        markers=True,
        custom_data=['순위', '스크린수']
    )
    
    fig1.update_traces(
        line_color='#E50914',
        hovertemplate="<b>날짜:</b> %{x|%Y년 %m월 %d일}<br>" +
                      "<b>일관객:</b> %{y:,}명<br>" +
                      "<b>박스오피스 순위:</b> %{customdata[0]}위<br>" +
                      "<b>스크린 수:</b> %{customdata[1]:,}개<extra></extra>"
    )
    
    fig1.update_layout(
        xaxis_title="날짜",
        yaxis_title="일 관객 수 (명)",
        hovermode="x unified",
        template="plotly_white",
        height=500
    )

    st.plotly_chart(fig1, use_container_width=True)

    max_row = movie_df.loc[movie_df['일관객'].idxmax()]
    max_date_str = max_row['날짜'].strftime('%Y년 %m월 %d일')
    max_audience = int(max_row['일관객'])
    
    st.info(f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'의 일일 최고 관객 수는 **{max_date_str}**에 기록한 **{max_audience:,}명**이며, 상영 기간 동안의 주말 관객 집중도와 관객 감소 폭을 한눈에 파악할 수 있습니다.")

# ----------------------------------------------------
# [구역 2] 총 관객수 TOP 5 영화의 날짜별 일관객 비교 (다중 선 그래프)
# ----------------------------------------------------
st.markdown("---")
st.header("2️⃣ 기간 내 관객수 TOP 5 영화의 일관객 추이 비교")
st.write("해당 기간 동안 일관객 합계가 가장 높았던 상위 5개 영화의 날짜별 일관객 변화를 비교해봅니다.")

top5_movies = df.groupby('영화명')['일관객'].sum().nlargest(5).index.tolist()
top5_df = df[df['영화명'].isin(top5_movies)].sort_values('날짜')

if not top5_df.empty:
    fig2 = px.line(
        top5_df,
        x='날짜',
        y='일관객',
        color='영화명',
        title="<b>기간 내 관객수 TOP 5 영화 일관객 비교</b>",
        labels={'날짜': '날짜', '일관객': '일일 관객 수(명)', '영화명': '영화 제목'},
        markers=True,
        custom_data=['순위', '스크린수']
    )
    
    fig2.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>" +
                      "<b>날짜:</b> %{x|%Y년 %m월 %d일}<br>" +
                      "<b>일관객:</b> %{y:,}명<br>" +
                      "<b>순위:</b> %{customdata[0]}위<br>" +
                      "<b>스크린 수:</b> %{customdata[1]:,}개<extra></extra>"
    )
    
    fig2.update_layout(
        xaxis_title="날짜",
        yaxis_title="일 관객 수 (명)",
        hovermode="x unified",
        template="plotly_white",
        height=550,
        legend=dict(
            title="영화 목록 (클릭하여 범례 토글)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig2, use_container_width=True)

    top5_names_str = ", ".join([f"**{m}**" for m in top5_movies])
    st.info(f"💡 **이 그래프로 알 수 있는 것:** 해당 기간 관객수 상위 5개 영화({top5_names_str})의 개봉 시기와 흥행 피크 기간이 어떻게 겹치고 차이나는지, 그리고 최고 흥행작 간의 일일 최고 관객 수 격차를 한눈에 비교할 수 있습니다.")

# ----------------------------------------------------
# [구역 3] 날짜별 박스오피스 10위권 총 관객수 영역 그래프 (Area Chart)
# ----------------------------------------------------
st.markdown("---")
st.header("3️⃣ 일별 박스오피스 TOP 10 총 관객수 추이")
st.write("매일 박스오피스 1~10위 영화의 관객 수 합계를 영역 그래프로 확인합니다. 극장가 전체의 성수기와 비수기 흐름을 한눈에 볼 수 있습니다.")

daily_total = df.groupby('날짜')['일관객'].sum().reset_index().sort_values('날짜')

if not daily_total.empty:
    top3_days = daily_total.nlargest(3, '일관객')

    fig3 = px.area(
        daily_total,
        x='날짜',
        y='일관객',
        title="<b>일별 박스오피스 TOP 10 전체 관객수 합계</b>",
        labels={'날짜': '날짜', '일관객': 'TOP 10 관객수 합계(명)'}
    )

    fig3.update_traces(
        line_color='#2E86C1',
        fillcolor='rgba(46, 134, 193, 0.3)',
        hovertemplate="<b>날짜:</b> %{x|%Y년 %m월 %d일}<br><b>TOP 10 총 관객수:</b> %{y:,}명<extra></extra>"
    )

    for idx, row in enumerate(top3_days.itertuples(), 1):
        date_str = row.날짜.strftime('%Y-%m-%d')
        audience_val = int(row.일관객)
        
        fig3.add_annotation(
            x=row.날짜,
            y=audience_val,
            text=f"<b>Top {idx}</b><br>{date_str}<br>({audience_val:,}명)",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor='#E50914',
            ax=0,
            ay=-40,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#E50914',
            borderwidth=1,
            borderpad=4
        )

    fig3.update_layout(
        xaxis_title="날짜",
        yaxis_title="TOP 10 관객수 합계 (명)",
        hovermode="x unified",
        template="plotly_white",
        height=550
    )

    st.plotly_chart(fig3, use_container_width=True)

    top3_text_list = [
        f"**{r.날짜.strftime('%Y년 %m월 %d일')}** ({int(r.일관객):,}명)" 
        for r in top3_days.itertuples()
    ]
    top3_str = ", ".join(top3_text_list)

    st.info(f"💡 **이 그래프로 알 수 있는 것:** 해당 1년 중 극장 전체 관객수가 가장 많았던 날 Top 3는 {top3_str}이며, 명절/연휴나 대형 신작 개봉 시기에 맞춰 전체 관객 수가 크게 치솟는 성수기 패턴을 한눈에 알 수 있습니다.")

# ----------------------------------------------------
# [구역 4] 기간 내 총 관객수 TOP 10 영화 (가로 막대그래프)
# ----------------------------------------------------
st.markdown("---")
st.header("4️⃣ 기간 내 총 관객수 TOP 10 영화")
st.write("해당 기간 일관객 합계가 가장 많은 영화 상위 10편을 순위별로 확인합니다. 관객 수가 가장 많은 영화가 맨 위에 위치합니다.")

movie_summary = df.groupby('영화명').agg(
    총관객수=('일관객', 'sum'),
    차트인일수=('날짜', 'nunique')
).reset_index()

top10_summary = movie_summary.nlargest(10, '총관객수').sort_values('총관객수', ascending=True)

if not top10_summary.empty:
    fig4 = px.bar(
        top10_summary,
        x='총관객수',
        y='영화명',
        orientation='h',
        title="<b>기간 내 총 관객수 TOP 10 영화</b>",
        labels={'총관객수': '총 관객 수(명)', '영화명': '영화 제목'},
        text='총관객수',
        custom_data=['차트인일수']
    )

    fig4.update_traces(
        marker_color='#27AE60',
        texttemplate='%{x:,}명',
        textposition='outside',
        hovertemplate="<b>영화명:</b> %{y}<br>" +
                      "<b>총 관객수:</b> %{x:,}명<br>" +
                      "<b>10위권 차트인 날수:</b> %{customdata[0]}일<extra></extra>"
    )

    fig4.update_layout(
        xaxis_title="총 관객 수 (명)",
        yaxis_title="영화 제목",
        template="plotly_white",
        height=500,
        xaxis=dict(range=[0, top10_summary['총관객수'].max() * 1.18])
    )

    st.plotly_chart(fig4, use_container_width=True)

    top1_movie = top10_summary.iloc[-1]
    
    st.info(f"💡 **이 그래프로 알 수 있는 것:** 해당 기간 관객수 1위 영화는 **{top1_movie['영화명']}** ({int(top1_movie['총관객수']):,}명, 10위권 차트인 **{top1_movie['차트인일수']}일**)이며, 흥행 규모와 함께 영화가 박스오피스 10위권 내에서 얼마나 오랫동안 롱런(Long-run)했는지 관객수 대비 차트인 날수를 함께 파악할 수 있습니다.")

# ----------------------------------------------------
# [구역 5] 월 × 요일별 일관객 합계 히트맵 (Heatmap)
# ----------------------------------------------------
st.markdown("---")
st.header("5️⃣ 월 × 요일별 일관객 합계 분포 (히트맵)")
st.write("월과 요일 조합별 총 관객 수를 히트맵으로 시각화합니다. 관객 수가 많을수록 색상이 진하게 표시됩니다.")

# 날짜 데이터에서 월, 요일 추출
heatmap_df = df.copy()
heatmap_df['월'] = heatmap_df['날짜'].dt.month.astype(str) + '월'
heatmap_df['요일'] = heatmap_df['날짜'].dt.day_name()

# 요일 한글 매핑 및 순서 지정 (월요일 ~ 일요일)
days_ko = {
    'Monday': '월요일', 'Tuesday': '화요일', 'Wednesday': '수요일',
    'Thursday': '목요일', 'Friday': '금요일', 'Saturday': '토요일', 'Sunday': '일요일'
}
heatmap_df['요일'] = heatmap_df['요일'].map(days_ko)

# 월(1월~12월) 및 요일(월~일) 정렬 기준 정의
month_order = [f"{m}월" for m in range(1, 13)]
day_order = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

# 월 x 요일 그룹화 및 피벗 테이블 생성
grouped_hm = heatmap_df.groupby(['월', '요일'])['일관객'].sum().reset_index()
pivot_hm = grouped_hm.pivot(index='월', columns='요일', values='일관객').reindex(index=month_order, columns=day_order).fillna(0)

if not pivot_hm.empty:
    # Plotly imshow 기반 히트맵 생성
    fig5 = px.imshow(
        pivot_hm,
        labels=dict(x="요일", y="월", color="총 관객 수(명)"),
        x=day_order,
        y=pivot_hm.index.tolist(),
        color_continuous_scale="Reds",  # 색상이 진할수록 관객 수가 많음
        title="<b>월 × 요일별 관객수 합계 히트맵</b>",
        text_auto=",.0f"  # 셀 내부에 숫자 자동 표시 (3자리 콤마)
    )

    fig5.update_traces(
        hovertemplate="<b>%{y} %{x}</b><br>총 관객수: %{z:,}명<extra></extra>"
    )

    fig5.update_layout(
        xaxis_title="요일",
        yaxis_title="월",
        template="plotly_white",
        height=600
    )

    st.plotly_chart(fig5, use_container_width=True)

    # 히트맵 상 최다 관객 월/요일 조합 추출
    max_val = pivot_hm.values.max()
    max_month, max_day = "", ""
    for r in pivot_hm.index:
        for c in pivot_hm.columns:
            if pivot_hm.loc[r, c] == max_val:
                max_month, max_day = r, c
                break

    st.info(f"💡 **이 그래프로 알 수 있는 것:** 해당 기간 중 가장 관객이 몰린 시점은 **{max_month} {max_day}**({int(max_val):,}명)이며, 주말(토/일요일) 집중 현상과 함께 연휴 및 방학 시즌(여름/겨울)에 해당 월의 관객수가 진하게 집중되는 패턴을 한눈에 확인할 수 있습니다.")

# ----------------------------------------------------
# [구역 6] 그래프 추가 구역 (확장용)
# ----------------------------------------------------
st.markdown("---")
st.header("6️⃣ [추가 예정] 시간 흐름에 따른 신규 그래프")
st.caption("👉 향후 추가될 그래프 구역입니다.")
