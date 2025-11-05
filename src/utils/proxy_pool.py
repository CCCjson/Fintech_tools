"""IP代理池管理模块"""
import random
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import threading
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.logger import logger
from src.utils.config import config


class ProxyPool:
    """IP代理池管理器"""

    def __init__(self):
        self.logger = logger
        self.proxies: List[Dict] = []
        self.failed_proxies: set = set()
        self.lock = threading.Lock()
        self.last_update = None
        self.update_interval = timedelta(hours=1)  # 每小时更新一次代理列表

    def add_proxy(self, proxy: str, proxy_type: str = 'http'):
        """
        添加代理到池中

        Args:
            proxy: 代理地址（格式：ip:port 或 user:pass@ip:port）
            proxy_type: 代理类型（http/https/socks5）
        """
        proxy_dict = {
            'proxy': proxy,
            'type': proxy_type,
            'fail_count': 0,
            'success_count': 0,
            'last_used': None,
            'avg_response_time': 0
        }

        with self.lock:
            # 检查是否已存在
            if not any(p['proxy'] == proxy for p in self.proxies):
                self.proxies.append(proxy_dict)
                self.logger.info(f"添加代理: {proxy}")

    def add_proxies_from_list(self, proxy_list: List[str], proxy_type: str = 'http'):
        """
        批量添加代理

        Args:
            proxy_list: 代理地址列表
            proxy_type: 代理类型
        """
        for proxy in proxy_list:
            self.add_proxy(proxy, proxy_type)

    def add_proxies_from_file(self, filepath: str, proxy_type: str = 'http'):
        """
        从文件读取代理列表

        Args:
            filepath: 文件路径（每行一个代理）
            proxy_type: 代理类型
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    proxy = line.strip()
                    if proxy and not proxy.startswith('#'):
                        self.add_proxy(proxy, proxy_type)

            self.logger.info(f"从文件 {filepath} 加载了代理列表")
        except Exception as e:
            self.logger.error(f"读取代理文件失败: {e}")

    def get_proxy(self, random_select: bool = True) -> Optional[Dict]:
        """
        获取一个可用代理

        Args:
            random_select: 是否随机选择（False则按成功率选择）

        Returns:
            代理字典或None
        """
        with self.lock:
            if not self.proxies:
                return None

            # 过滤掉失败次数过多的代理
            available_proxies = [
                p for p in self.proxies
                if p['proxy'] not in self.failed_proxies
                and p['fail_count'] < 5
            ]

            if not available_proxies:
                # 清空失败记录，重新开始
                self.failed_proxies.clear()
                for p in self.proxies:
                    p['fail_count'] = 0
                available_proxies = self.proxies

            if random_select:
                proxy = random.choice(available_proxies)
            else:
                # 按成功率排序
                available_proxies.sort(
                    key=lambda x: x['success_count'] / (x['fail_count'] + 1),
                    reverse=True
                )
                proxy = available_proxies[0]

            proxy['last_used'] = datetime.now()
            return proxy

    def get_proxy_dict(self, random_select: bool = True) -> Optional[Dict[str, str]]:
        """
        获取requests库使用的代理字典格式

        Args:
            random_select: 是否随机选择

        Returns:
            代理字典，格式：{'http': 'http://ip:port', 'https': 'http://ip:port'}
        """
        proxy_info = self.get_proxy(random_select)
        if not proxy_info:
            return None

        proxy_url = f"{proxy_info['type']}://{proxy_info['proxy']}"

        return {
            'http': proxy_url,
            'https': proxy_url
        }

    def mark_success(self, proxy: str, response_time: float = 0):
        """
        标记代理使用成功

        Args:
            proxy: 代理地址
            response_time: 响应时间（秒）
        """
        with self.lock:
            for p in self.proxies:
                if p['proxy'] == proxy:
                    p['success_count'] += 1

                    # 更新平均响应时间
                    if p['avg_response_time'] == 0:
                        p['avg_response_time'] = response_time
                    else:
                        p['avg_response_time'] = (
                            p['avg_response_time'] * 0.7 + response_time * 0.3
                        )

                    # 从失败列表中移除
                    if proxy in self.failed_proxies:
                        self.failed_proxies.remove(proxy)

                    break

    def mark_failure(self, proxy: str):
        """
        标记代理使用失败

        Args:
            proxy: 代理地址
        """
        with self.lock:
            for p in self.proxies:
                if p['proxy'] == proxy:
                    p['fail_count'] += 1

                    # 如果失败次数过多，加入失败列表
                    if p['fail_count'] >= 3:
                        self.failed_proxies.add(proxy)

                    break

    def remove_proxy(self, proxy: str):
        """
        从池中移除代理

        Args:
            proxy: 代理地址
        """
        with self.lock:
            self.proxies = [p for p in self.proxies if p['proxy'] != proxy]
            if proxy in self.failed_proxies:
                self.failed_proxies.remove(proxy)

            self.logger.info(f"移除代理: {proxy}")

    def test_proxy(self, proxy: str, test_url: str = 'http://www.baidu.com',
                   timeout: int = 5) -> bool:
        """
        测试代理是否可用

        Args:
            proxy: 代理地址
            test_url: 测试URL
            timeout: 超时时间

        Returns:
            是否可用
        """
        proxy_dict = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }

        try:
            response = requests.get(
                test_url,
                proxies=proxy_dict,
                timeout=timeout
            )

            if response.status_code == 200:
                self.mark_success(proxy, response.elapsed.total_seconds())
                return True
            else:
                self.mark_failure(proxy)
                return False

        except Exception as e:
            self.logger.debug(f"代理 {proxy} 测试失败: {e}")
            self.mark_failure(proxy)
            return False

    def test_all_proxies(self, test_url: str = 'http://www.baidu.com'):
        """
        测试所有代理

        Args:
            test_url: 测试URL
        """
        self.logger.info(f"开始测试 {len(self.proxies)} 个代理")

        working_count = 0
        for proxy_info in self.proxies:
            if self.test_proxy(proxy_info['proxy'], test_url):
                working_count += 1

        self.logger.info(f"代理测试完成，可用: {working_count}/{len(self.proxies)}")

    def get_stats(self) -> Dict:
        """
        获取代理池统计信息

        Returns:
            统计信息字典
        """
        with self.lock:
            total = len(self.proxies)
            failed = len(self.failed_proxies)
            available = total - failed

            return {
                'total': total,
                'available': available,
                'failed': failed,
                'proxies': [
                    {
                        'proxy': p['proxy'],
                        'success': p['success_count'],
                        'fail': p['fail_count'],
                        'avg_time': round(p['avg_response_time'], 2)
                    }
                    for p in sorted(
                        self.proxies,
                        key=lambda x: x['success_count'] / (x['fail_count'] + 1),
                        reverse=True
                    )[:10]  # 只返回前10个最好的
                ]
            }

    def clear(self):
        """清空代理池"""
        with self.lock:
            self.proxies.clear()
            self.failed_proxies.clear()
            self.logger.info("代理池已清空")


# 全局代理池实例
proxy_pool = ProxyPool()


def init_proxy_pool_from_config():
    """从配置文件初始化代理池"""
    proxy_file = config.get('crawler.proxy_file', None)

    if proxy_file:
        proxy_pool.add_proxies_from_file(proxy_file)
    else:
        # 可以添加一些免费代理作为示例（实际使用需要自己维护代理列表）
        logger.info("未配置代理文件，代理池为空")


# 初始化代理池
# init_proxy_pool_from_config()
