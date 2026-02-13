"""
测试 Tushare API Key 是否有效
"""

import tushare as ts
import yaml
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_tushare_api():
    # 读取配置文件
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    token = config.get('tushare', {}).get('token', '')
    
    if not token:
        logger.error("❌ 错误: 未配置 Tushare Token")
        return False
    
    logger.info(f"Token: {token[:10]}...{token[-10:]}")
    
    try:
        # 设置 token
        ts.set_token(token)
        pro = ts.pro_api()
        
        # 测试获取每日指标（请求一个股票代码的当日数据）
        df = pro.daily(ts_code='000001.SZ', start_date='20250101', limit=1)
        
        if df is not None and not df.empty:
            logger.info("✅ Tushare API 测试成功!")
            logger.info(f"   成功获取数据: {len(df)} 条记录")
            logger.info(f"   示例数据: {df.to_dict('records')[0]}")
            return True
        else:
            logger.error("❌ API 调用成功但返回空数据")
            return False
            
    except Exception as e:
        logger.error(f"❌ Tushare API 测试失败: {e}")
        if "权限" in str(e) or "permission" in str(e).lower():
            logger.error("   提示: 该接口可能需要更高积分权限")
        return False


if __name__ == "__main__":
    success = test_tushare_api()
    exit(0 if success else 1)
