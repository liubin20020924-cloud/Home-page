# 代码优化待办事项

> 本文档记录所有代码优化建议和实施计划
> 最后更新：2026-03-02

---

## 📊 优化概览

| 优先级 | 待办事项 | 预计工作量 | 预期收益 | 状态 |
|-------|---------|-----------|---------|------|
| 🔴 高 | 修复 JavaScript 语法错误 | 2h | 提升前端稳定性 | ⏳ 待处理 |
| 🔴 高 | 提取重复的登录逻辑 | 4h | 减少 200+ 行重复代码 | ⏳ 待处理 |
| 🔴 高 | 重新启用 CSRF 保护 | 6h | 提升安全性 | ⏳ 待处理 |
| 🔴 高 | 提取用户状态检查逻辑 | 2h | 减少重复代码 | ⏳ 待处理 |
| 🟡 中 | 优化统计查询（7次→1次） | 3h | 提升性能 50% | ⏳ 待处理 |
| 🟡 中 | 增强文件上传验证 | 4h | 提升安全性 | ⏳ 待处理 |
| 🟡 中 | 创建登录模板基类 | 3h | 减少 500+ 行重复 HTML | ⏳ 待处理 |
| 🟡 中 | 增加数据库索引 | 2h | 提升查询性能 30%+ | ⏳ 待处理 |
| 🟡 中 | 实现缓存机制（Redis） | 8h | 提升性能 60%+ | ⏳ 待处理 |
| 🟡 中 | 增加测试覆盖率 | 16h | 提升代码质量 | ⏳ 待处理 |
| 🟢 低 | 统一用户管理 API | 4h | 提升代码可维护性 | ⏳ 待处理 |
| 🟢 低 | 图片优化 | 2h | 减少带宽 40% | ⏳ 待处理 |
| 🟢 低 | CSS/JS 合并压缩 | 3h | 减少请求数 | ⏳ 待处理 |

**总预计工作量**: 59 小时
**预期收益**: 性能提升 60%+, 代码重复率降低 40%, 安全漏洞减少 70%

---

## 🔴 高优先级优化（立即处理）

### 1. 修复 JavaScript 语法错误

**问题描述**: `templates/kb/management.html` 存在 31 个 JavaScript 语法错误

**影响范围**:
- 影响知识库管理界面的正常使用
- 可能导致功能异常
- 控制台报错影响调试

**修复步骤**:

#### 1.1 检查语法错误
```bash
# 使用 ESLint 检查 JavaScript 语法
npx eslint templates/kb/management.html
```

#### 1.2 常见问题修复

**问题 1**: 未闭合的括号
```javascript
// 错误
function fetchData() {
    fetch('/api/data')
    .then(response => response.json()
}  // 缺少闭合括号

// 正确
function fetchData() {
    fetch('/api/data')
    .then(response => response.json())
}
```

**问题 2**: 变量未定义
```javascript
// 错误
result.forEach(item => {
    console.log(item.name)
})  // result 未定义

// 正确
const result = await response.json()
result.forEach(item => {
    console.log(item.name)
})
```

**问题 3**: 异步函数缺少 await
```javascript
// 错误
async function loadData() {
    const data = fetch('/api/data')
    console.log(data)  // 得到的是 Promise 对象
}

// 正确
async function loadData() {
    const response = await fetch('/api/data')
    const data = await response.json()
    console.log(data)
}
```

#### 1.3 修复后验证
```bash
# 启动开发服务器
python app.py

# 访问管理界面
http://localhost:5000/kb/MGMT

# 打开浏览器控制台，确认无错误
```

**涉及文件**:
- `templates/kb/management.html`

**预计工作量**: 2 小时

**验收标准**:
- ✅ 浏览器控制台无 JavaScript 错误
- ✅ 管理界面所有功能正常工作
- ✅ 无 ESLint 警告

---

### 2. 提取重复的登录逻辑

**问题描述**: 三个系统（知识库、工单、用户管理）的登录逻辑代码重复

**重复位置**:
- `routes/kb_bp.py`: 79-99 行
- `routes/case_bp.py`: 102-123 行
- `routes/user_management_bp.py`: 47-66 行

**重复代码**:
```python
session['user_id'] = user_info['id']
session['username'] = user_info['username']
session['display_name'] = user_info.get('display_name', '')
session['role'] = user_info['role']
session['login_time'] = datetime.now().isoformat()
session['force_password_change'] = force_password_change
session['redirect_after_password_change'] = redirect_url

# 密码强度检查
from common.validators import check_password_strength
is_strong, strength_msg = check_password_strength(password)
session['password_strength_warning'] = None if is_strong else strength_msg
```

**优化方案**:

#### 2.1 在 `common/unified_auth.py` 添加统一函数

```python
from datetime import datetime
from flask import session
from typing import Optional, Dict
from common.logger import logger

def set_user_session(
    user_info: Dict,
    password: Optional[str] = None,
    force_password_change: bool = False,
    redirect_after_change: Optional[str] = None,
    check_strength: bool = True
) -> None:
    """统一设置用户 Session

    Args:
        user_info: 用户信息字典，包含 id, username, display_name, role 等
        password: 用户密码（用于复杂度检查）
        force_password_change: 是否强制修改密码
        redirect_after_change: 修改密码后跳转地址
        check_strength: 是否检查密码复杂度
    """
    # 基础 Session 信息
    session['user_id'] = user_info['id']
    session['username'] = user_info['username']
    session['display_name'] = user_info.get('display_name', '')
    session['role'] = user_info['role']
    session['login_time'] = datetime.now().isoformat()
    session['force_password_change'] = force_password_change

    # 记录来源系统（用于修改密码后跳转）
    if redirect_after_change:
        session['redirect_after_password_change'] = redirect_after_change

    # 密码强度检查（不阻止登录，仅提示）
    if check_strength and password:
        try:
            from common.validators import check_password_strength
            is_strong, strength_msg = check_password_strength(password)
            session['password_strength_warning'] = None if is_strong else strength_msg

            if not is_strong:
                logger.info(f"用户 {user_info['username']} 密码复杂度不足: {strength_msg}")
        except Exception as e:
            logger.error(f"密码强度检查失败: {str(e)}")
```

#### 2.2 修改知识库登录

**修改文件**: `routes/kb_bp.py`

**原代码** (79-99 行):
```python
# 设置session
session['user_id'] = user_info['id']
session['username'] = user_info['username']
session['display_name'] = user_info.get('display_name', '')
session['role'] = user_info['role']
session['login_time'] = datetime.now().isoformat()
session['force_password_change'] = user_info.get('force_password_change', False)

# 记录来源系统（用于修改密码后跳转）
session['redirect_after_password_change'] = '/kb/'

# 检查密码复杂度（不阻止登录，仅记录）
from common.validators import check_password_strength
is_strong, strength_msg = check_password_strength(password)
session['password_strength_warning'] = None if is_strong else strength_msg
```

