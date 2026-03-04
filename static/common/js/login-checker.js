/**
 * 通用登录检查模块
 * 用于防止退出登录后通过浏览器回退访问需要登录的页面
 */

(function() {
    'use strict';

    // 配置
    const CONFIG = {
        checkInterval: 10000,  // 每10秒检查一次（从5秒改为10秒，减少日志）
        debounceDelay: 3000,  // 防抖延迟3秒（从2秒改为3秒）
        checkOnVisibilityChange: true,  // 页面可见性改变时检查
        checkOnFocus: true,  // 页面获得焦点时检查
        loginUrl: '/user-mgmt/login',  // 默认登录页URL
        apiEndpoints: {
            kb: '/kb/auth/check-login',
            case: '/case/auth/check-login',
            userMgmt: '/user-mgmt/check-login'
        }
    };

    // 防抖控制
    let lastCheckTime = 0;
    let checkInProgress = false;

    // 当前系统类型
    const getCurrentSystem = function() {
        const path = window.location.pathname;
        if (path.startsWith('/user-mgmt')) {
            return 'userMgmt';
        } else if (path.startsWith('/case')) {
            return 'case';
        } else if (path.startsWith('/kb')) {
            return 'kb';
        }
        return null;
    };

    // 检查登录状态
    const checkLoginStatus = function(callback) {
        const system = getCurrentSystem();
        if (!system) {
            // 如果不是需要登录的系统，不检查
            if (callback) callback(false);
            return;
        }

        // 防抖检查：2秒内不重复请求
        const now = Date.now();
        if (now - lastCheckTime < CONFIG.debounceDelay && checkInProgress) {
            console.log('Login check skipped (debounce), last check was', now - lastCheckTime, 'ms ago');
            if (callback) callback(false); // 返回上一次的结果或默认值
            return;
        }

        // 如果正在检查中，等待前一次请求完成
        if (checkInProgress) {
            console.log('Login check already in progress, skipping');
            if (callback) callback(false);
            return;
        }

        lastCheckTime = now;
        checkInProgress = true;

        const checkUrl = CONFIG.apiEndpoints[system];

        $.ajax({
            url: checkUrl,
            method: 'GET',
            cache: false,  // 禁用缓存
            success: function(response) {
                checkInProgress = false;
                const isLoggedIn = response.success && response.data && response.data.user;
                const user = response.data ? response.data.user : null;

                if (callback) {
                    callback(isLoggedIn, user);
                }
            },
            error: function(xhr) {
                checkInProgress = false;
                console.error('Login status check failed:', xhr);
                // 检查失败时视为未登录
                if (callback) {
                    callback(false);
                }
            }
        });
    };

    // 处理未登录状态
    const handleNotLoggedIn = function() {
        const system = getCurrentSystem();
        let loginUrl = CONFIG.loginUrl;
        
        // 根据系统类型设置登录URL
        if (system === 'kb') {
            loginUrl = '/kb/auth/login';
        } else if (system === 'case') {
            loginUrl = '/case/auth/login';
        }
        
        console.log('User not logged in, redirecting to:', loginUrl);
        
        // 清除当前页面并跳转
        document.body.innerHTML = '<div style="display:flex;justify-content:center;align-items:center;height:100vh;background:#f5f5f5;"><h2 style="color:#666;">请先登录...</h2></div>';
        
        // 延迟跳转，给用户看到提示
        setTimeout(function() {
            window.location.href = loginUrl + '?next=' + encodeURIComponent(window.location.pathname);
        }, 500);
    };

    // 主检查函数
    const checkAndRedirect = function() {
        checkLoginStatus(function(isLoggedIn, user) {
            if (!isLoggedIn) {
                handleNotLoggedIn();
            } else {
                console.log('User is logged in:', user ? user.username : 'unknown');
            }
        });
    };

    // 初始化
    const init = function(options) {
        // 合并配置
        if (options) {
            Object.assign(CONFIG, options);
        }

        console.log('Login checker initialized for system:', getCurrentSystem());

        // 页面加载完成后立即检查
        $(document).ready(function() {
            // 短暂延迟确保AJAX库已加载
            setTimeout(checkAndRedirect, 100);
        });

        // 定期检查
        setInterval(checkAndRedirect, CONFIG.checkInterval);

        // 页面可见性改变时检查（防止从后台切换回来）
        if (CONFIG.checkOnVisibilityChange) {
            document.addEventListener('visibilitychange', function() {
                if (!document.hidden) {
                    console.log('Page became visible, checking login status');
                    checkAndRedirect();
                }
            });
        }

        // 页面获得焦点时检查（从其他标签页切换回来）
        if (CONFIG.checkOnFocus) {
            window.addEventListener('focus', function() {
                console.log('Page gained focus, checking login status');
                checkAndRedirect();
            });
        }

        // 监听浏览器后退/前进
        window.addEventListener('popstate', function() {
            console.log('Popstate event detected, checking login status');
            checkAndRedirect();
        });
    };

    // 导出到全局
    window.LoginChecker = {
        init: init,
        check: checkAndRedirect,
        checkStatus: checkLoginStatus,
        handleNotLoggedIn: handleNotLoggedIn
    };

    // 自动初始化（如果已加载jQuery）
    if (window.jQuery) {
        init();
    } else {
        // 等待jQuery加载后再初始化
        document.addEventListener('DOMContentLoaded', function() {
            if (window.jQuery) {
                init();
            }
        });
    }

})();
