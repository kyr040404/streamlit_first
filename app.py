
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt

st.title('복합 차트 구현 📊')

# 샘플 데이터 생성
@st.cache_data
def generate_data():
    np.random.seed(42)
    date_range = pd.date_range(start='2023-01-01', periods=100, freq='D')
    
    df = pd.DataFrame({
        'date': date_range,
        'sales': np.random.randint(100, 500, size=100) + np.sin(np.linspace(0, 10, 100)) * 50,
        'customers': np.random.randint(50, 200, size=100),
        'avg_purchase': np.random.uniform(10, 50, size=100),
        'category': np.random.choice(['A', 'B', 'C', 'D'], size=100),
        'region': np.random.choice(['East', 'West', 'North', 'South'], size=100)
    })
    
    # 파생 데이터 추가
    df['revenue'] = df['sales'] * df['avg_purchase']
    df['year_month'] = df['date'].dt.strftime('%Y-%m')
    
    return df

data = generate_data()

st.dataframe(data, use_container_width=True)

st.header('1. Plotly를 사용한 복합 차트')

# Plotly 서브플롯 예제
st.subheader('매출과 고객 수의 관계')

# 서브플롯 생성
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('일별 매출', '일별 고객 수', '매출 vs 고객 수', '지역별 매출'),
    specs=[
        [{"type": "scatter"}, {"type": "scatter"}],
        [{"type": "scatter"}, {"type": "pie"}]
    ],
    vertical_spacing=0.1,
    horizontal_spacing=0.1
)

# 첫 번째 그래프: 일별 매출
fig.add_trace(
    go.Scatter(
        x=data['date'], 
        y=data['sales'],
        mode='lines+markers',
        name='일별 매출',
        line=dict(color='royalblue')
    ),
    row=1, col=1
)

# 두 번째 그래프: 일별 고객 수
fig.add_trace(
    go.Scatter(
        x=data['date'], 
        y=data['customers'],
        mode='lines+markers',
        name='일별 고객 수',
        line=dict(color='firebrick')
    ),
    row=1, col=2
)

# 세 번째 그래프: 매출 vs 고객 수 산점도
fig.add_trace(
    go.Scatter(
        x=data['customers'], 
        y=data['sales'],
        mode='markers',
        marker=dict(
            size=8,
            color=data['avg_purchase'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='평균 구매액',
                            x=0.47,      # 서브플롯의 오른쪽 내부에 배치 (전체 피규어 x 좌표 기준; 필요시 도메인 중앙 계산)
                            y=0.25,       # 서브플롯 중앙에 위치 (전체 피규어 y 좌표 기준; 필요시 도메인 중앙 계산)
                            len=0.4,     # 서브플롯 높이에 맞는 길이 (예시 값)
                            thickness=10 # 색상 막대 두께
                        )
        ),
        name='매출 vs 고객 수'
    ),
    row=2, col=1
)

# 네 번째 그래프: 지역별 매출 파이 차트
region_sales = data.groupby('region')['sales'].sum().reset_index()
fig.add_trace(
    go.Pie(
        labels=region_sales['region'],
        values=region_sales['sales'],
        hole=0.4,
        name='지역별 매출'
    ),
    row=2, col=2
)

# 레이아웃 업데이트
fig.update_layout(
    height=700,
    width=800,
    title_text='판매 데이터 대시보드',
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

st.header('2. Altair를 사용한 인터랙티브 차트')

# 기본 차트
st.subheader('카테고리별 매출 분석')

# 카테고리별 평균 계산
category_avg = data.groupby('category')[['sales', 'customers', 'avg_purchase']].mean().reset_index()

# 기본 막대 차트
base = alt.Chart(category_avg).encode(
    x='category:N' # Nominal: 범주형 데이터
)

# 막대 차트
bar = base.mark_bar().encode(
    y='sales:Q', # Quantitative: 수치형 데이터
    color=alt.Color('category:N', scale=alt.Scale(scheme='category10')),
    tooltip=['category', 'sales', 'customers', 'avg_purchase']
).properties(
    width=300,
    height=300,
    title='카테고리별 평균 매출'
)

# 점 차트
point = base.mark_point(filled=True, size=100).encode(
    y='customers:Q',
    tooltip=['category', 'customers']
).properties(
    width=300,
    height=300,
    title='카테고리별 평균 고객 수'
)

# 두 차트 결합
combined_chart = alt.hconcat(bar, point)
st.altair_chart(combined_chart, use_container_width=True)

# 인터랙티브 히트맵
st.subheader('날짜별 판매 히트맵')

# 연-월-카테고리별 집계
heatmap_data = data.groupby(['year_month', 'category'])['sales'].sum().reset_index()

# 히트맵 차트
heatmap = alt.Chart(heatmap_data).mark_rect().encode(
    x='year_month:O', # Ordinal: 순서형 데이터 # 시계열의 경우 :T로 설정
    y='category:O',
    color=alt.Color('sales:Q', scale=alt.Scale(scheme='viridis')),
    tooltip=['year_month', 'category', 'sales']
).properties(
    width=600,
    height=300,
    title='월별-카테고리별 판매 히트맵'
)

st.altair_chart(heatmap, use_container_width=True)