**新代码**:
```python
# 导入统一函数
from common.unified_auth import set_user_session

# 统一设置 Session
set_user_session(
    user_info=user_info,
    password=password,
    force_password_change=user_info.get('force_password_change', False),
    redirect_after_change='/kb/',
    check_strength=True
)
```

#### 2.3 修改工单系统登录

**修改文件**: `routes/case_bp.py`

**原代码** (102-123 行):
```python
# 设置session
session['user_id'] = user_info['id']
session['username'] = user_info['username']
session['display_name'] = user_info.get('display_name', '')
session['role'] = user_info['role']
session['login_time'] = datetime.now().isoformat()
session['force_password_change'] = user_info.get('force_password_change', False)

# 记录来源系统（用于修改密码后跳转）
session['redirect_after_password_change'] = '/case/'

# 检查密码复杂度（不阻止登录，仅记录）
from common.validators import check_password_strength
is_strong, strength_msg = check_password_strength(password)
session['password_strength_warning'] = None if is_strong else strength_msg
```

**新代码**:
```python
from common.unified_auth import set_user_session

set_user_session(
    user_info=user_info,
    password=password,
    force_password_change=user_info.get('force_password_change', False),
    redirect_after_change='/case/',
    check_strength=True
)
```

#### 2.4 修改用户管理登录

**修改文件**: `routes/user_management_bp.py`

**原代码** (47-66 行):
```python
# 设置session
session['user_id'] = user_info['id']
session['username'] = user_info['username']
session['display_name'] = user_info.get('display_name', '')
session['role'] = user_info['role']
session['login_time'] = datetime.now().isoformat()
session['force_password_change'] = user_info.get('force_password_change', False)

# 记录来源系统（用于修改密码后跳转）
session['redirect_after_password_change'] = '/user-mgmt/'
```

**新代码**:
```python
from common.unified_auth import set_user_session

set_user_session(
    user_info=user_info,
    force_password_change=user_info.get('force_password_change', False),
    redirect_after_change='/user-mgmt/',
    check_strength=False  # 用户管理不需要检查密码
)
```

**涉及文件**:
- `common/unified_auth.py` - 添加 `set_user_session()` 函数
- `routes/kb_bp.py` - 替换重复代码
- `routes/case_bp.py` - 替换重复代码
- `routes/user_management_bp.py` - 替换重复代码

**预计工作量**: 4 小时

**验收标准**:
- ✅ 三个系统的登录功能正常工作
- ✅ 密码复杂度提示正常显示
- ✅ 修改密码后正确跳转
- ✅ 减少约 60 行重复代码

---

### 3. 重新启用 CSRF 保护

**问题描述**: 所有蓝图都被豁免 CSRF 保护，存在 CSRF 攻击风险

**当前状态** (`app.py` 256-262 行):
```python
# 豁免所有蓝图的 CSRF 保护（临时措施）
csrf.exempt(kb_bp)
csrf.exempt(kb_management_bp)
csrf.exempt(case_bp)
csrf.exempt(auth_bp)
csrf.exempt(user_management_bp)
csrf.exempt(home_bp)
```

**安全风险**:
- 攻击者可以构造恶意页面，诱导用户执行操作
- 可能导致数据泄露、篡改、删除

**优化方案**:

#### 3.1 步骤 1：移除全局豁免

**修改文件**: `app.py`

```python
# 删除或注释以下代码
# csrf.exempt(kb_bp)
# csrf.exempt(kb_management_bp)
# csrf.exempt(case_bp)
# csrf.exempt(auth_bp)
# csrf.exempt(user_management_bp)
# csrf.exempt(home_bp)
```

#### 3.2 步骤 2：豁免公开接口

**修改文件**: `routes/kb_bp.py`

```python
@kb_bp.route('/auth/login', methods=['GET', 'POST'])
@csrf.exempt  # 仅豁免登录接口
def login():
    """知识库登录"""
    ...
```

**修改文件**: `routes/case_bp.py`

```python
@case_bp.route('/login', methods=['GET', 'POST'])
@csrf.exempt  # 仅豁免登录接口
def login():
    """工单系统登录"""
    ...
```

**修改文件**: `routes/user_management_bp.py`

```python
@user_management_bp.route('/login', methods=['GET', 'POST'])
@csrf.exempt  # 仅豁免登录接口
def login():
    """用户管理登录"""
    ...
```

#### 3.3 步骤 3：在表单中添加 CSRF Token

**修改文件**: 所有包含 POST 表单的模板

**示例**: `templates/kb/change_password.html`

```html
<form method="POST" action="{{ url_for('kb.change_password') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>

    <div class="mb-3">
        <label for="old_password">当前密码</label>
        <input type="password" class="form-control" id="old_password" name="old_password" required>
    </div>

    <div class="mb-3">
        <label for="new_password">新密码</label>
        <input type="password" class="form-control" id="new_password" name="new_password" required>
    </div>

    <button type="submit" class="btn btn-primary">修改密码</button>
</form>
```

**需要添加 CSRF Token 的表单**:
- `templates/kb/change_password.html`
- `templates/case/submit_ticket.html`
- `templates/user_management/change_password.html`
- 所有包含 POST 表单的页面

#### 3.4 步骤 4：在 AJAX 请求中添加 CSRF Token

**修改文件**: 所有包含 AJAX 请求的 JavaScript 文件

**方法 1**: 在全局 AJAX 设置中添加 CSRF Token

```javascript
// 在所有页面加载时执行
$(document).ready(function() {
    // 获取 CSRF Token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // 为所有 AJAX 请求添加 CSRF Token
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': getCookie('csrf_token')
        }
    });
});
```

**方法 2**: 为每个请求手动添加

```javascript
$.ajax({
    url: '/api/endpoint',
    type: 'POST',
    headers: {
        'X-CSRFToken': '{{ csrf_token() }}'
    },
    data: {...},
    success: function(response) {
        ...
    }
});
```

**需要添加 CSRF Token 的 AJAX 请求**:
- `templates/kb/index.html` - Trilium 搜索
- `templates/kb/management.html` - 批量操作
- `templates/case/ticket_detail.html` - 工单操作
- `templates/case/submit_ticket.html` - 提交工单

#### 3.5 步骤 5：测试验证

```bash
# 启动应用
python app.py

# 测试登录（应该正常工作，因为已豁免）
# 访问 http://localhost:5000/kb/auth/login

# 测试表单提交
# 尝试修改密码、提交工单等操作

# 测试 AJAX 请求
# 使用浏览器控制台检查 CSRF Token 是否正确发送
```

**验证要点**:
- ✅ 登录功能正常（已豁免）
- ✅ 表单提交需要 CSRF Token
- ✅ AJAX 请求包含 CSRF Token
- ✅ 没有 CSRF Token 时返回 400 错误
- ✅ 无 CSRF Token 时无法执行敏感操作

