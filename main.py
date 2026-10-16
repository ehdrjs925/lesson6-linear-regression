        name="관측 연평균기온",
        marker=dict(size=7, color="#2E86C1"),
        hovertemplate="%{x}년<br>연평균기온: %{y:.2f} ℃<extra></extra>",
    )
)
fig.add_trace(
    go.Scatter(
        x=line_years,
        y=line_temps,
        mode="lines",
        name="선형 회귀 직선 (1900~2100)",
        line=dict(color="#E67E22", width=3),
        hovertemplate="%{x}년<br>회귀 예측: %{y:.2f} ℃<extra></extra>",
    )
)
fig.update_layout(
    xaxis_title="연도",
    yaxis_title="연평균기온 (℃)",
    hovermode="closest",
    legend=dict(orientation="h", y=1.1),
)
st.plotly_chart(fig, use_container_width=True)

st.metric("연도와 연평균기온의 피어슨 상관계수 (r)", f"{correlation:.3f}")
st.caption(f"회귀식: 예상 연평균기온 = {slope:.5f} × 연도 + ({intercept:.3f})")

st.subheader("원하는 연도의 기온 예측")
selected_year = st.slider("예측할 연도를 선택하세요", 1900, 2100, 2030, 1)
predicted_temperature = slope * selected_year + intercept
st.metric(f"{selected_year}년 서울 예상 연평균기온", f"{predicted_temperature:.2f} ℃")

if selected_year < start_year or selected_year > end_year:
    st.info("선택한 연도는 학습 데이터 범위 밖이므로, 회귀 직선을 연장한 외삽 예측입니다.")

st.caption(
    "자료 기준: 2025년까지, 유효한 일평균기온 관측일 300일 이상인 연도만 사용. "
    "이 예측값은 과거 자료에 맞춘 단순 선형 추세이며 실제 미래 기온을 보장하지 않습니다."
)

with st.expander("분석에 사용한 연도별 데이터 보기"):
    st.dataframe(
        annual.rename(columns={"연도": "연도", "연평균기온": "연평균기온 (℃)", "관측일수": "관측일수"}),
        use_container_width=True,
        hide_index=True,
    )
