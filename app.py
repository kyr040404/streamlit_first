import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.title('인터랙티브 대시보드 구현 🎮')

# 샘플 데이터 생성
@st.cache_data
def generate_sales_data():
    np.random.seed(42)
    date_range = pd.date_range(start='2023-01-01', periods=365, freq='D')
    
    # 기본 데이터 생성
    df = pd.DataFrame({
        'date': date_range,
        'weekday': date_range.day_name(),
        'month': date_range.month_name(),
        'quarter': date_range.quarter,
    })
    
    # 요일 효과 추가
    weekday_effect = {
        'Monday': 0.7,
        'Tuesday': 0.8,
        'Wednesday': 0.9,
        'Thursday': 1.0,
        'Friday': 1.3,
        'Saturday': 1.5,
        'Sunday': 1.2
    }
    df['weekday_effect'] = df['weekday'].map(weekday_effect)
    
    # 월별 효과 추가 (계절성)
    month_effect = {
        'January': 1.0,
        'February': 0.8,
        'March': 0.9,
        'April': 1.0,
        'May': 1.1,
        'June': 1.2,
        'July': 1.3,
        'August': 1.2,
        'September': 1.1,
        'October': 1.0,
        'November': 1.1,
        'December': 1.4
    }
    df['month_effect'] = df['month'].map(month_effect)
    
    # 프로모션 효과 추가 (무작위 10일)
    promo_dates = np.random.choice(date_range, size=10, replace=False)
    df['promotion'] = df['date'].isin(promo_dates)
    df['promo_effect'] = 1.0
    df.loc[df['promotion'], 'promo_effect'] = 1.5
    
    # 트렌드 효과 추가 (완만한 상승)
    days = np.arange(len(df))
    trend = 1 + days * 0.0005  # 약간 상승하는 트렌드
    df['trend'] = trend
    
    # 카테고리 및 지역 추가
    categories = ['전자제품', '의류', '식품', '가구', '스포츠용품']
    regions = ['서울', '부산', '인천', '대구', '대전', '광주', '수원']
    
    # 각 카테고리와 지역에 대한 매출 시뮬레이션
    all_data = []
    
    for category in categories:
        for region in regions:
            category_factor = np.random.uniform(0.7, 1.3)  # 카테고리별 변동성
            region_factor = np.random.uniform(0.8, 1.2)    # 지역별 변동성
            
            # 카테고리-지역별 데이터 복사
            temp_df = df.copy()
            temp_df['category'] = category
            temp_df['region'] = region
            
            # 기본 매출 (100~500 사이) 및 영향 요소 적용
            base_sales = np.random.randint(100, 500)
            noise = np.random.normal(1, 0.05, size=len(temp_df))  # 약간의 무작위성
            
            temp_df['sales'] = base_sales * \
                            temp_df['weekday_effect'] * \
                            temp_df['month_effect'] * \
                            temp_df['promo_effect'] * \
                            temp_df['trend'] * \
                            category_factor * \
                            region_factor * \
                            noise
            
            # 반올림하여 정수로 변환
            temp_df['sales'] = temp_df['sales'].round().astype(int)
            
            # 필요한 열만 선택
            temp_df = temp_df[['date', 'category', 'region', 'sales', 'promotion', 'weekday', 'month', 'quarter']]
            all_data.append(temp_df)
    
    # 모든 데이터 합치기
    final_df = pd.concat(all_data, ignore_index=True)
    return final_df

# 데이터 로드
sales_data = generate_sales_data()

st.dataframe(sales_data, use_container_width=True)

# 대시보드 레이아웃
st.sidebar.header('대시보드 필터')

# 날짜 범위 선택
min_date = sales_data['date'].min().date()
max_date = sales_data['date'].max().date()

