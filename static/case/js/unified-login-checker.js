/**
 * 统一的登录状态检查脚本
 * 用于所有需要登录的页面
 */

(function() {
    'use strict';

    // 防抖控制
    const DEBOUNCE_DELAY = 3000; // 3秒内不重复请求（从2秒改为3秒）
    const CHECK_INTERVAL = 10000; // 每10秒检查一次（新增配置）
    let lastCheckTime = 0;
    let checkInProgress = false;

    // 检查登录状态
    function checkLoginStatus() {
        // 防抖检查：2秒内不重复请求
        const now = Date.now();
        if (now - lastCheckTime < DEBOUNCE_DELAY && checkInProgress) {
            console.log('Login check skipped (debounce), last check was', now - lastCheckTime, 'ms ago');
            return;
        }

        // 如果正在检查中，等待前一次请求完成
        if (checkInProgress) {
            console.log('Login check already in progress, skipping');
            return;
        }

        lastCheckTime = now;
        checkInProgress = true;

        $.ajax({
            url: '/case/auth/check-login',
            method: 'GET',
            cache: false,
            success: function(response) {
                checkInProgress = false;
                const isLoggedIn = response.success && response.data && response.data.user;

                if (!isLoggedIn) {
                    // 未登录，重定向到登录页面
                    console.log('User not logged in, redirecting to /case/');

                    // 显示加载提示
                    document.body.innerHTML = '<div style="display:flex;justify-content:center;align-items:center;height:100vh;background:#f5f5f5;"><h2 style="color:#666;">请先登录...</h2></div>';

                    // 跳转到登录页
                    setTimeout(function() {
                        window.location.href = '/case/?next=' + encodeURIComponent(window.location.pathname);
                    }, 500);
                } else {
                    console.log('User is logged in:', response.data.user.username);
                }
            },
            error: function(xhr) {
                checkInProgress = false;
                console.error('Login status check failed:', xhr);
                // 检查失败时视为未登录
                document.body.innerHTML = '<div style="display:flex;justify-content:center;align-items:center;height:100vh;background:#f5f5f5;"><h2 style="color:#666;">请先登录...</h2></div>';
                setTimeout(function() {
                    window.location.href = '/case/?next=' + encodeURIComponent(window.location.pathname);
                }, 500);
            }
        });
    }

    // 页面加载后立即检查
    $(document).ready(function() {
        console.log('Unified login checker initialized');

        // 短暂延迟确保一切准备就绪
        setTimeout(checkLoginStatus, 100);
    });

    // 定期检查登录状态（每10秒，从5秒改为10秒以减少日志）
    setInterval(checkLoginStatus, CHECK_INTERVAL);

    // 页面可见性改变时检查（从后台切换回来）
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            // 延迟检查，与防抖配合避免频繁请求
            setTimeout(function() {
                const now = Date.now();
                if (now - lastCheckTime >= DEBOUNCE_DELAY) {
                    console.log('Page became visible, checking login status');
                    checkLoginStatus();
                }
            }, 500);
        }
    });

    // 页面获得焦点时检查（从其他标签页切换回来）
    window.addEventListener('focus', function() {
        // 延迟检查，与防抖配合避免频繁请求
        setTimeout(function() {
            const now = Date.now();
            if (now - lastCheckTime >= DEBOUNCE_DELAY) {
                console.log('Page gained focus, checking login status');
                checkLoginStatus();
            }
        }, 500);
    });

    // 监听浏览器后退/前进按钮
    window.addEventListener('popstate', function() {
        console.log('Popstate event detected, checking login status');
        checkLoginStatus();
    });

    // 监听pageshow事件（处理缓存页面）
    window.addEventListener('pageshow', function(event) {
        // 如果是从缓存中恢复的页面
        if (event.persisted) {
            console.log('Page restored from cache, checking login status');
            checkLoginStatus();
        }
    });

})();
