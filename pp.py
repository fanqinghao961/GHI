import streamlit as st
import requests
from datetime import date

st.title("光伏发电量 & 弃光率计算")
st.caption("基于经纬度、日期、装机容量自动计算理论发电量与弃光率")

# 输入区
col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("纬度", value=38.962061, format="%.6f")
with col2:
    lon = st.number_input("经度", value=117.255167, format="%.6f")

col3, col4 = st.columns(2)
with col3:
    start_date = st.date_input("开始日期", value=date(2026,2,13))
with col4:
    end_date = st.date_input("结束日期", value=date(2026,2,13))

col5, col6 = st.columns(2)
with col5:
    capacity = st.number_input("装机容量 (kW)", value=120000.0)
with col6:
    pr = st.number_input("PR值", value=0.8, min_value=0.0, max_value=1.0)

# 计算理论发电量
if st.button("获取理论发电量"):
    with st.spinner("正在获取气象辐射数据..."):
        try:
            url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": "shortwave_radiation_instant",
                "timezone": "Asia/Shanghai",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            res = requests.get(url, params=params)
            data = res.json()
            ghi_list = data["hourly"]["shortwave_radiation_instant"]

            total_theo = 0.0
            for ghi in ghi_list:
                if ghi and ghi > 0:
                    total_theo += ghi / 1000 * capacity * pr

            st.session_state["total_theo"] = total_theo
            st.success(f"理论总发电量：**{total_theo:.2f} kWh**")

        except Exception as e:
            st.error(f"获取失败：{str(e)}")

# 弃光率计算
st.divider()
st.subheader("弃光率计算")
actual = st.number_input("实际发电量（kWh）", value=0.0)

if st.button("计算弃光率"):
    if "total_theo" not in st.session_state or st.session_state["total_theo"] <= 0:
        st.warning("请先计算理论发电量！")
    else:
        theo = st.session_state["total_theo"]
        curtail_rate = (theo - actual) / theo * 100

        st.metric("弃光率", f"{curtail_rate:.2f} %")
