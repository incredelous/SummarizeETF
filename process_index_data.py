"""
整理中证指数数据并映射行业估值
"""

import pandas as pd
import os
import numpy as np

# 读取数据
df_index = pd.read_excel('data/指数列表.xlsx')
df_valuation = pd.read_excel('data/csi20260209_20260209230824.xls')

# 整理指数数据
df_index_clean = df_index.iloc[:, :3].copy()
df_index_clean.columns = ['代码', '简称', '全称']

# 整理行业估值 - 转换数值列
df_valuation.columns = ['行业代码', '行业名称', '市盈率_静态', '股票数量', '变化', '市盈率_TTM', '市净率', '市销率', '股息率']

# 转换为数值
for col in ['市盈率_TTM', '市净率', '股息率']:
    df_valuation[col] = pd.to_numeric(df_valuation[col], errors='coerce')

df_industry = df_valuation[df_valuation['行业代码'].astype(str).str.len() == 4].copy()

# 中证一级行业代码与行业类别映射
industry_map = {
    '1010': '能源',
    '1510': '材料',
    '1520': '材料',
    '1530': '材料',
    '1540': '材料',
    '1550': '材料',
    '2010': '工业',
    '2020': '工业',
    '2030': '工业',
    '2040': '工业',
    '2050': '工业',
    '2060': '工业',
    '2070': '工业',
    '2510': '可选消费',
    '2520': '可选消费',
    '2530': '可选消费',
    '2540': '可选消费',
    '2550': '工业',
    '3010': '必需消费',
    '3020': '必需消费',
    '3030': '必需消费',
    '3510': '医药卫生',
    '3520': '医药卫生',
    '4010': '金融',
    '4020': '金融',
    '4030': '金融',
    '4040': '金融',
    '4510': '信息技术',
    '4520': '信息技术',
    '4530': '电信服务',
    '5010': '公用事业',
    '5020': '公用事业',
    '5030': '电信服务',
    '5510': '房地产',
    '6010': '房地产',
}

# 添加行业类别
df_industry['行业类别'] = df_industry['行业代码'].astype(str).map(industry_map)

# 计算行业类别平均估值
df_industry_avg = df_industry.groupby('行业类别').agg({
    '市盈率_TTM': 'mean',
    '市净率': 'mean',
    '股息率': 'mean'
}).reset_index()

print("=== 行业类别平均估值 ===")
print(df_industry_avg.to_string(index=False))

# 筛选中证一级行业指数
keywords = ['能源', '材料', '工业', '制造', '可选消费', '必需消费', '食品', '饮料',
            '医药', '医疗', '卫生', '制药',
            '银行', '证券', '保险', '非银', '金融',
            '电子', '信息', '计算机', '软件',
            '电信', '通信', '传媒',
            '公用', '电力', '水务', '燃气',
            '房地产', '地产']

df_csi = df_index_clean[
    df_index_clean['全称'].str.contains('|'.join(keywords), na=False) &
    df_index_clean['全称'].str.contains('中证', na=False) &
    df_index_clean['全称'].str.contains('指数', na=False)
].copy()

# 手动映射指数到行业类别
def map_to_industry(name):
    name = str(name)
    if '能源' in name:
        return '能源'
    elif '材料' in name:
        return '材料'
    elif '工业' in name or '制造' in name:
        return '工业'
    elif '可选消费' in name or '消费服务' in name:
        return '可选消费'
    elif '必需消费' in name or '食品' in name or '饮料' in name or '农业' in name:
        return '必需消费'
    elif '医药' in name or '医疗' in name or '卫生' in name or '制药' in name:
        return '医药卫生'
    elif '银行' in name or '证券' in name or '保险' in name or '非银' in name or '金融' in name:
        return '金融'
    elif '电子' in name or '信息' in name or '计算机' in name or '软件' in name:
        return '信息技术'
    elif '电信' in name or '通信' in name or '传媒' in name:
        return '电信服务'
    elif '公用' in name or '电力' in name or '水务' in name or '燃气' in name:
        return '公用事业'
    elif '房地产' in name or '地产' in name:
        return '房地产'
    return None

df_csi['行业类别'] = df_csi['全称'].apply(map_to_industry)
df_csi = df_csi[df_csi['行业类别'].notna()].copy()

# 合并行业平均估值
df_final = df_csi.merge(df_industry_avg, on='行业类别', how='left')

# 选择并排序列
df_result = df_final[['代码', '简称', '全称', '行业类别', '市盈率_TTM', '市净率', '股息率']].copy()
df_result.columns = ['指数代码', '指数简称', '指数全称', '对应行业', '市盈率(TTM)', '市净率', '股息率(%)']

# 按行业类别和代码排序
df_result = df_result.sort_values(['对应行业', '指数代码']).reset_index(drop=True)

print("\n=== 中证行业指数估值汇总 ===")
print(df_result.to_string(index=False))

# 保存
df_result.to_excel('data/中证行业指数估值汇总.xlsx', index=False)
print("\n已保存: data/中证行业指数估值汇总.xlsx")