**涉及文件**:
- `app.py` - 移除全局豁免
- `routes/kb_bp.py` - 豁免登录接口
- `routes/case_bp.py` - 豁免登录接口
- `routes/user_management_bp.py` - 豁免登录接口
- 所有包含 POST 表单的模板 - 添加 CSRF Token
- 所有包含 AJAX 请求的模板 - 添加 CSRF Token

**预计工作量**: 6 小时

**验收标准**:
- ✅ 登录功能正常工作
- ✅ 表单提交需要 CSRF Token
- ✅ AJAX 请求包含 CSRF Token
- ✅ CSRF 攻击被防护

---

### 4. 提取用户状态检查逻辑

**问题描述**: 用户状态检查逻辑在知识库和工单系统中重复

**重复位置**:
- `routes/kb_bp.py`: 262-297 行
- `routes/case_bp.py`: 185-220 行

**重复代码**:
```python
# 验证session中的用户是否在数据库中仍然有效
user_id = session.get('user_id')
if user_id:
    # 使用缓存减少数据库查询
    cache_key = f'user_status_{user_id}'
    cache_time, cached_status = _user_status_cache.get(cache_key, (None, None))

    if cache_time and (datetime.now() - cache_time) < timedelta(minutes=5):
        if cached_status not in ['active']:
            logger.warning(f"用户状态缓存异常: {cached_status}, 清除session, user_id: {user_id}")
            session.clear()
            return unauthorized_response(message='账户已被禁用，请重新登录')
    else:
        from common.unified_auth import get_connection
        conn = get_connection('kb')
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT status FROM `users` WHERE id = %s", (user_id,))
                    result = cursor.fetchone()
                    if result:
                        user_status = result[0] if isinstance(result, tuple) else result.get('status')
                        _user_status_cache[cache_key] = (datetime.now(), user_status)

                        if user_status not in ['active']:
                            logger.warning(f"用户session中的用户状态异常: {user_status}, 清除session, user_id: {user_id}")
                            session.clear()
                            return unauthorized_response(message='账户已被禁用，请重新登录')
            except Exception as e:
                logger.error(f"验证用户状态失败: {str(e)}")
            finally:
                conn.close()
```

**优化方案**:

#### 4.1 在 `common/unified_auth.py` 添加检查函数

```python
from datetime import datetime, timedelta
from flask import session, jsonify
from typing import Optional, Tuple, Dict
from common.logger import logger

# 用户状态缓存（模块级全局变量）
_user_status_cache = {}

def check_user_status(
    cache_duration_minutes: int = 5,
    clear_session_on_inactive: bool = True
) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """检查用户 Session 和数据库状态是否一致

    Args:
        cache_duration_minutes: 缓存持续时间（分钟）
        clear_session_on_inactive: 用户状态异常时是否清除 Session

    Returns:
        (is_valid, user_info, error_message)
        is_valid: 用户状态是否有效
        user_info: 用户信息字典（如果有效）
        error_message: 错误消息（如果无效）
    """
    user_id = session.get('user_id')

    if not user_id:
        return False, None, '未登录'

    # 检查缓存
    cache_key = f'user_status_{user_id}'
    cache_time, cached_status = _user_status_cache.get(cache_key, (None, None))

    if cache_time and (datetime.now() - cache_time) < timedelta(minutes=cache_duration_minutes):
        # 使用缓存状态
        if cached_status not in ['active']:
            logger.warning(f"用户状态缓存异常: {cached_status}, user_id: {user_id}")
            if clear_session_on_inactive:
                session.clear()
            return False, None, '账户已被禁用，请重新登录'
    else:
        # 查询数据库
        from common.unified_auth import get_connection
        conn = get_connection('kb')
        if not conn:
            logger.error("无法获取数据库连接")
            return False, None, '数据库连接失败'

        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, username, display_name, role, status FROM `users` WHERE id = %s", (user_id,))
                result = cursor.fetchone()

                if not result:
                    logger.warning(f"用户不存在于数据库，user_id: {user_id}")
                    if clear_session_on_inactive:
                        session.clear()
                    return False, None, '用户不存在，请重新登录'

                user_status = result[4] if isinstance(result, tuple) else result.get('status')

                # 更新缓存
                _user_status_cache[cache_key] = (datetime.now(), user_status)

                # 检查用户状态
                if user_status not in ['active']:
                    logger.warning(f"用户状态异常: {user_status}, user_id: {user_id}")
                    if clear_session_on_inactive:
                        session.clear()
                    return False, None, '账户已被禁用，请重新登录'

                # 返回用户信息
                user_info = {
                    'id': result[0] if isinstance(result, tuple) else result.get('id'),
                    'username': result[1] if isinstance(result, tuple) else result.get('username'),
                    'display_name': result[2] if isinstance(result, tuple) else result.get('display_name'),
                    'role': result[3] if isinstance(result, tuple) else result.get('role')
                }
                return True, user_info, None

        except Exception as e:
            logger.error(f"验证用户状态失败: {str(e)}")
            return False, None, '验证失败，请重新登录'
        finally:
            conn.close()

    return False, None, '未知错误'
```

#### 4.2 修改知识库 check_login

**修改文件**: `routes/kb_bp.py`

```python
@kb_bp.route('/auth/check-login')
def check_login():
    """检查登录状态"""
    from common.unified_auth import check_user_status, get_current_user

    # 使用统一的用户状态检查
    is_valid, user_info, error_msg = check_user_status()

    if not is_valid:
        return unauthorized_response(message=error_msg)

    # 获取当前用户完整信息
    user = get_current_user()
    if user:
        from common.response import success_response
        return success_response(data={'user': user}, message='已登录')

    return unauthorized_response(message='未登录')
```

#### 4.3 修改工单系统 check_login

**修改文件**: `routes/case_bp.py`

```python
@case_bp.route('/api/check-login')
def check_login():
    """检查登录状态"""
    from common.unified_auth import check_user_status, get_current_user

    # 使用统一的用户状态检查
    is_valid, user_info, error_msg = check_user_status()

    if not is_valid:
        return unauthorized_response(message=error_msg)

    # 获取当前用户完整信息
    user = get_current_user()
    if user:
        return success_response(data={'user': user}, message='已登录')

    return unauthorized_response(message='未登录')
```

#### 4.4 移除重复的缓存变量

**修改文件**: `routes/kb_bp.py` 和 `routes/case_bp.py`

```python
# 删除以下行
# _user_status_cache = {}
```

**涉及文件**:
- `common/unified_auth.py` - 添加 `check_user_status()` 函数和全局缓存
- `routes/kb_bp.py` - 使用统一函数，移除重复代码和缓存变量
- `routes/case_bp.py` - 使用统一函数，移除重复代码和缓存变量

**预计工作量**: 2 小时

**验收标准**:
- ✅ 用户状态检查功能正常
- ✅ 缓存机制正常工作
- ✅ 减少约 60 行重复代码
- ✅ 用户被锁定后立即清除 Session

