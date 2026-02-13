"""
数据获取模块
使用Tushare或akshare获取A股板块指数、ETF和估值数据
优先使用Tushare，无Token时使用akshare
"""

import tushare as ts
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    def __init__(self, config: dict):
        self.config = config
        self.history_years = config.get('data', {}).get('history_years', 5)
        self.pro = None
        self._init_data_source()
    
    def _init_data_source(self):
        token = self.config.get('tushare', {}).get('token', '')
        if token:
            try:
                ts.set_token(token)
                self.pro = ts.pro_api()
                logger.info("Tushare Pro API 初始化成功")
            except Exception as e:
                logger.warning(f"Tushare初始化失败: {e}")
                self.pro = None
        else:
            logger.info("未配置Tushare Token，将使用akshare数据源")
    
    def _get_index_code_tushare(self, code: str) -> str:
        """将指数代码转换为Tushare格式"""
        code = str(code).strip()
        if code.startswith('399') or code.startswith('000'):
            return f"{code}.SH" if code.startswith('000') else f"{code}.SZ"
        return f"{code}.SH"
    
    def _get_stock_code(self, code: str) -> str:
        """将股票/ETF代码转换为akshare格式"""
        code = str(code).strip()
        if code.startswith(('5', '1')):
            return f"sz.{code}" if code.startswith('1') else f"sz.{code}"
        elif code.startswith(('6', '8')):
            return f"sh.{code}"
        else:
            return f"sz.{code}"
    
    def get_sector_indices(self, sector_code: str, sector_name: str, index_name: str = "") -> Dict:
        try:
            logger.info(f"正在获取 {sector_name} ({index_name}) 指数数据...")
            
            start_date = (datetime.now() - timedelta(days=self.history_years*365)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            if self.pro:
                ts_code = self._get_index_code_tushare(sector_code)
                try:
                    df = self.pro.index_daily(
                        ts_code=ts_code,
                        start_date=start_date.replace('-', ''),
                        end_date=end_date.replace('-', '')
                    )
                    if df is not None and not df.empty:
                        df = df.sort_values('trade_date')
                        df['close'] = pd.to_numeric(df['close'], errors='coerce')
                        df['high'] = pd.to_numeric(df['high'], errors='coerce')
                        df['low'] = pd.to_numeric(df['low'], errors='coerce')
                        df = df.dropna(subset=['close'])
                        
                        if not df.empty:
                            return {
                                'name': sector_name,
                                'code': sector_code,
                                'index_name': index_name,
                                'data': df,
                                'current_price': float(df['close'].iloc[-1]),
                                'high': float(df['high'].max()),
                                'low': float(df['low'].min()),
                                'mean': float(df['close'].mean())
                            }
                except Exception as e:
                    logger.warning(f"Tushare获取 {sector_name} 失败: {e}")
            
            logger.info(f"使用akshare获取 {sector_name}...")
            return self._get_from_akshare(sector_code, sector_name, index_name, start_date, end_date)
            
        except Exception as e:
            logger.error(f"获取 {sector_name} 数据失败: {e}")
            return self._get_sector_backup(sector_code, sector_name, index_name)
    
    def _get_from_akshare(self, sector_code: str, sector_name: str, index_name: str, start_date: str, end_date: str) -> Dict:
        """使用akshare获取指数数据"""
        try:
            bs_code = self._get_stock_code(sector_code)
            rs = ak.stock_zh_index_daily(symbol=bs_code.replace('sh.', '').replace('sz.', ''))
            
            if rs is not None and not rs.empty:
                rs['close'] = pd.to_numeric(rs['close'], errors='coerce')
                rs['high'] = pd.to_numeric(rs['high'], errors='coerce')
                rs['low'] = pd.to_numeric(rs['low'], errors='coerce')
                rs = rs.dropna(subset=['close'])
                
                if not rs.empty:
                    return {
                        'name': sector_name,
                        'code': sector_code,
                        'index_name': index_name,
                        'data': rs,
                        'current_price': float(rs['close'].iloc[-1]),
                        'high': float(rs['high'].max()),
                        'low': float(rs['low'].min()),
                        'mean': float(rs['close'].mean())
                    }
        except Exception as e:
            logger.warning(f"akshare获取 {sector_name} 失败: {e}")
        
        return self._get_sector_backup(sector_code, sector_name, index_name)
    
    def _get_sector_backup(self, sector_code: str, sector_name: str, index_name: str = "") -> Dict:
        return {
            'name': sector_name,
            'code': sector_code,
            'index_name': index_name,
            'data': pd.DataFrame(),
            'current_price': 0,
            'high': 0,
            'low': 0,
            'mean': 0
        }
    
    def get_etf_info(self, etf_list: List[Dict]) -> List[Dict]:
        result = []
        for etf in etf_list:
            code = etf.get('code', '')
            name = etf.get('name', '')
            
            try:
                logger.info(f"正在获取ETF {name} ({code}) 信息...")
                
                bs_code = self._get_stock_code(code)
                symbol = bs_code.replace('sh.', '').replace('sz.', '')
                
                try:
                    df = ak.fund_etf_hist_em(
                        symbol=symbol,
                        period="daily",
                        start_date=(datetime.now() - timedelta(days=30)).strftime("%Y%m%d"),
                        end_date=datetime.now().strftime("%Y%m%d"),
                        adjust="qfq"
                    )
                    
                    if df is not None and not df.empty:
                        df['close'] = pd.to_numeric(df['close'], errors='coerce')
                        df['pct_chg'] = pd.to_numeric(df.get('pct_chg', 0), errors='coerce')
                        
                        result.append({
                            'code': code,
                            'name': name,
                            'price': float(df['close'].iloc[-1]),
                            'change': float(df['pct_chg'].iloc[-1]) if 'pct_chg' in df.columns else 0
                        })
                        time.sleep(0.3)
                        continue
                except Exception as e:
                    logger.warning(f"获取ETF {code} 数据失败: {e}")
                
                result.append({
                    'code': code,
                    'name': name,
                    'price': 0,
                    'change': 0
                })
                time.sleep(0.3)
                
            except Exception as e:
                logger.warning(f"获取ETF {name} 信息失败: {e}")
                result.append({
                    'code': code,
                    'name': name,
                    'price': 0,
                    'change': 0
                })
        
        return result
    
    def get_etf_valuation(self, etf_code: str) -> Dict:
        logger.info(f"正在获取ETF {etf_code} 估值数据...")
        return {}
    
    def get_etf_holdings(self, etf_code: str, top_n: int = 10) -> List[Dict]:
        try:
            logger.info(f"正在获取ETF {etf_code} 持仓数据...")
            
            symbol = etf_code
            if not symbol.startswith(('5', '1', '6', '8', '0')):
                return []
            
            try:
                import akshare.fund as fund
                df = fund.fund_portfolio_em(symbol=symbol)
                if df is not None and not df.empty:
                    holdings = []
                    df = df.head(top_n)
                    for _, row in df.iterrows():
                        holdings.append({
                            'code': str(row.get('代码', '')),
                            'name': str(row.get('名称', '')),
                            'proportion': float(row.get('持仓占比', 0))
                        })
                    return holdings
            except Exception as e:
                logger.warning(f"获取ETF {etf_code} 持仓失败: {e}")
            
            return []
            
        except Exception as e:
            logger.error(f"获取ETF {etf_code} 持仓失败: {e}")
            return []
    
    def get_all_sector_data(self, sectors_config: List[Dict]) -> List[Dict]:
        all_data = []
        
        for sector in sectors_config:
            sector_name = sector.get('name')
            sector_code = sector.get('code')
            index_name = sector.get('index_name', '')
            etf_configs = sector.get('etf', [])
            
            logger.info(f"\n{'='*50}")
            logger.info(f"处理板块: {sector_name} ({index_name})")
            logger.info(f"{'='*50}")
            
            sector_data = self.get_sector_indices(sector_code, sector_name, index_name)
            etf_list = self.get_etf_info(etf_configs)
            
            for etf in etf_list:
                etf_code = etf.get('code')
                valuation = self.get_etf_valuation(etf_code)
                holdings = self.get_etf_holdings(etf_code)
                
                etf.update({
                    'pe': valuation.get('pe'),
                    'pb': valuation.get('pb'),
                    'holdings': holdings
                })
            
            sector_data['etfs'] = etf_list
            all_data.append(sector_data)
            
            time.sleep(0.5)
        
        return all_data


def calculate_percentile(current: float, historical: List[float]) -> float:
    if not historical or len(historical) < 2:
        return 50.0
    
    historical_array = np.array(historical)
    below_count = np.sum(historical_array < current)
    percentile = (below_count / len(historical_array)) * 100
    
    return min(100, max(0, percentile))


def get_color_by_percentile(percentile: float, config: dict) -> str:
    low_threshold = config.get('percentile', {}).get('low', 30)
    high_threshold = config.get('percentile', {}).get('high', 70)
    colors = config.get('colors', {})
    
    if percentile < low_threshold:
        return colors.get('low', '#4CAF50')
    elif percentile > high_threshold:
        return colors.get('high', '#F44336')
    else:
        return colors.get('medium', '#FFC107')
