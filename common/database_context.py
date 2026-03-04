"""
数据库连接上下文管理器
提供自动管理数据库连接的上下文管理器
"""
from contextlib import contextmanager
from common.db_manager import get_connection
from common.logger import logger


class DatabaseConnectionError(Exception):
    """数据库连接错误"""
    pass


@contextmanager
def db_connection(db_name):
    """数据库连接上下文管理器
    
    提供自动管理数据库连接的上下文管理器，确保连接在使用后正确关闭。
    使用连接池获取连接，并在异常发生时自动回滚事务。
    
    Args:
        db_name (str): 数据库名称，可选值为 'home', 'kb', 'case'
    
    Yields:
        pymysql.connections.Connection: 数据库连接对象，已配置为使用字典游标
    
    Raises:
        DatabaseConnectionError: 当无法连接到数据库时抛出
        Exception: 数据库操作过程中发生的其他异常
    
    Example:
        >>> from common.database_context import db_connection
        >>> 
        >>> # 简单查询
        >>> with db_connection('kb') as conn:
        ...     cursor = conn.cursor(pymysql.cursors.DictCursor)
        ...     cursor.execute("SELECT * FROM users WHERE role = %s", ('admin',))
        ...     users = cursor.fetchall()
        >>> 
        >>> # 事务操作
        >>> try:
        ...     with db_connection('kb') as conn:
        ...         cursor = conn.cursor()
        ...         cursor.execute("INSERT INTO users ...")
        ...         cursor.execute("UPDATE other_table ...")
        ...         conn.commit()
        ... except Exception:
        ...     # 连接会自动回滚和关闭
    
    Note:
        - 连接会在上下文退出时自动关闭
        - 发生异常时会自动回滚事务
        - 推荐始终使用字典游标（pymysql.cursors.DictCursor）
    """
    conn = get_connection(db_name)
    if not conn:
        logger.error(f"无法连接到 {db_name} 数据库")
        raise DatabaseConnectionError(f"数据库连接失败: {db_name}")
    
    try:
        yield conn
    except Exception as e:
        logger.error(f"数据库操作异常 [{db_name}]: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
            logger.debug(f"释放数据库连接 [{db_name}]")
