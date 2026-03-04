"""
用户服务类
统一管理用户相关的业务逻辑，消除重复代码
"""
from typing import Dict, Optional, Tuple, Any
from werkzeug.security import generate_password_hash
from common.unified_auth import create_user, authenticate_user
from common.logger import logger


class UserService:
    """用户服务类"""
    
    @staticmethod
    def update_user(conn, user_id: int, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        更新用户信息（统一方法）
        
        Args:
            conn: 数据库连接
            user_id: 用户ID
            data: 要更新的数据字典
            
        Returns:
            (success, message)
        """
        try:
            cursor = conn.cursor()
            
            # 构建更新SQL
            update_fields = []
            update_values = []
            
            # 处理可更新字段
            if 'display_name' in data:
                update_fields.append('display_name = %s')
                update_values.append(data['display_name'])

            if 'role' in data:
                update_fields.append('role = %s')
                update_values.append(data['role'])
            
            if 'status' in data:
                update_fields.append('status = %s')
                update_values.append(data['status'])
            
            if 'email' in data:
                update_fields.append('email = %s')
                update_values.append(data['email'])
            
            if 'phone' in data:
                update_fields.append('phone = %s')
                update_values.append(data['phone'])
            
            if 'company_name' in data:
                update_fields.append('company_name = %s')
                update_values.append(data['company_name'])
            
            # 处理密码更新
            if 'password' in data and data['password']:
                password_hash = generate_password_hash(data['password'])
                update_fields.append('password_hash = %s')
                update_values.append(password_hash)
                update_fields.append('password_type = %s')
                update_values.append('werkzeug')
            
            # 添加WHERE条件参数
            update_values.append(user_id)
            
            # 执行更新
            if update_fields:
                sql = f"UPDATE `users` SET {', '.join(update_fields)} WHERE id = %s"
                cursor.execute(sql, update_values)
                conn.commit()
                logger.info(f"更新用户 {user_id} 成功")
                return True, "用户更新成功"
            else:
                return False, "没有提供要更新的字段"
                
        except Exception as e:
            logger.error(f"更新用户失败: {e}")
            conn.rollback()
            return False, f"更新用户失败：{str(e)}"
    
    @staticmethod
    def get_user(conn, user_id: int) -> Optional[Dict]:
        """
        获取用户信息
        
        Args:
            conn: 数据库连接
            user_id: 用户ID
            
        Returns:
            用户信息字典，如果不存在返回None
        """
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, display_name, email, phone, role, status, created_at, last_login, company_name FROM `users` WHERE id = %s",
                (user_id,)
            )
            user = cursor.fetchone()

            if user:
                columns = ['id', 'username', 'display_name', 'email', 'phone', 'role', 'status', 'created_at', 'last_login', 'company_name']
                return dict(zip(columns, user))
            return None
            
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    @staticmethod
    def get_users(conn, filters: Optional[Dict] = None, limit: int = 100, offset: int = 0) -> Tuple[list, int]:
        """
        获取用户列表
        
        Args:
            conn: 数据库连接
            filters: 过滤条件
            limit: 限制数量
            offset: 偏移量
            
        Returns:
            (用户列表, 总数)
        """
        try:
            cursor = conn.cursor()
            
            # 构建查询条件
            where_conditions = []
            params = []
            
            if filters:
                if filters.get('username'):
                    where_conditions.append("username LIKE %s")
                    params.append(f"%{filters['username']}%")
                
                if filters.get('role'):
                    where_conditions.append("role = %s")
                    params.append(filters['role'])
                
                if filters.get('status'):
                    where_conditions.append("status = %s")
                    params.append(filters['status'])
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            # 查询总数
            count_sql = f"SELECT COUNT(*) FROM `users` {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()[0]
            
            # 查询列表
            list_sql = f"""
            SELECT id, username, display_name, email, phone, role, status, created_at, last_login, company_name
            FROM `users`
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """
            cursor.execute(list_sql, params + [limit, offset])
            rows = cursor.fetchall()

            columns = ['id', 'username', 'display_name', 'email', 'phone', 'role', 'status', 'created_at', 'last_login', 'company_name']
            users = [dict(zip(columns, row)) for row in rows]
            
            return users, total
            
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return [], 0
    
    @staticmethod
    def delete_user(conn, user_id: int) -> Tuple[bool, str]:
        """
        删除用户
        
        Args:
            conn: 数据库连接
            user_id: 用户ID
            
        Returns:
            (success, message)
        """
        try:
            cursor = conn.cursor()
            
            # 检查用户是否存在
            cursor.execute("SELECT id FROM `users` WHERE id = %s", (user_id,))
            if not cursor.fetchone():
                return False, "用户不存在"
            
            # 执行删除
            cursor.execute("DELETE FROM `users` WHERE id = %s", (user_id,))
            conn.commit()
            
            logger.info(f"删除用户 {user_id} 成功")
            return True, "用户删除成功"
            
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            conn.rollback()
            return False, f"删除用户失败：{str(e)}"
    
    @staticmethod
    def change_password(conn, user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        修改密码
        
        Args:
            conn: 数据库连接
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            (success, message)
        """
        try:
            cursor = conn.cursor()
            
            # 获取用户当前密码
            cursor.execute("SELECT username, password_hash FROM `users` WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return False, "用户不存在"
            
            username, current_hash = user
            
            # 验证旧密码
            auth_result, _ = authenticate_user(username, old_password)
            if not auth_result:
                return False, "旧密码错误"
            
            # 更新密码
            new_hash = generate_password_hash(new_password)
            cursor.execute(
                "UPDATE `users` SET password_hash = %s, password_type = %s WHERE id = %s",
                (new_hash, 'werkzeug', user_id)
            )
            conn.commit()
            
            logger.info(f"用户 {username} 修改密码成功")
            return True, "密码修改成功"
            
        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            conn.rollback()
            return False, f"修改密码失败：{str(e)}"
