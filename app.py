import streamlit as st
import pandas as pd
import numpy as np
import time

st.header('캐싱 예시 입니다.')

# 캐싱 없는 데이터 로딩 함수
def load_data_no_cache():
    # 시간이 오래 걸리는 작업 시뮬레이션
    time.sleep(2)
    
    # 샘플 데이터 생성
    data = pd.DataFrame({
        'A': np.random.randn(100),
        'B': np.random.randn(100),
        'C': np.random.randn(100)
    })
    
    return data

# 캐싱을 사용하는 데이터 로딩 함수
@st.cache_data
def load_data_with_cache():
    # 시간이 오래 걸리는 작업 시뮬레이션
    time.sleep(2)
    
    # 샘플 데이터 생성
    data = pd.DataFrame({
        'A': np.random.randn(100),
        'B': np.random.randn(100),
        'C': np.random.randn(100)
    })
    
    return data

# 데모 탭
cache_tab1, cache_tab2 = st.tabs(["캐싱 없음", "캐싱 있음"])

with cache_tab1:
    st.subheader("캐싱 없음")
    if st.button("데이터 로드 (캐싱 없음)"):
        with st.spinner("데이터 로딩 중..."):
            data = load_data_no_cache()
            st.success("데이터 로딩 완료!")
            st.dataframe(data.head())

with cache_tab2:
    st.subheader("캐싱 있음")
    if st.button("데이터 로드 (캐싱 있음)"):
        with st.spinner("데이터 로딩 중..."):
            data = load_data_with_cache()
            st.success("데이터 로딩 완료!")
            st.dataframe(data.head())
            st.info("두 번째 실행부터는 즉시 결과가 표시됩니다.")