import pandas as pd

# 读取指数列表
df_index = pd.read_excel('data/指数列表.xlsx')
print("=== 指数列表.xlsx ===")
print(f"Shape: {df_index.shape}")
print(f"Columns: {list(df_index.columns)}")
print(df_index.head(20).to_string())

print("\n\n")

# 读取中证行业估值
df_valuation = pd.read_excel('data/csi20260209_20260209230824.xls')
print("=== 中证行业估值.xls ===")
print(f"Shape: {df_valuation.shape}")
print(f"Columns: {list(df_valuation.columns)}")
print(df_valuation.head(30).to_string())