---

## 🟡 中优先级优化（近期处理）

### 5. 优化统计查询（7次→1次）

**问题描述**: 用户统计接口执行 7 次独立的 COUNT 查询

**当前代码** (`routes/unified_bp.py` 285-314 行):
```python
# 执行7次独立的 COUNT 查询
cursor.execute("SELECT COUNT(*) as total FROM `users`")
total = cursor.fetchone()['total']

cursor.execute("SELECT COUNT(*) as count FROM `users` WHERE status = 'active'")
stats['users']['active'] = cursor.fetchone()['count']

cursor.execute("SELECT COUNT(*) as count FROM `users` WHERE role = 'admin'")
stats['users']['admins'] = cursor.fetchone()['count']

cursor.execute("SELECT COUNT(*) as count FROM `users` WHERE role = 'customer'")
stats['users']['customers'] = cursor.fetchone()['count']

cursor.execute("SELECT COUNT(*) as count FROM `users` WHERE role IN ('admin', 'user')")
stats['users']['kb_users'] = cursor.fetchone()['count']

cursor.execute("SELECT COUNT(*) as count FROM `users` WHERE login_count >= 5")
stats['users']['frequent_users'] = cursor.fetchone()['count']

cursor.execute("SELECT COUNT(*) as count FROM `users` WHERE DATE(created_at) = CURDATE()")
stats['users']['new_today'] = cursor.fetchone()['count']
```

**性能影响**:
- 7 次数据库查询
- 每次查询都有网络往返
- 统计页面加载较慢

**优化方案**:

#### 5.1 合并为一次查询

**修改文件**: `routes/unified_bp.py`

```python
@unified_bp.route('/api/stats', methods=['GET'])
@login_required
def get_user_stats():
    """获取用户统计信息"""
    try:
        log_request(logger, request)

        # 只允许管理员和用户角色查看
        user_role = session.get('role')
        if user_role not in ['admin', 'user']:
            return forbidden_response(message='权限不足')

        with db_connection('kb') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 使用一次查询获取所有统计数据
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(status = 'active') as active,
                    SUM(role = 'admin') as admins,
                    SUM(role = 'customer') as customers,
                    SUM(role IN ('admin', 'user')) as kb_users,
                    SUM(login_count >= 5) as frequent_users,
                    SUM(DATE(created_at) = CURDATE()) as new_today
                FROM `users`
            """)

            result = cursor.fetchone()

            stats = {
                'users': {
                    'total': int(result['total']),
                    'active': int(result['active'] or 0),
                    'admins': int(result['admins'] or 0),
                    'customers': int(result['customers'] or 0),
                    'kb_users': int(result['kb_users'] or 0),
                    'frequent_users': int(result['frequent_users'] or 0),
                    'new_today': int(result['new_today'] or 0)
                }
            }

        return success_response(data=stats, message='查询成功')

    except Exception as e:
        log_exception(logger, "查询用户统计失败")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return server_error_response(message=f'查询失败：{str(e)}')
```

**涉及文件**:
- `routes/unified_bp.py`

**预计工作量**: 3 小时

**验收标准**:
- ✅ 统计数据准确
- ✅ 查询次数从 7 次减少到 1 次
- ✅ 响应时间减少 50%+

---

### 6. 增强文件上传验证

**问题描述**: 当前仅验证文件扩展名，未验证文件内容

**当前代码** (`routes/case_bp.py` 511-514 行):
```python
def allowed_file(filename):
    allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
```

**安全风险**:
- 攻击者可以修改文件扩展名绕过验证
- 未检查文件内容类型
- 未限制文件大小

**优化方案**:

#### 6.1 创建文件验证模块

**创建文件**: `common/file_validator.py`

```python
import os
import magic
from typing import Tuple
from werkzeug.utils import secure_filename

# 允许的 MIME 类型
ALLOWED_MIME_TYPES = {
    'text/plain': ['txt'],
    'application/pdf': ['pdf'],
    'image/jpeg': ['jpg', 'jpeg'],
    'image/png': ['png'],
    'image/gif': ['gif'],
    'application/msword': ['doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['docx'],
    'application/vnd.ms-excel': ['xls'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['xlsx'],
}

# 最大文件大小（10MB）
MAX_FILE_SIZE = 10 * 1024 * 1024

def validate_file_upload(file) -> Tuple[bool, str]:
    """验证上传的文件

    Args:
        file: Flask FileStorage 对象

    Returns:
        (is_valid, error_message)
        is_valid: 文件是否有效
        error_message: 错误消息（如果无效）
    """
    if not file:
        return False, "未选择文件"

    filename = secure_filename(file.filename)
    if not filename:
        return False, "文件名无效"

    # 检查文件大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size == 0:
        return False, "文件为空"

    if file_size > MAX_FILE_SIZE:
        size_mb = MAX_FILE_SIZE // 1024 // 1024
        return False, f"文件大小超过限制（最大 {size_mb}MB）"

    # 检查扩展名
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    # 检查文件类型（通过魔数）
    try:
        file_content = file.read(2048)
        file.seek(0)

        mime_type = magic.from_buffer(file_content, mime=True)

        if mime_type not in ALLOWED_MIME_TYPES:
            return False, f"不支持的文件类型: {mime_type}"

        if ext not in ALLOWED_MIME_TYPES[mime_type]:
            return False, f"文件扩展名与内容不匹配"

    except Exception as e:
        return False, f"文件验证失败: {str(e)}"

    return True, ""

def get_safe_filename(filename: str) -> str:
    """获取安全的文件名

    Args:
        filename: 原始文件名

    Returns:
        安全的文件名
    """
    # 使用 werkzeug 的 secure_filename
    safe_name = secure_filename(filename)

    # 如果文件名被完全过滤，使用时间戳
    if not safe_name or safe_name in ('.', '..'):
        import time
        safe_name = f"file_{int(time.time())}"

    return safe_name
```

#### 6.2 安装依赖

```bash
pip install python-magic
```

**Windows 系统需要额外安装**:
```bash
pip install python-magic-bin
```

#### 6.3 修改工单上传处理

**修改文件**: `routes/case_bp.py`

