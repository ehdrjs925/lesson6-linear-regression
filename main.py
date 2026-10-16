import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "bb860932644270ad1199f10d3e7670e30231bce4/data/seoul.csv"
)

st.set_page_config(page_title="기온 예측기", page_icon="🌡️", layout="wide")
st.title("서울 기온 예측기")
st.write("서울의 연평균기온 데이터를 직선 회귀분석하여 선택한 연도의 기온을 예상합니다.")


@st.cache_data(ttl=3600)
def load_annual_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")
    df = df.dropna(subset=["날짜", "평균기온"]).copy()
    df["연도"] = df["날짜"].dt.year
    df = df[df["연도"] <= 2025]

    annual = (
        df.groupby("연도", as_index=False)
        .agg(연평균기온=("평균기온", "mean"), 관측일수=("날짜", "nunique"))
    )
    return annual[annual["관측일수"] >= 300].sort_values("연도")


try:
    annual = load_annual_data()
except Exception as exc:
    st.error(f"기온 데이터를 불러올 수 없습니다: {exc}")
    st.stop()

if len(annual) < 2:
    st.error("회귀분석에 필요한 연도가 2개 이상 존재하지 않습니다.")
    st.stop()

x = annual["연도"].to_numpy(dtype=float)
y = annual["연평균기온"].to_numpy(dtype=float)
slope, intercept = np.polyfit(x, y, 1)
correlation = annual["연도"].corr(annual["연평균기온"])

start_year = int(annual["연도"].min())
end_year = int(annual["연도"].max())

# 최근 20년: 자료의 마지막 기준 연도를 포함한 20개 달력 연도
recent_start = end_year - 19
recent = annual[annual["연도"].between(recent_start, end_year)]
if len(recent) >= 2:
    recent_slope, recent_intercept = np.polyfit(
        recent["연도"].to_numpy(dtype=float),
        recent["연평균기온"].to_numpy(dtype=float),
        1,
    )
else:
    recent_slope = None

col1, col2, col3 = st.columns(3)
col1.metric("회귀분석에 사용한 연도", f"{len(annual)}개")
col2.metric("시작 연도", f"{start_year}년")
col3.metric("끝 연도", f"{end_year}년")

st.subheader("100년당 기온 변화 추세 비교")
whole_col, recent_col = st.columns(2)
whole_col.metric(
    f"전체 기간 ({start_year}~{end_year}년)",
    f"{slope * 100:+.2f} ℃/100년",
)
whole_col.caption(f"유효한 관측 연도 {len(annual)}개로 회귀분석")
if recent_slope is not None:
    recent_col.metric(
        f"최근 20년 ({recent_start}~{end_year}년)",
        f"{recent_slope * 100:+.2f} ℃/100년",
    )
    recent_col.caption(f"해당 기간 중 유효한 관측 연도 {len(recent)}개로 회귀분석")
else:
    recent_col.warning("최근 20년 구간에 회귀분석 가능한 연도가 2개 미만입니다.")
st.caption(
    "회귀 직선의 연간 기울기(℃/년)에 100을 곱했습니다. "
    "최근 20년 값은 비교를 위한 추세로, 향후 100년간의 실제 상승량을 뜻하지 않습니다."
)

st.subheader("연도별 평균기온과 회귀 직선")
line_years = np.arange(1900, 2101)
line_temps = slope * line_years + intercept

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=x,
        y=y,
        mode="markers",
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
