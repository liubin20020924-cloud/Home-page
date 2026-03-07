"""
数据库索引优化脚本

功能：
1. 分析慢查询日志
2. 推荐索引
3. 自动创建索引
4. 性能对比测试
"""

import pymysql
import time
import logging
from datetime import datetime
from typing import List, Dict, Tuple

from common.database_context import get_db_connection


class DatabaseIndexOptimizer:
    """数据库索引优化器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recommendations = []
        self.performance_results = []

    def analyze_all_databases(self) -> Dict[str, List[str]]:
        """
        分析所有数据库

        Returns:
            数据库名 -> 推荐索引列表
        """
        databases = ['clouddoors_db', 'YHKB', 'casedb']
        results = {}

        for db_name in databases:
            try:
                results[db_name] = self.analyze_database(db_name)
            except Exception as e:
                self.logger.error(f"Error analyzing database {db_name}: {e}", exc_info=True)
                results[db_name] = []

        return results

    def analyze_database(self, db_name: str) -> List[str]:
        """
        分析单个数据库

        Args:
            db_name: 数据库名

        Returns:
            推荐索引列表
        """
        self.logger.info(f"Analyzing database: {db_name}")

        recommendations = []
        conn = get_db_connection(db_name)

        try:
            with conn.cursor() as cursor:
                # 获取所有表
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]

                self.logger.info(f"Found {len(tables)} tables in {db_name}")

                # 分析每个表
                for table in tables:
                    table_recommendations = self.analyze_table(cursor, table)
                    recommendations.extend(table_recommendations)

        finally:
            conn.close()

        return recommendations

    def analyze_table(self, cursor, table: str) -> List[str]:
        """
        分析表结构并推荐索引

        Args:
            cursor: 数据库游标
            table: 表名

        Returns:
            推荐索引列表
        """
        recommendations = []

        # 获取表结构
        cursor.execute(f"DESCRIBE `{table}`")
        columns = cursor.fetchall()

        # 获取现有索引
        cursor.execute(f"SHOW INDEX FROM `{table}`")
        existing_indexes = cursor.fetchall()

        existing_index_columns = set()
        for index in existing_indexes:
            if index[2] != 'PRIMARY':  # 跳过主键
                existing_index_columns.add(index[4])

        # 获取表行数
        cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
        row_count = cursor.fetchone()[0]

        if row_count < 1000:
            return recommendations  # 小表不需要索引

        # 分析列并推荐索引
        for col in columns:
            column_name = col[0]
            column_type = col[1]
            column_key = col[3]  # PRI, UNI, MUL, or empty

            # 跳过已有的索引列
            if column_name in existing_index_columns:
                continue

            # 跳过不适合索引的列
            if self._should_skip_index(column_name, column_type, row_count):
                continue

            # 推荐索引
            recommendation = f"ADD INDEX `idx_{column_name}` ON `{table}`(`{column_name}`)"
            recommendations.append(recommendation)
            self.logger.info(f"Recommendation for {table}: {recommendation}")

        return recommendations

    def _should_skip_index(self, column_name: str, column_type: str, row_count: int) -> bool:
        """
        判断是否应该跳过索引

        Args:
            column_name: 列名
            column_type: 列类型
            row_count: 表行数

        Returns:
            True 表示应该跳过
        """
        # 跳过不适合索引的列名
        skip_patterns = [
            'content', 'body', 'description', 'message', 'note',
            'html', 'markdown', 'text', 'data', 'value'
        ]
        if any(pattern in column_name.lower() for pattern in skip_patterns):
            return True

        # 跳过大文本列
        if 'text' in column_type.lower() or 'blob' in column_type.lower():
            return True

        return False

    def create_indexes(self, db_name: str, recommendations: List[str], dry_run: bool = True) -> List[Tuple[str, bool, str]]:
        """
        创建推荐的索引

        Args:
            db_name: 数据库名
            recommendations: 推荐的索引列表
            dry_run: 是否仅测试（不实际创建）

        Returns:
            (SQL, 成功, 错误消息) 列表
        """
        results = []
        conn = get_db_connection(db_name)

        try:
            with conn.cursor() as cursor:
                for sql in recommendations:
                    full_sql = f"ALTER TABLE {sql}"

                    try:
                        if dry_run:
                            self.logger.info(f"[DRY RUN] Would execute: {full_sql}")
                            results.append((full_sql, True, "Dry run"))
                        else:
                            start_time = time.time()
                            cursor.execute(full_sql)
                            execution_time = time.time() - start_time

                            conn.commit()
                            self.logger.info(f"Created index in {execution_time:.2f}s: {full_sql}")
                            results.append((full_sql, True, f"Created in {execution_time:.2f}s"))

                    except Exception as e:
                        error_msg = str(e)
                        self.logger.error(f"Failed to create index: {full_sql} - {error_msg}")
                        results.append((full_sql, False, error_msg))

        finally:
            conn.close()

        return results

    def test_query_performance(self, db_name: str, query: str, 
                             before_index: bool = True) -> float:
        """
        测试查询性能

        Args:
            db_name: 数据库名
            query: 测试查询
            before_index: 是否在创建索引前测试

        Returns:
            执行时间（秒）
        """
        conn = get_db_connection(db_name)

        try:
            with conn.cursor() as cursor:
                start_time = time.time()
                cursor.execute(f"EXPLAIN {query}")
                cursor.execute(query)
                cursor.fetchall()
                execution_time = time.time() - start_time

                self.logger.info(
                    f"Query {'before' if before_index else 'after'} index: "
                    f"{execution_time:.4f}s - {query[:100]}"
                )

                return execution_time

        finally:
            conn.close()

    def optimize_all(self, dry_run: bool = True):
        """
        优化所有数据库

        Args:
            dry_run: 是否仅测试
        """
        self.logger.info(f"Starting database optimization (dry_run={dry_run})")

        # 分析所有数据库
        results = self.analyze_all_databases()

        # 创建索引
        all_results = {}
        for db_name, recommendations in results.items():
            if recommendations:
                self.logger.info(f"Optimizing {db_name} with {len(recommendations)} recommendations")
                index_results = self.create_indexes(db_name, recommendations, dry_run)
                all_results[db_name] = index_results

        return all_results

    def generate_report(self, results: Dict[str, List[Tuple]]) -> str:
        """
        生成优化报告

        Args:
            results: 优化结果

        Returns:
            Markdown 格式的报告
        """
        report_lines = [
            "# 数据库索引优化报告",
            f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        ]

        for db_name, index_results in results.items():
            if not index_results:
                continue

            report_lines.append(f"## 数据库: {db_name}")
            report_lines.append(f"\n索引数量: {len(index_results)}\n")
            report_lines.append("| SQL | 状态 | 消息 |")
            report_lines.append("|-----|------|------|")

            for sql, success, message in index_results:
                status = "✅ 成功" if success else "❌ 失败"
                report_lines.append(f"| `{sql}` | {status} | {message} |")

            report_lines.append("")

        return "\n".join(report_lines)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='数据库索引优化工具')
    parser.add_argument('--dry-run', action='store_true', help='仅测试，不实际创建索引')
    parser.add_argument('--output', type=str, default='index_optimization_report.md',
                       help='输出报告文件路径')

    args = parser.parse_args()

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 创建优化器
    optimizer = DatabaseIndexOptimizer()

    # 执行优化
    if args.dry_run:
        print("🔍 运行模式：测试模式（不会实际创建索引）")
    else:
        print("⚠️  运行模式：实际创建索引")
        confirm = input("确认要创建索引吗？(yes/no): ")
        if confirm.lower() != 'yes':
            print("已取消")
            return

    results = optimizer.optimize_all(dry_run=args.dry_run)

    # 生成报告
    report = optimizer.generate_report(results)

    # 保存报告
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✅ 优化报告已保存到: {args.output}")
    print("\n" + report)


if __name__ == '__main__':
    main()