date_range = st.sidebar.date_input(
    "날짜 범위 선택",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_data = sales_data[(sales_data['date'].dt.date >= start_date) & 
                              (sales_data['date'].dt.date <= end_date)]
else:
    filtered_data = sales_data.copy()

# 카테고리 및 지역 선택
selected_categories = st.sidebar.multiselect(
    "카테고리 선택",
    options=sales_data['category'].unique(),
    default=sales_data['category'].unique()
)

selected_regions = st.sidebar.multiselect(
    "지역 선택",
    options=sales_data['region'].unique(),
    default=sales_data['region'].unique()
)

# 필터 적용
if selected_categories and selected_regions:
    filtered_data = filtered_data[
        (filtered_data['category'].isin(selected_categories)) & 
        (filtered_data['region'].isin(selected_regions))
    ]
else:
    st.error("카테고리와 지역을 하나 이상 선택해주세요.")
    st.stop()

# 프로모션 필터
promotion_filter = st.sidebar.radio(
    "프로모션 필터",
    ["모두", "프로모션 있음", "프로모션 없음"]
)

if promotion_filter == "프로모션 있음":
    filtered_data = filtered_data[filtered_data['promotion'] == True]
elif promotion_filter == "프로모션 없음":
    filtered_data = filtered_data[filtered_data['promotion'] == False]

# 주요 지표
st.header('주요 판매 지표')

# 지표 계산
total_sales = filtered_data['sales'].sum()
avg_daily_sales = filtered_data.groupby('date')['sales'].sum().mean()
top_category = filtered_data.groupby('category')['sales'].sum().idxmax()
top_region = filtered_data.groupby('region')['sales'].sum().idxmax()

# 지표 표시
col1, col2, col3, col4 = st.columns(4)
col1.metric("총 매출", f"{total_sales:,}원")
col2.metric("일평균 매출", f"{avg_daily_sales:,.0f}원")
col3.metric("최고 매출 카테고리", top_category)
col4.metric("최고 매출 지역", top_region)

# 매출 트렌드 차트
st.header('매출 트렌드')

# 일별 매출 집계
daily_sales = filtered_data.groupby('date')['sales'].sum().reset_index()


fig = px.line(
    daily_sales, 
    x='date', 
    y='sales',
    title='일별 총 매출',
    labels={'date': '날짜', 'sales': '매출'},
    template='plotly_white'
)

# 프로모션 날짜 표시
promo_dates = filtered_data[filtered_data['promotion']]['date'].dt.normalize().unique()

for promo_date in promo_dates:
    fig.add_vline(
        x=promo_date.to_pydatetime(), 
        line_dash="dash", 
        line_color="red",
        # annotation_text="프로모션",
        # annotation_position="top right"
    )

st.plotly_chart(fig, use_container_width=True)

# 카테고리별 지역별 분석
st.header('세부 분석')

tab1, tab2 = st.tabs(["카테고리별 분석", "지역별 분석"])

with tab1:
    # 카테고리별 매출
    category_sales = filtered_data.groupby('category')['sales'].sum().reset_index()
    
    fig_category = px.pie(
        category_sales,
        values='sales',
        names='category',
        title='카테고리별 매출 비중',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    st.plotly_chart(fig_category, use_container_width=True)
    
    # 카테고리별 월간 트렌드
    filtered_data['month_year'] = filtered_data['date'].dt.strftime('%Y-%m')
    category_monthly = filtered_data.groupby(['month_year', 'category'])['sales'].sum().reset_index()
    
    fig_category_trend = px.line(
        category_monthly,
        x='month_year',
        y='sales',
        color='category',
        title='카테고리별 월간 매출 트렌드',
        labels={'month_year': '월', 'sales': '매출', 'category': '카테고리'},
        template='plotly_white'
    )
    
    st.plotly_chart(fig_category_trend, use_container_width=True)

with tab2:
    # 지역별 매출
    region_sales = filtered_data.groupby('region')['sales'].sum().reset_index()
    
    fig_region = px.bar(
        region_sales,
        x='region',
        y='sales',
        title='지역별 총 매출',
        labels={'region': '지역', 'sales': '매출'},
        color='sales',
        color_continuous_scale='Viridis',
        template='plotly_white'
    )
    
    st.plotly_chart(fig_region, use_container_width=True)
    
    # 지역 및 카테고리별 히트맵
    region_category = filtered_data.groupby(['region', 'category'])['sales'].sum().reset_index()
    region_category_pivot = region_category.pivot(index='region', columns='category', values='sales')
    
    fig_heatmap = px.imshow(
        region_category_pivot,
        labels=dict(x="카테고리", y="지역", color="매출"),
        x=region_category_pivot.columns,
        y=region_category_pivot.index,
        color_continuous_scale='Viridis',
        title='지역 및 카테고리별 매출 히트맵'
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

# 상세 데이터 테이블
st.header('상세 데이터')

show_data = st.checkbox('상세 데이터 보기')
if show_data:
    st.write(f'데이터 행 수: {len(filtered_data)}')
    st.dataframe(
        filtered_data[['date', 'category', 'region', 'sales', 'promotion']].sort_values('date'),
        use_container_width=True
    )

# 데이터 다운로드 버튼
st.download_button(
    label="데이터 CSV 다운로드",
    data=filtered_data[['date', 'category', 'region', 'sales', 'promotion']].to_csv(index=False).encode('utf-8'),
    file_name=f'sales_data_{start_date}_to_{end_date}.csv',
    mime='text/csv',
)