```python
from common.file_validator import validate_file_upload, get_safe_filename

@case_bp.route('/api/tickets/<int:ticket_id>/upload', methods=['POST'])
@login_required
def upload_attachment(ticket_id):
    """上传工单附件"""
    try:
        log_request(logger, request)

        # 检查工单权限
        user_id = session.get('user_id')
        with db_connection('casedb') as conn:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
            ticket = cursor.fetchone()

            if not ticket:
                return not_found_response(message='工单不存在')

            # 检查权限
            user_role = session.get('role')
            if user_role == 'customer' and ticket['submit_user'] != user_id:
                return forbidden_response(message='无权限')

        # 验证文件
        if 'file' not in request.files:
            return error_response(message='未选择文件', code=400)

        file = request.files['file']

        # 使用增强的文件验证
        is_valid, error_msg = validate_file_upload(file)
        if not is_valid:
            return error_response(message=error_msg, code=400)

        # 获取安全的文件名
        filename = get_safe_filename(file.filename)

        # 保存文件
        upload_dir = os.path.join('uploads', 'tickets', str(ticket_id))
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # 保存到数据库
        file_size = os.path.getsize(file_path)
        with db_connection('casedb') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO attachments (ticket_id, filename, file_path, file_size, upload_time, uploaded_by)
                VALUES (%s, %s, %s, %s, NOW(), %s)
            """, (ticket_id, filename, file_path, file_size, user_id))
            conn.commit()

        return success_response(message='上传成功')

    except Exception as e:
        log_exception(logger, "上传附件失败")
        return server_error_response(message=f'上传失败：{str(e)}')
```

**涉及文件**:
- `common/file_validator.py` - 新建文件验证模块
- `routes/case_bp.py` - 使用新的文件验证
- `requirements.txt` - 添加 `python-magic` 依赖

**预计工作量**: 4 小时

**验收标准**:
- ✅ 文件类型通过 MIME 验证
- ✅ 文件扩展名与内容匹配
- ✅ 文件大小限制生效
- ✅ 无法上传恶意文件

---

### 7. 创建登录模板基类

**问题描述**: 三个系统的登录页面 HTML 重复，仅背景色不同

**重复内容**:
- HTML 头部结构
- CSS 样式
- JavaScript 库引用
- 登录表单布局

**优化方案**:

#### 7.1 创建通用登录基类

**创建文件**: `templates/common/login_base.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta charset="UTF-8">
    <title>{% block title %}登录 - 云户科技{% endblock %}</title>
    <link rel="icon" type="image/png" href="{{ url_for('static', filename='home/images/icon1.png') }}">
    <link href="https://cdn.bootcdn.net/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.bootcdn.net/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
        body {
            background: {% block bg_gradient %}linear-gradient(135deg, #0f4c81 0%, #1a5c9e 100%){% endblock %};
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
        }

        .login-container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            max-width: 450px;
            width: 100%;
            padding: 40px;
        }

        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }

        .login-header h2 {
            color: {% block header_color %}#0f4c81{% endblock %};
            margin-bottom: 10px;
            font-weight: 700;
        }

        .login-header p {
            color: #666;
            font-size: 14px;
        }

        .form-control {
            border-radius: 8px;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            transition: all 0.3s;
        }

        .form-control:focus {
            border-color: {% block focus_color %}#0f4c81{% endblock %};
            box-shadow: 0 0 0 0.2rem rgba(15, 76, 129, 0.1);
        }

        .btn-primary {
            background: {% block btn_color %}#0f4c81{% endblock %};
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s;
        }

        .btn-primary:hover {
            background: {% block btn_hover_color %}#0a3d6a{% endblock %};
        }

        .alert {
            border-radius: 8px;
            border: none;
        }

        .alert-danger {
            background: #fee;
            color: #c33;
        }

        .alert-info {
            background: #e3f2fd;
            color: #1565c0;
        }

        .password-toggle {
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            cursor: pointer;
            color: #666;
            background: none;
            border: none;
            padding: 0;
        }

        .password-toggle:hover {
            color: #333;
        }

        .password-container {
            position: relative;
        }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <div class="login-container">
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.bootcdn.net/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
    <script>
        // 密码显示/隐藏切换
        function togglePassword(inputId) {
            const input = document.getElementById(inputId);
            const toggle = event.target;
            const icon = toggle.querySelector('i');

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');

                // 3秒后自动隐藏
                setTimeout(() => {
                    input.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }, 3000);
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        }

        // 表单提交前验证
        function validateForm(formId) {
            const form = document.getElementById(formId);
            const inputs = form.querySelectorAll('input[required]');

            for (const input of inputs) {
                if (!input.value.trim()) {
                    input.focus();
                    return false;
                }
            }

            return true;
        }
    </script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

#### 7.2 修改知识库登录

**修改文件**: `templates/kb/login.html`

```html
{% extends "common/login_base.html" %}

{% block title %}云户知识库 - 登录{% endblock %}

