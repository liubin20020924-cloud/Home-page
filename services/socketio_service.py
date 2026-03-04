"""
SocketIO 事件服务 - 处理 WebSocket 事件
工单系统实时通信
"""
from flask import request, session
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
from common.database_context import db_connection
from common.logger import logger

# 全局 socketio 实例，用于从外部发送消息
socketio_instance = None


def register_socketio_events(socketio):
    """注册SocketIO事件"""
    global socketio_instance
    socketio_instance = socketio
    """注册SocketIO事件"""

    @socketio.on('connect')
    def handle_connect():
        logger.info(f'客户端已连接：{request.sid}')

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f'客户端已断开连接：{request.sid}')

    @socketio.on('join')
    def handle_join(data):
        ticket_id = data.get('ticket_id')
        username = data.get('username')
        role = data.get('role')

        if ticket_id:
            room = f'ticket_{ticket_id}'
            join_room(room)
            logger.info(f'{username} ({role}) 加入了工单 {ticket_id} 聊天室')

            emit('notification', {
                'message': f'{username} 加入了聊天',
                'role': role
            }, room=room, skip_sid=request.sid)

    @socketio.on('leave')
    def handle_leave(data):
        ticket_id = data.get('ticket_id')
        username = data.get('username')

        if ticket_id:
            room = f'ticket_{ticket_id}'
            leave_room(room)
            logger.info(f'{username} 离开了工单 {ticket_id} 聊天室')

            emit('notification', {
                'message': f'{username} 离开了聊天',
            }, room=room, skip_sid=request.sid)

    @socketio.on('send_message')
    def handle_send_message(data):
        ticket_id = data.get('ticket_id')
        content = data.get('content')
        
        sender = session.get('role')
        sender_name = session.get('display_name') or session.get('username', '匿名用户')

        if not all([ticket_id, sender, content]):
            return {'success': False, 'message': '消息参数不完整'}

        try:
            with db_connection('case') as conn:
                cursor = conn.cursor()
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                insert_sql = """
                    INSERT INTO messages (ticket_id, sender, sender_name, content, send_time)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (ticket_id, sender, sender_name, content, now))
                conn.commit()
                message_id = cursor.lastrowid

            message_data = {
                'id': message_id,
                'ticket_id': ticket_id,
                'sender': sender,
                'sender_name': sender_name,
                'content': content,
                'send_time': now
            }

            room = f'ticket_{ticket_id}'
            emit('new_message', message_data, room=room)

            logger.info(f"工单 {ticket_id} 新消息: {sender_name}")
            return {'success': True, 'message': '消息发送成功'}
        except Exception as e:
            logger.error(f"发送消息异常：{e}")
            return {'success': False, 'message': f'发送失败：{str(e)}'}


def init_case_database():
    """初始化工单系统数据库表"""
    try:
        with db_connection('case') as conn:
            cursor = conn.cursor()

            create_ticket_sql = """
                CREATE TABLE IF NOT EXISTS tickets (
                    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增ID',
                    ticket_id VARCHAR(32) NOT NULL UNIQUE COMMENT '工单唯一标识ID',
                    customer_name VARCHAR(100) NOT NULL COMMENT '客户名称',
                    customer_contact VARCHAR(50) NOT NULL COMMENT '客户联系方式',
                    customer_email VARCHAR(100) NOT NULL COMMENT '客户邮箱',
                    product VARCHAR(50) NOT NULL COMMENT '涉及产品',
                    issue_type VARCHAR(20) NOT NULL COMMENT '问题类型',
                    priority VARCHAR(10) NOT NULL COMMENT '工单优先级',
                    title VARCHAR(200) NOT NULL COMMENT '问题标题',
                    content TEXT NOT NULL COMMENT '问题详情',
                    status VARCHAR(10) DEFAULT 'pending' COMMENT '工单状态',
                    assignee VARCHAR(50) DEFAULT NULL COMMENT '处理人',
                    create_time DATETIME NOT NULL COMMENT '创建时间',
                    update_time DATETIME NOT NULL COMMENT '更新时间',
                    INDEX idx_ticket_id (ticket_id),
                    INDEX idx_customer_name (customer_name),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工单系统主表'
            """

            create_message_sql = """
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
                    ticket_id VARCHAR(32) NOT NULL COMMENT '工单ID',
                    sender VARCHAR(20) NOT NULL COMMENT '发送者',
                    sender_name VARCHAR(100) NOT NULL COMMENT '发送者名称',
                    content TEXT NOT NULL COMMENT '消息内容',
                    send_time DATETIME NOT NULL COMMENT '发送时间',
                    INDEX idx_ticket_id (ticket_id),
                    INDEX idx_send_time (send_time)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工单聊天消息表'
            """

            cursor.execute(create_ticket_sql)
            cursor.execute(create_message_sql)
            conn.commit()
            logger.info("工单系统数据库表初始化成功")
    except Exception as e:
        logger.error(f"工单系统数据库初始化失败：{e}")


def emit_ticket_update(ticket_id):
    """发送工单更新事件到所有客户端"""
    global socketio_instance
    if socketio_instance:
        socketio_instance.emit('ticket_update', {'ticket_id': ticket_id})
