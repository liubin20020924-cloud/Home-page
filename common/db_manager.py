"""
统一数据库连接管理模块
使用连接池管理所有数据库连接
"""
import pymysql
from dbutils.pooled_db import PooledDB
import sys
import os

# 添加项目根目录到路径以导入config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# 数据库连接池字典
_db_pools = {}


def get_pool(db_name):
    """
    获取指定数据库的连接池

    Args:
        db_name: 数据库名称 ('home', 'kb', 'case')

    Returns:
        PooledDB: 数据库连接池实例
    """
    global _db_pools

    # 如果连接池已存在，直接返回
    if db_name in _db_pools:
        return _db_pools[db_name]

    # 根据数据库名称获取对应的数据库配置
    db_name_map = {
        'home': config.DB_NAME_HOME,
        'kb': config.DB_NAME_KB,
        'case': config.DB_NAME_CASE
    }

    if db_name not in db_name_map:
        raise ValueError(f"不支持的数据库名称: {db_name}")

    # 使用统一的数据库配置
    db_config = {
        'host': config.DB_HOST,
        'port': config.DB_PORT,
        'user': config.DB_USER,
        'password': config.DB_PASSWORD,
        'database': db_name_map[db_name],
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor  # 使用字典游标
    }

    # 创建连接池
    pool = PooledDB(
        creator=pymysql,
        maxconnections=config.DB_POOL_MAX_CONNECTIONS,
        mincached=config.DB_POOL_MIN_CACHED,
        maxcached=config.DB_POOL_MAX_CACHED,
        maxshared=config.DB_POOL_MAX_SHARED,
        blocking=True,
        ping=1,  # 自动检测连接是否有效
        **db_config
    )

    # 缓存连接池
    _db_pools[db_name] = pool
    print(f"数据库 {db_name} ({db_name_map[db_name]}) 连接池初始化成功")
    return pool


def get_connection(db_name):
    """
    获取数据库连接

    Args:
        db_name: 数据库名称 ('home', 'kb', 'case')

    Returns:
        Connection: 数据库连接对象
    """
    try:
        pool = get_pool(db_name)
        return pool.connection()
    except Exception as e:
        print(f"获取 {db_name} 数据库连接失败: {e}")
        return None


def close_all_pools():
    """关闭所有数据库连接池"""
    global _db_pools
    for pool_name, pool in _db_pools.items():
        try:
            pool.close()
            print(f"数据库 {pool_name} 连接池已关闭")
        except Exception as e:
            print(f"关闭数据库 {pool_name} 连接池失败: {e}")
    _db_pools.clear()


def get_pool_stats(db_name):
    """
    获取连接池状态信息

    Args:
        db_name: 数据库名称

    Returns:
        dict: 连接池状态
    """
    try:
        pool = get_pool(db_name)
        return {
            'db_name': db_name,
            'maxconnections': pool._maxconnections,
            'mincached': pool._mincached,
            'maxcached': pool._maxcached,
            'maxshared': pool._maxshared,
            '_connections': len(pool._connections) if hasattr(pool, '_connections') else 0
        }
    except Exception as e:
        return {'error': str(e)}
