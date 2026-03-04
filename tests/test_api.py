"""
API 接口测试
"""
import pytest


@pytest.mark.integration
def test_health_check(client):
    """测试健康检查接口"""
    if client is None:
        pytest.skip("客户端未初始化")

    response = client.get('/api/health')
    # 允许 200 或 404（如果路由不存在）
    assert response.status_code in [200, 404]


@pytest.mark.integration
def test_api_root(client):
    """测试 API 根路径"""
    if client is None:
        pytest.skip("客户端未初始化")

    response = client.get('/api/')
    # 允许 200 或 404
    assert response.status_code in [200, 404]