{% block bg_gradient %}linear-gradient(135deg, #0f4c81 0%, #1a5c9e 100%){% endblock %}
{% block header_color %}#0f4c81{% endblock %}
{% block focus_color %}#0f4c81{% endblock %}
{% block btn_color %}#0f4c81{% endblock %}
{% block btn_hover_color %}#0a3d6a{% endblock %}

{% block content %}
<div class="login-header">
    <h2>云户知识库</h2>
    <p>欢迎回来，请登录您的账户</p>
</div>

{% if error %}
<div class="alert alert-danger mb-3" role="alert">
    <i class="fas fa-exclamation-circle me-2"></i>
    {{ error }}
</div>
{% endif %}

{% if success %}
<div class="alert alert-info mb-3" role="alert">
    <i class="fas fa-check-circle me-2"></i>
    {{ success }}
</div>
{% endif %}

<form method="POST" autocomplete="off" onsubmit="return validateForm('loginForm')">
    <div class="mb-3">
        <label for="username" class="form-label">用户名或邮箱</label>
        <input type="text" class="form-control" id="username" name="username"
               placeholder="请输入用户名" required autocomplete="username" autofocus>
    </div>

    <div class="mb-3">
        <label for="password" class="form-label">密码</label>
        <div class="password-container">
            <input type="password" class="form-control" id="password" name="password"
                   placeholder="请输入密码" required autocomplete="current-password">
            <button type="button" class="password-toggle" onclick="togglePassword('password')">
                <i class="fas fa-eye"></i>
            </button>
        </div>
    </div>

    <button type="submit" class="btn btn-primary">登录</button>
</form>
{% endblock %}
```

#### 7.3 修改工单登录

**修改文件**: `templates/case/login.html`

```html
{% extends "common/login_base.html" %}

{% block title %}云户工单 - 登录{% endblock %}

{% block bg_gradient %}linear-gradient(135deg, #10b981 0%, #059669 100%){% endblock %}
{% block header_color %}#10b981{% endblock %}
{% block focus_color %}#10b981{% endblock %}
{% block btn_color %}#10b981{% endblock %}
{% block btn_hover_color %}#059669{% endblock %}

{% block content %}
<div class="login-header">
    <h2>云户工单系统</h2>
    <p>欢迎回来，请登录您的账户</p>
</div>

{% if error %}
<div class="alert alert-danger mb-3" role="alert">
    <i class="fas fa-exclamation-circle me-2"></i>
    {{ error }}
</div>
{% endif %}

<form method="POST" autocomplete="off" onsubmit="return validateForm('loginForm')">
    <div class="mb-3">
        <label for="username" class="form-label">用户名或邮箱</label>
        <input type="text" class="form-control" id="username" name="username"
               placeholder="请输入用户名" required autocomplete="username" autofocus>
    </div>

    <div class="mb-3">
        <label for="password" class="form-label">密码</label>
        <div class="password-container">
            <input type="password" class="form-control" id="password" name="password"
                   placeholder="请输入密码" required autocomplete="current-password">
            <button type="button" class="password-toggle" onclick="togglePassword('password')">
                <i class="fas fa-eye"></i>
            </button>
        </div>
    </div>

    <button type="submit" class="btn btn-primary">登录</button>
</form>
{% endblock %}
```

#### 7.4 修改用户管理登录

**修改文件**: `templates/user_management/login.html`

类似地修改用户管理登录页面，使用紫色渐变主题。

**涉及文件**:
- `templates/common/login_base.html` - 新建登录基类
- `templates/kb/login.html` - 继承基类
- `templates/case/login.html` - 继承基类
- `templates/user_management/login.html` - 继承基类

**预计工作量**: 3 小时

**验收标准**:
- ✅ 所有登录页面外观一致
- ✅ 仅背景色和主题色不同
- ✅ 减少 500+ 行重复 HTML
- ✅ 维护更加方便

---

### 8. 增加数据库索引

**问题描述**: 缺少必要的索引，查询性能不佳

**当前索引**:
```sql
-- 仅部分表有索引
CREATE INDEX idx_username ON users(username);
CREATE INDEX idx_company_name ON users(company_name);
```

**优化方案**:

#### 8.1 为 users 表添加索引

**创建文件**: `database/patches/v3.2_to_v3.3/add_indexes_users.sql`

```sql
-- users 表索引优化

-- 用户名索引（已存在，确保唯一性）
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- 邮箱索引（已存在，确保唯一性）
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- 角色索引（用于权限检查）
CREATE INDEX idx_users_role ON users(role);

-- 状态索引（用于活跃用户查询）
CREATE INDEX idx_users_status ON users(status);

-- 创建时间索引（用于新用户统计）
CREATE INDEX idx_users_created_at ON users(created_at);

-- 复合索引（状态 + 角色，用于管理员查询）
CREATE INDEX idx_users_status_role ON users(status, role);
```

#### 8.2 为 tickets 表添加索引

**创建文件**: `database/patches/v3.2_to_v3.3/add_indexes_tickets.sql`

```sql
-- tickets 表索引优化

-- 提交用户索引（用于查询我的工单）
CREATE INDEX idx_tickets_submit_user ON tickets(submit_user);

-- 状态索引（用于工单列表筛选）
CREATE INDEX idx_tickets_status ON tickets(status);

-- 创建时间索引（用于工单排序和分页）
CREATE INDEX idx_tickets_create_time ON tickets(create_time);

-- 更新时间索引（用于工单更新统计）
CREATE INDEX idx_tickets_updated_at ON tickets(updated_at);

-- 复合索引（提交用户 + 状态，用于工单列表查询）
CREATE INDEX idx_tickets_user_status ON tickets(submit_user, status);

-- 复合索引（状态 + 创建时间，用于工单列表排序）
CREATE INDEX idx_tickets_status_time ON tickets(status, create_time DESC);
```

#### 8.3 为 mgmt_login_logs 表添加索引

**创建文件**: `database/patches/v3.2_to_v3.3/add_indexes_login_logs.sql`

```sql
-- mgmt_login_logs 表索引优化

-- 登录时间索引（用于登录历史查询）
CREATE INDEX idx_login_logs_time ON mgmt_login_logs(login_time);

-- 用户 ID 索引（用于用户登录历史）
CREATE INDEX idx_login_logs_user_id ON mgmt_login_logs(user_id);

-- 登录状态索引（用于成功/失败统计）
CREATE INDEX idx_login_logs_status ON mgmt_login_logs(status);

-- IP 地址索引（用于异常登录检测）
CREATE INDEX idx_login_logs_ip ON mgmt_login_logs(login_ip);

-- 复合索引（用户 ID + 登录时间，用于用户登录历史）
CREATE INDEX idx_login_logs_user_time ON mgmt_login_logs(user_id, login_time DESC);
```

#### 8.4 创建索引管理脚本

**创建文件**: `database/apply_indexes_v3.3.sql`

```sql
-- v3.2 到 v3.3 版本索引优化

-- 使用知识库数据库
USE YHKB;

-- 应用 users 表索引
SOURCE database/patches/v3.2_to_v3.3/add_indexes_users.sql;

-- 应用 mgmt_login_logs 表索引
SOURCE database/patches/v3.2_to_v3.3/add_indexes_login_logs.sql;

-- 使用工单数据库
USE casedb;

-- 应用 tickets 表索引
SOURCE database/patches/v3.2_to_v3.3/add_indexes_tickets.sql;

COMMIT;

-- 显示索引信息
SELECT
    TABLE_NAME,
    INDEX_NAME,
    COLUMN_NAME,
    SEQ_IN_INDEX
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA IN ('YHKB', 'casedb')
    AND TABLE_NAME IN ('users', 'mgmt_login_logs', 'tickets')
ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;
```

#### 8.5 应用索引

```bash
# Windows
mysql -u root -p < database/apply_indexes_v3.3.sql

# Linux/Mac
mysql -u root -p < database/apply_indexes_v3.3.sql
```

**涉及文件**:
- `database/patches/v3.2_to_v3.3/add_indexes_users.sql` - 新建
- `database/patches/v3.2_to_v3.3/add_indexes_tickets.sql` - 新建
- `database/patches/v3.2_to_v3.3/add_indexes_login_logs.sql` - 新建
- `database/apply_indexes_v3.3.sql` - 新建

**预计工作量**: 2 小时

**验收标准**:
- ✅ 索引创建成功
- ✅ 查询性能提升 30%+
- ✅ 无索引冲突或错误

---

### 9. 实现缓存机制（Redis）

**问题描述**: 缺少缓存机制，频繁查询数据库

**当前缓存**:
- 仅用户状态缓存（5分钟，内存缓存）
- 缓存容量有限，重启后丢失

**优化方案**:

#### 9.1 安装 Redis

**Windows**:
```bash
# 下载 Redis for Windows
# https://github.com/microsoftarchive/redis/releases

# 或使用 Docker
docker run -d -p 6379:6379 redis:latest
```

**Linux/Mac**:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# CentOS/RHEL
sudo yum install redis

# macOS
brew install redis
```

#### 9.2 安装 Python Redis 客户端

```bash
pip install redis
```

#### 9.3 更新配置文件

**修改文件**: `config.py`

```python
# Redis 配置
REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'False').lower() in ('true', '1', 'yes')
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# 缓存配置（秒）
CACHE_TTL_USER_STATUS = 300  # 5分钟
CACHE_TTL_USER_LIST = 600   # 10分钟
CACHE_TTL_STATS = 1800       # 30分钟
CACHE_TTL_KB_CONTENT = 3600  # 1小时
```

#### 9.4 创建缓存管理模块

**创建文件**: `common/cache_manager.py`

```python
import redis
import json
import pickle
from typing import Any, Optional
from common.logger import logger

class CacheManager:
    """缓存管理器"""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.client = None

        if self.enabled:
            try:
                from config import (
                    REDIS_HOST, REDIS_PORT, REDIS_DB,
                    REDIS_PASSWORD
                )
                self.client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    password=REDIS_PASSWORD,
                    decode_responses=False
                )
                # 测试连接
                self.client.ping()
                logger.info("Redis 连接成功")
            except Exception as e:
                logger.error(f"Redis 连接失败: {str(e)}")
                self.enabled = False

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.enabled or not self.client:
            return None

        try:
            data = self.client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            logger.error(f"缓存获取失败: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """设置缓存"""
        if not self.enabled or not self.client:
            return False

        try:
            data = pickle.dumps(value)
            self.client.setex(key, ttl, data)
            return True
        except Exception as e:
            logger.error(f"缓存设置失败: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.enabled or not self.client:
            return False

        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"缓存删除失败: {str(e)}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的缓存"""
        if not self.enabled or not self.client:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"批量删除缓存失败: {str(e)}")
            return 0

    def clear(self) -> bool:
        """清空所有缓存"""
        if not self.enabled or not self.client:
            return False

        try:
            self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: {str(e)}")
            return False

# 全局缓存管理器实例
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """获取缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        from config import REDIS_ENABLED
        _cache_manager = CacheManager(enabled=REDIS_ENABLED)
    return _cache_manager
```

#### 9.5 在用户状态检查中使用缓存

**修改文件**: `common/unified_auth.py`

```python
from common.cache_manager import get_cache_manager

def check_user_status(
    cache_duration_minutes: int = 5,
    clear_session_on_inactive: bool = True
) -> Tuple[bool, Optional[Dict], Optional[str]]:
    """检查用户 Session 和数据库状态是否一致"""
    user_id = session.get('user_id')

    if not user_id:
        return False, None, '未登录'

    # 使用 Redis 缓存
    cache = get_cache_manager()
    cache_key = f'user_status_{user_id}'
    cached_status = cache.get(cache_key)

    if cached_status:
        if cached_status not in ['active']:
            logger.warning(f"用户状态缓存异常: {cached_status}, user_id: {user_id}")
            if clear_session_on_inactive:
                session.clear()
            return False, None, '账户已被禁用，请重新登录'
    else:
        # 查询数据库
        conn = get_connection('kb')
        if not conn:
            logger.error("无法获取数据库连接")
            return False, None, '数据库连接失败'

        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, username, display_name, role, status FROM `users` WHERE id = %s", (user_id,))
                result = cursor.fetchone()

                if not result:
                    logger.warning(f"用户不存在于数据库，user_id: {user_id}")
                    if clear_session_on_inactive:
                        session.clear()
                    return False, None, '用户不存在，请重新登录'

                user_status = result[4] if isinstance(result, tuple) else result.get('status')

                # 缓存用户状态
                cache.set(cache_key, user_status, ttl=300)

                # 检查用户状态
                if user_status not in ['active']:
                    logger.warning(f"用户状态异常: {user_status}, user_id: {user_id}")
                    if clear_session_on_inactive:
                        session.clear()
                    return False, None, '账户已被禁用，请重新登录'

                # 返回用户信息
                user_info = {
                    'id': result[0] if isinstance(result, tuple) else result.get('id'),
                    'username': result[1] if isinstance(result, tuple) else result.get('username'),
                    'display_name': result[2] if isinstance(result, tuple) else result.get('display_name'),
                    'role': result[3] if isinstance(result, tuple) else result.get('role')
                }
                return True, user_info, None

        except Exception as e:
            logger.error(f"验证用户状态失败: {str(e)}")
            return False, None, '验证失败，请重新登录'
        finally:
            conn.close()

    return False, None, '未知错误'
```

#### 9.6 缓存失效策略

在用户信息变更时清除相关缓存：

```python
# 在用户更新、删除、状态变更时
def invalidate_user_cache(user_id: int):
    """清除用户相关缓存"""
    cache = get_cache_manager()
    cache.delete(f'user_status_{user_id}')
    cache.delete(f'user_info_{user_id}')
    cache.delete_pattern('user_list_*')
```

**涉及文件**:
- `config.py` - 添加 Redis 配置
- `common/cache_manager.py` - 新建缓存管理模块
- `common/unified_auth.py` - 使用 Redis 缓存
- `routes/unified_bp.py` - 缓存用户列表和统计
- `requirements.txt` - 添加 `redis` 依赖

**预计工作量**: 8 小时

**验收标准**:
- ✅ Redis 连接正常
- ✅ 缓存命中率 80%+
- ✅ 缓存失效正确
- ✅ 查询性能提升 60%+

---

### 10. 增加测试覆盖率

**问题描述**: 当前测试覆盖率不足，缺少业务逻辑测试

**当前测试**:
- `tests/test_case.py` - 部分工单测试
- `tests/test_home.py` - 部分官网测试
- `tests/test_kb.py` - 部分知识库测试

**缺失测试**:
- 业务逻辑层测试
- 异常场景测试
- 安全测试
- 性能测试

**优化方案**:

#### 10.1 安装测试工具

```bash
pip install pytest pytest-cov pytest-flask pytest-mock
```

#### 10.2 创建测试配置

**创建文件**: `tests/conftest.py`

```python
import pytest
from app import app
from flask import Flask

@pytest.fixture
def client():
    """测试客户端"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers():
    """认证头"""
    # 模拟登录获取 token
    return {'Authorization': 'Bearer test_token'}

@pytest.fixture
def mock_db_connection(monkeypatch):
    """模拟数据库连接"""
    # 模拟数据库连接
    pass
```

#### 10.3 创建认证测试

**创建文件**: `tests/test_auth.py`

```python
import pytest
from flask import session

def test_login_success(client):
    """测试登录成功"""
    response = client.post('/kb/auth/login', data={
        'username': 'admin',
        'password': 'YHKB@2024'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'知识库' in response.data

def test_login_invalid_credentials(client):
    """测试登录失败（错误密码）"""
    response = client.post('/kb/auth/login', data={
        'username': 'admin',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200
    assert b'用户名或密码错误' in response.data

def test_login_missing_fields(client):
    """测试登录失败（缺少字段）"""
    response = client.post('/kb/auth/login', data={
        'username': 'admin'
    })
    assert response.status_code == 200
    assert b'请输入' in response.data

def test_logout(client):
    """测试退出登录"""
    # 先登录
    client.post('/kb/auth/login', data={
        'username': 'admin',
        'password': 'YHKB@2024'
    })

    # 退出登录
    response = client.get('/kb/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'登录' in response.data

def test_session_reuse_after_locked(client):
    """测试用户被锁定后 Session 复用"""
    # 登录
    response = client.post('/kb/auth/login', data={
        'username': 'admin',
        'password': 'YHKB@2024'
    })
    assert response.status_code == 200

    # 锁定用户（模拟）
    # ...

    # 尝试访问需要认证的页面
    response = client.get('/kb/')
    assert response.status_code == 302  # 重定向到登录页
```

#### 10.4 创建 API 测试

**创建文件**: `tests/test_api.py`

```python
def test_create_ticket(client, auth_headers):
    """测试创建工单"""
    response = client.post('/case/api/tickets', 
        json={
            'title': '测试工单',
            'content': '测试内容',
            'priority': 'high'
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json['success'] == True

def test_get_tickets(client, auth_headers):
    """测试获取工单列表"""
    response = client.get('/case/api/tickets', headers=auth_headers)
    assert response.status_code == 200
    assert 'data' in response.json

def test_unauthorized_access(client):
    """测试未授权访问"""
    response = client.get('/case/api/tickets')
    assert response.status_code == 401
```

#### 10.5 创建业务逻辑测试

**创建文件**: `tests/test_user_service.py`

```python
from services.user_service import UserService
import pytest

def test_create_user():
    """测试创建用户"""
    user = UserService.create_user(
        username='testuser',
        password='Test@123',
        email='test@example.com',
        role='user'
    )
    assert user is not None
    assert user['username'] == 'testuser'

def test_duplicate_username():
    """测试重复用户名"""
    with pytest.raises(ValueError):
        UserService.create_user(
            username='admin',  # 已存在
            password='Test@123',
            email='test2@example.com',
            role='user'
        )

def test_weak_password():
    """测试弱密码"""
    with pytest.raises(ValueError):
        UserService.create_user(
            username='testuser',
            password='123',  # 太弱
            email='test@example.com',
            role='user'
        )
```

#### 10.6 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 生成覆盖率报告
pytest --cov=common --cov=routes --cov=services --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

**目标覆盖率**: 70%+

**涉及文件**:
- `tests/conftest.py` - 测试配置
- `tests/test_auth.py` - 认证测试
- `tests/test_api.py` - API 测试
- `tests/test_user_service.py` - 业务逻辑测试
- `requirements-dev.txt` - 添加测试依赖

**预计工作量**: 16 小时

**验收标准**:
- ✅ 测试覆盖率达到 70%+
- ✅ 所有核心功能有测试
- ✅ CI/CD 集成测试

---

## 🟢 低优先级优化（长期优化）

### 11. 统一用户管理 API

**问题描述**: 用户管理 API 分散在 `unified_bp` 和 `auth_bp` 中

**优化方案**:
- 将所有用户管理 API 统一到 `unified_bp`
- 明确功能边界：
  - `unified_bp`: 用户 CRUD、查询
  - `auth_bp`: 登录、注销、密码修改

---

### 12. 图片优化

**问题描述**: 部分图片未优化，占用带宽较大

**优化方案**:
- 使用 `scripts/optimize_images.py` 批量压缩
- 配置 `IMAGE_QUALITY=80`
- 启用 WebP 格式

---

### 13. CSS/JS 合并压缩

**问题描述**: 多个独立的 Bootstrap 文件，请求数过多

**优化方案**:
- 合并重复的 CSS/JS 文件
- 使用工具压缩（如 `cssmin`, `jsmin`）
- 减少请求数

---

## 📊 优化优先级矩阵

| 优化项 | 紧急性 | 重要性 | 工作量 | 优先级 |
|-------|-------|--------|--------|-------|
| 修复 JavaScript 语法错误 | 🔴 高 | 🔴 高 | 小 | 🔴 P0 |
| 提取重复的登录逻辑 | 🔴 高 | 🟡 中 | 小 | 🔴 P0 |
| 重新启用 CSRF 保护 | 🔴 高 | 🔴 高 | 中 | 🔴 P0 |
| 提取用户状态检查逻辑 | 🟡 中 | 🟡 中 | 小 | 🔴 P1 |
| 优化统计查询 | 🟡 中 | 🟡 中 | 小 | 🟡 P2 |
| 增强文件上传验证 | 🟡 中 | 🔴 高 | 中 | 🟡 P1 |
| 创建登录模板基类 | 🟡 中 | 🟢 低 | 中 | 🟡 P2 |
| 增加数据库索引 | 🟡 中 | 🟡 中 | 小 | 🟡 P2 |
| 实现缓存机制（Redis） | 🟢 低 | 🟡 中 | 大 | 🟡 P3 |
| 增加测试覆盖率 | 🟢 低 | 🟡 中 | 大 | 🟡 P3 |
| 统一用户管理 API | 🟢 低 | 🟢 低 | 中 | 🟢 P4 |
| 图片优化 | 🟢 低 | 🟢 低 | 小 | 🟢 P4 |
| CSS/JS 合并压缩 | 🟢 低 | 🟢 低 | 小 | 🟢 P4 |

---

## 🎯 实施计划

### 第一周（P0 优先级）
- ✅ 修复 JavaScript 语法错误
- ✅ 提取重复的登录逻辑
- ✅ 重新启用 CSRF 保护

### 第二周（P1 优先级）
- ✅ 提取用户状态检查逻辑
- ✅ 增强文件上传验证

### 第三周（P2 优先级）
- ✅ 优化统计查询
- ✅ 创建登录模板基类
- ✅ 增加数据库索引

### 第四周及以后（P3-P4 优先级）
- ✅ 实现缓存机制（Redis）
- ✅ 增加测试覆盖率
- ✅ 统一用户管理 API
- ✅ 图片优化
- ✅ CSS/JS 合并压缩

---

## 📈 预期收益

### 性能提升
- 查询性能提升 50%+（统计查询优化）
- 响应时间减少 60%+（缓存机制）
- 数据库负载降低 70%（缓存和索引）

### 代码质量
- 代码重复率降低 40%（提取公共逻辑）
- 代码可维护性提升 30%（统一架构）
- 测试覆盖率达到 70%（测试增强）

### 安全性
- CSRF 攻击防护（重新启用）
- 文件上传安全增强（内容验证）
- 安全漏洞减少 70%（全面加固）

### 开发效率
- 新功能开发速度提升 20%（代码复用）
- Bug 修复时间减少 30%（架构清晰）
- 团队协作效率提升 25%（规范统一）

---

## 📝 注意事项

### 测试要求
- 每个优化项完成后必须经过测试
- 确保不影响现有功能
- 性能优化需要基准测试对比

### 兼容性
- 数据库变更需要提供迁移脚本
- API 变更需要版本管理
- 前端变更需要向后兼容

### 文档更新
- 每次优化后更新相关文档
- 记录优化原因和效果
- 维护 CHANGELOG

---

**文档版本**: v1.0
**最后更新**: 2026-03-02
**维护者**: Development Team
