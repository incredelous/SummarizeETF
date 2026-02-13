#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股板块指数分析器
"""
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import argparse
import sys
import os
import webbrowser
from datetime import datetime

import yaml

from utils.data_fetcher import DataFetcher
from utils.html_generator import HTMLGenerator


def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        default_paths = [
            'config.yaml',
            './config.yaml',
            os.path.join(os.path.dirname(__file__), 'config.yaml')
        ]
        for path in default_paths:
            if os.path.exists(path):
                config_path = path
                break
        else:
            print(f"错误: 配置文件不存在: {config_path}")
            sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def parse_arguments():
    parser = argparse.ArgumentParser(description='A股板块指数分析器')
    parser.add_argument('--config', '-c', default='config.yaml', help='配置文件路径')
    parser.add_argument('--output', '-o', default=None, help='输出HTML文件名')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器预览')
    parser.add_argument('--sectors', nargs='+', default=None, help='指定分析的板块列表')
    return parser.parse_args()


def main():
    print("=" * 60)
    print("        A股板块指数分析器")
    print("=" * 60)
    print()

    args = parse_arguments()
    print(f"📁 正在加载配置文件: {args.config}")
    config = load_config(args.config)
    print("✅ 配置文件加载成功")
    print()

    sectors_config = config.get('sectors', [])
    if args.sectors:
        sectors_config = [s for s in sectors_config if s.get('name') in args.sectors]

    print(f"📊 即将分析 {len(sectors_config)} 个板块:")
    for sector in sectors_config:
        print(f"   - {sector.get('name')} ({sector.get('code')})")
    print()

    print("🔄 正在初始化数据获取器...")
    data_fetcher = DataFetcher(config)
    print("✅ 数据获取器初始化成功")
    print()

    print("📥 正在获取板块数据，请稍候...")
    try:
        sector_data = data_fetcher.get_all_sector_data(sectors_config)
        print(f"✅ 成功获取 {len(sector_data)} 个板块的数据")
    except Exception as e:
        print(f"❌ 获取数据失败: {e}")
        sys.exit(1)

    print()

    print("🎨 正在生成HTML报告...")
    try:
        html_generator = HTMLGenerator(config)
        output_filename = args.output or f"a_stock_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        output_path = html_generator.generate_report(sector_data, output_filename)
        print(f"✅ 报告已生成: {output_path}")
    except Exception as e:
        print(f"❌ 生成报告失败: {e}")
        sys.exit(1)

    print()

    if not args.no_browser and config.get('output', {}).get('open_browser', True):
        print("🌐 正在打开浏览器预览...")
        try:
            webbrowser.open(f'file://{os.path.abspath(output_path)}')
            print("✅ 浏览器已打开")
        except Exception as e:
            print(f"⚠️  无法自动打开浏览器: {e}")

    print()
    print("=" * 60)
    print("        分析完成！")
    print("=" * 60)
    print()
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
