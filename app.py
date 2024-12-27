import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.title("幸福量シミュレータ")

# このアプリケーションの趣旨の説明文
st.markdown(r"""\
このアプリケーションは、年齢と幸福度の関係を入力し、幸福度の積分を計算するものです。  
幸福度は、年齢が増えるにつれてどのように変化するのか、ステップ関数で表現してください。  
体感時間はジャネーの法則に従うと仮定し、年齢 $y$ に対して $1/(y+1)$ で表せると仮定します。  
幸福度の関数を $f(x)$ とすると、そう幸福量は次のように表されます。  

$$
\int_{0}^{N} f(y) \cdot \frac{1}{y+1} dy.
$$

ただし、$N$ は寿命です。
""")

# ──────────────────────────────────────────────────────
# 初期データ
# ──────────────────────────────────────────────────────
initial_data = {
    "Age": [0, 10, 20, 30, 40, 50, 100],
    "Happiness": [0.5, 0.6, 0.7, 0.8, 0.6, 0.7, 0.7],
}
df_initial = pd.DataFrame(initial_data)

# ──────────────────────────────────────────────────────
# Data Editor（表）
# ──────────────────────────────────────────────────────
st.subheader("年齢と幸福度を入力・編集してください")
df_edited = st.data_editor(
    df_initial,
    num_rows="dynamic",  # 行の追加・削除を可能に
    use_container_width=True,
)

st.subheader("現在入力されているデータのステップグラフ")

# NaN や重複・負値などを想定し、適宜バリデーションする場合は調整してください
df_no_na = df_edited.dropna(subset=["Age", "Happiness"])

# 年齢でソート
df_no_na = df_no_na.sort_values("Age")

# Altair でステップ状の線グラフを描画する
# "step-before" を指定すると、左側の点の値を次の点まで一定に保つステップが描画される
chart = (
    alt.Chart(df_no_na)
    .mark_line(interpolate="step-after", point=True)
    .encode(
        x=alt.X("Age", title="年齢"),
        y=alt.Y("Happiness", title="幸福度"),
        tooltip=["Age", "Happiness"],
    )
    .interactive()
)
# じゃねーの法則に基づく、体感時間の関数も描画する。ただし区間は0歳から100歳までとする
x = np.linspace(0, 100, 500)
y = 1 / (x + 1)
df_janee = pd.DataFrame({"Age": x, "Happiness": y})
chart_janee = (
    alt.Chart(df_janee).mark_line(color="red").encode(x="Age", y="Happiness")
)

# st.altair_chart(chart, use_container_width=True)
st.altair_chart(chart + chart_janee, use_container_width=True)

# ──────────────────────────────────────────────────────
# 「計算する」ボタンで、ステップ関数での数値積分(ジャネーの法則)を実装
# ──────────────────────────────────────────────────────
ages = df_no_na["Age"].values
happies = df_no_na["Happiness"].values

if len(ages) < 2:
    st.warning("少なくとも2つ以上の (Age, Happiness) が必要です。")
else:
    total_area = 0.0

    # 年齢の昇順に並んだデータでステップ関数積分を実行
    for i in range(len(ages) - 1):
        x0 = ages[i]
        x1 = ages[i + 1]
        h0 = happies[i]  # 左端の幸福度を区間全体で一定とみなす

        # ステップ関数 f(x) = h0 を、ジャネーの法則の重み 1/(x+1) と掛け合わせた積分
        # ∫[x0, x1] h0/(x+1) dx = h0 * [ln(x+1)] from x0 to x1
        segment_area = h0 * (np.log(x1 + 1) - np.log(x0 + 1))
        total_area += segment_area

    st.write(f"総幸福量: **{total_area:.5f}**")
