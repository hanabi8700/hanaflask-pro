import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# 1. 日本語フォントの設定（環境に合わせて調整してください。Windowsは 'MS Gothic'、Macは 'Hiragino Sans' など）
plt.rcParams["font.family"] = "MS Gothic"

# 2. サンプルデータの作成（24時間 × 7曜日）
hours = [f"{i:02d}:00" for i in range(24)]
days = ["月", "火", "水", "木", "金", "土", "日"]

# 11時〜18時に着信が集中するような疑似データを生成
np.random.seed(42)
base_data = np.random.randint(1, 10, size=(24, 7))
base_data[11:19, :] += np.random.randint(
    20, 50, size=(8, 7)
)  # 11:00〜18:59の着信を増やす

df = pd.DataFrame(base_data, index=hours, columns=days)

# 3. ヒートマップの描画
plt.figure(figsize=(10, 8))
sns.heatmap(
    df,
    cmap="YlOrRd",  # 色のグラデーション（黄色〜赤）。青系なら 'Blues'
    annot=True,  # 各マスに数値を表示（非表示にしたい場合は False）
    fmt="d",  # 数値のフォーマット（整数）
    cbar_kws={"label": "着信数（相対値）"},
)

plt.title("曜日・時間帯別の着信分布（11時〜18時に集中）", fontsize=14, pad=15)
plt.xlabel("曜日", fontsize=12)
plt.ylabel("時間帯", fontsize=12)
plt.tight_layout()

# 画像として保存する場合
# plt.savefig('call_distribution.png', dpi=300)

plt.show()
