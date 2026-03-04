# 静态资源说明

## 本地化的 JavaScript 库

为了解决 CDN 加载失败的问题，以下 JavaScript 库已下载到本地：

### Bootstrap 5.3.0
- **知识库模块**: `/static/kb/js/bootstrap.bundle.min.js`
- **工单系统模块**: `/static/case/js/bootstrap.bundle.min.js`

### 使用方式
在 HTML 模板中使用本地路径：
```html
<!-- 知识库模块 -->
<script src="/static/kb/js/bootstrap.bundle.min.js"></script>

<!-- 工单系统模块 -->
<script src="/static/case/js/bootstrap.bundle.min.js"></script>
```

## 更新说明
- **更新日期**: 2025-02-12
- **原因**: BootCDN 在某些网络环境下无法访问，导致页面功能失效
- **解决方案**: 将 Bootstrap JS 文件下载到本地，确保稳定访问

## 更新的模板文件

### 知识库模块 (kb)
- `templates/kb/management.html`
- `templates/kb/index.html`
- `templates/kb/login.html`
- `templates/kb/change_password.html`
- `templates/kb/user_management.html`

### 工单系统模块 (case)
- `templates/case/login.html`
- `templates/case/base.html`

## 文件大小
- Bootstrap 5.3.0 bundle.min.js: ~80KB
