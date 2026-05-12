#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
廉政意见智答系统 - 原型实现
功能：根据姓名和事项类型，自动检索违纪违规记录，判断影响期，生成标准化答复
"""

import pandas as pd
from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional, Tuple


class IntegrityAnswerSystem:
    """廉政意见智答系统核心类"""
    
    # Excel日期序列号转Python日期（1900年基准）
    @staticmethod
    def excel_date_to_python(excel_date) -> Optional[datetime]:
        """将Excel日期序列号转换为Python datetime对象"""
        if pd.isna(excel_date):
            return None
        
        # 处理字符串形式的序列号
        if isinstance(excel_date, str):
            # 清理可能的占位符如 "reserved-45760x1F"
            match = re.search(r'(\d+)', excel_date)
            if match:
                excel_date = int(match.group(1))
            else:
                return None
        
        if isinstance(excel_date, (int, float)):
            # Excel日期基准：1899-12-30（考虑1900闰年bug）
            base_date = datetime(1899, 12, 30)
            return base_date + timedelta(days=int(excel_date))
        
        # 如果已经是datetime，直接返回
        if isinstance(excel_date, datetime):
            return excel_date
        
        return None
    
    @staticmethod
    def format_date_chinese(dt: datetime) -> str:
        """格式化日期为中文格式：XXXX年XX月"""
        return dt.strftime("%Y年%m月")
    
    @staticmethod
    def format_date_standard(dt: datetime) -> str:
        """格式化日期为标准格式：YYYY-MM-DD"""
        return dt.strftime("%Y-%m-%d")
    
    def __init__(self, excel_path: str):
        """初始化系统，读取Excel数据"""
        self.excel_path = excel_path
        
        # 读取违纪信息表（跳过第一行标题）
        df_discipline_raw = pd.read_excel(excel_path, sheet_name='违纪信息', header=1)
        # 重命名列
        df_discipline_raw.columns = [
            '序号', '姓名', '处理机构', '年度', '分公司', '职务/职级', 
            '问责情况', '问责时间', '有无影响期', '影响期截止日期', '违纪事由', '录入人', '审核人'
        ]
        self.df_discipline = df_discipline_raw
        
        # 读取违规信息表
        df_violation_raw = pd.read_excel(excel_path, sheet_name='违规信息', header=1)
        df_violation_raw.columns = [
            '序号', '姓名', '处理机构', '年度', '分公司', '职务/职级',
            '问责类型', '问责时间', '有无影响期', '影响期截止日期', '事由', '录入人', '审核人'
        ]
        self.df_violation = df_violation_raw
        
        # 读取标准答复模板
        df_templates_raw = pd.read_excel(excel_path, sheet_name='标准答复', header=1)
        self.templates = {}
        for _, row in df_templates_raw.iterrows():
            category = row.iloc[0]
            content = row.iloc[1] if pd.notna(row.iloc[1]) else ""
            self.templates[category] = content
        
        # 解析干部选拔任用模板
        self.selection_templates = self._parse_selection_templates()
    
    def _parse_selection_templates(self) -> Dict[int, str]:
        """解析干部选拔任用的8个模板"""
        content = self.templates.get('干部选拔任用', '')
        templates = {}
        
        # 移除"答复模版："前缀
        content = re.sub(r'^答复模版：\s*', '', content)
        
        # 使用更简单的分割方式：按行分割并提取模板
        lines = content.strip().split('\n')
        for line in lines:
            match = re.match(r'^(\d+)．(.+)$', line.strip())
            if match:
                num = int(match.group(1))
                text = match.group(2).strip()
                templates[num] = text
        
        return templates
    
    def search_person(self, name: str) -> List[Dict]:
        """搜索指定人员的所有违纪违规记录"""
        records = []
        
        # 查询违纪信息
        discipline_mask = self.df_discipline['姓名'].astype(str).str.strip() == name.strip()
        for _, row in self.df_discipline[discipline_mask].iterrows():
            record = {
                '检索分类': '违纪情况',
                '姓名': row['姓名'],
                '处理机构': row['处理机构'],
                '问责情况': row['问责情况'],
                '问责时间_raw': row['问责时间'],
                '问责时间': self.format_date_standard(self.excel_date_to_python(row['问责时间'])),
                '有无影响期': row['有无影响期'],
                '影响期截止_raw': row['影响期截止日期'],
                '影响期截止日期': self.excel_date_to_python(row['影响期截止日期']),
                '事由': row['违纪事由']
            }
            records.append(record)
        
        # 查询违规信息
        violation_mask = self.df_violation['姓名'].astype(str).str.strip() == name.strip()
        for _, row in self.df_violation[violation_mask].iterrows():
            record = {
                '检索分类': '违规情况',
                '姓名': row['姓名'],
                '处理机构': row['处理机构'],
                '问责情况': row['问责类型'],
                '问责时间_raw': row['问责时间'],
                '问责时间': self.format_date_standard(self.excel_date_to_python(row['问责时间'])),
                '有无影响期': row['有无影响期'],
                '影响期截止_raw': row['影响期截止日期'],
                '影响期截止日期': self.excel_date_to_python(row['影响期截止日期']),
                '事由': row['事由']
            }
            records.append(record)
        
        # 按时间排序
        records.sort(key=lambda x: x['问责时间'] if x['问责时间'] else '9999-99-99')
        
        return records
    
    def check_influence_period(self, record: Dict, current_date: datetime = None) -> str:
        """判断记录是否在影响期内"""
        if current_date is None:
            current_date = datetime.now()
        
        has_period = record.get('有无影响期', '无')
        
        # 无影响期或影响期为空
        if has_period == '无' or pd.isna(has_period) or str(has_period).strip() == '':
            return '已过影响期'
        
        end_date = record.get('影响期截止日期')
        if end_date is None:
            return '已过影响期'
        
        if current_date > end_date:
            return '已过影响期'
        else:
            return '尚在影响期内'
    
    def determine_template(self, records: List[Dict], current_date: datetime = None) -> Tuple[int, Dict]:
        """
        根据检索结果确定匹配的模板编号
        返回：(模板编号, 相关信息字典)
        """
        if current_date is None:
            current_date = datetime.now()
        
        if not records:
            # 无任何记录 → 模板1
            return (1, {})
        
        # 分析记录状态
        has_processing = False  # 是否有正在办理的举报
        has_in_period = False   # 是否有尚在影响期内的处分
        latest_record = None    # 最新的处分记录
        all_passed = True       # 是否全部已过影响期
        
        for record in records:
            status = self.check_influence_period(record, current_date)
            
            # 检查是否有"正在办理"状态（这里简化处理，实际需额外字段）
            # 假设：如果有记录且影响期截止日期在未来很远，可能是正在办理
            # 实际应根据"信访举报状态"字段判断
            
            if status == '尚在影响期内':
                has_in_period = True
                all_passed = False
                if latest_record is None:
                    latest_record = record
                else:
                    # 取最新的
                    if record['问责时间'] > latest_record['问责时间']:
                        latest_record = record
        
        # 优先级判断
        if has_processing:
            return (7, {'name': records[0]['姓名'] if records else ''})
        
        if has_in_period and latest_record:
            # 模板8：尚在影响期内
            info = {
                'name': latest_record['姓名'],
                'problem': latest_record['事由'] or '',
                'punishment': latest_record['问责情况'],
                'start_date': self.format_date_chinese(self.excel_date_to_python(latest_record['问责时间_raw'])),
                'end_date': self.format_date_chinese(latest_record['影响期截止日期'])
            }
            return (8, info)
        
        if all_passed and records:
            # 全部已过影响期，取最新的一条
            latest = max(records, key=lambda x: x['问责时间'] if x['问责时间'] else '0000-00-00')
            info = {
                'name': latest['姓名'],
                'problem': latest['事由'] or '',
                'punishment': latest['问责情况'],
                'date': self.format_date_chinese(self.excel_date_to_python(latest['问责时间_raw']))
            }
            # 判断用模板5还是6
            if '未收到' in str(latest.get('信访状态', '')):
                return (6, info)
            else:
                return (6, info)  # 默认用模板6
        
        return (1, {})
    
    def generate_answer(self, name: str, event_type: str = '干部选拔任用', 
                       current_date: datetime = None) -> Dict:
        """
        生成完整的廉政意见答复
        
        参数:
            name: 被查询人姓名
            event_type: 事项类型（干部选拔任用/表彰奖励等）
            current_date: 当前日期（用于影响期判断）
        
        返回:
            包含检索结果和答复文本的字典
        """
        if current_date is None:
            current_date = datetime.now()
        
        # 1. 检索记录
        records = self.search_person(name)
        
        # 2. 构建检索智答结果
        search_result = []
        for record in records:
            search_result.append({
                '姓名': record['姓名'],
                '检索分类': record['检索分类'],
                '处理机构': record['处理机构'],
                '问责情况': record['问责情况'],
                '问责时间': record['问责时间'],
                '有无影响期': record['有无影响期'],
                '影响期截止日期': self.format_date_standard(record['影响期截止日期']) if record['影响期截止日期'] else '',
                '事由': record['事由'],
                '影响期状态': self.check_influence_period(record, current_date)
            })
        
        # 3. 匹配模板并生成答复
        template_num, info = self.determine_template(records, current_date)
        
        # 获取模板文本
        template_text = self.selection_templates.get(template_num, '')
        
        # 填充变量
        answer_text = template_text
        
        if 'date' in info:
            # 按顺序替换模板6中的变量
            date_str = info['date']
            problem_str = info['problem']
            punishment_str = info['punishment']
            
            # 先替换日期
            answer_text = answer_text.replace('XXXX年XX月', date_str)
            # 再替换问题（注意只替换第一个XXX问题）
            answer_text = answer_text.replace('XXX问题', problem_str, 1)
            # 替换处分类型
            answer_text = answer_text.replace('诫勉/XXX党纪政务处分', punishment_str)
        
        if 'start_date' in info and 'end_date' in info:
            # 模板8需要替换两个日期
            start_date = info['start_date']
            end_date = info['end_date']
            problem = info.get('problem', '')
            punishment = info.get('punishment', '')
            
            # 先替换问题
            answer_text = answer_text.replace('XXX问题', problem, 1)
            # 替换处分和日期（XXXX年XX月受到诫勉或党纪政务处分 → 2025年04月受到记过处分）
            answer_text = re.sub(r'XXXX年XX月受到诫勉或党纪政务处分', 
                                f"{start_date}受到{punishment}处分", 
                                answer_text)
            # 替换影响期范围（自XXXX年XX月起至XXXX年XX月止 → 自2025年04月起至2026年04月止）
            answer_text = re.sub(r'自XXXX年XX月起至XXXX年XX月止', 
                                f"自{start_date}起至{end_date}止", 
                                answer_text)
        
        # 统一替换姓名（最后替换，避免影响其他变量）
        answer_text = answer_text.replace('XXX', name)
        
        return {
            '查询姓名': name,
            '事项类型': event_type,
            '当前日期': current_date.strftime('%Y-%m-%d'),
            '检索结果': search_result,
            '匹配模板': template_num,
            '答复文本': answer_text
        }
    
    def print_result(self, result: Dict):
        """格式化打印结果"""
        print("=" * 70)
        print(f"查询姓名：{result['查询姓名']}")
        print(f"事项类型：{result['事项类型']}")
        print(f"当前日期：{result['当前日期']}")
        print("-" * 70)
        print("【检索智答】")
        if result['检索结果']:
            for i, record in enumerate(result['检索结果'], 1):
                print(f"  {i}. [{record['检索分类']}] {record['问责情况']} "
                      f"({record['问责时间']}) - {record['事由']}")
                print(f"     影响期状态：{record['影响期状态']} "
                      f"(截止：{record['影响期截止日期']})")
        else:
            print("  未查询到相关记录")
        print("-" * 70)
        print(f"【智答助手】(匹配模板{result['匹配模板']})")
        print(f"  {result['答复文本']}")
        print("=" * 70)


def main():
    """主函数 - 试运行演示"""
    # 初始化系统
    system = IntegrityAnswerSystem('/workspace/廉政意见智答回复意见.xlsx')
    
    print("\n" + "=" * 70)
    print("廉政意见智答系统 - 试运行")
    print("=" * 70)
    
    # 测试案例1：王五（有两条记录，均已过影响期）
    print("\n>>> 测试案例1：王五（干部选拔任用，当前日期：2026-05-11）")
    result1 = system.generate_answer('王五', '干部选拔任用', datetime(2026, 5, 11))
    system.print_result(result1)
    
    # 测试案例2：张三（可能有在影响期内的记录）
    print("\n>>> 测试案例2：张三（干部选拔任用，当前日期：2026-05-11）")
    result2 = system.generate_answer('张三', '干部选拔任用', datetime(2026, 5, 11))
    system.print_result(result2)
    
    # 测试案例3：曹六
    print("\n>>> 测试案例3：曹六（干部选拔任用，当前日期：2026-05-11）")
    result3 = system.generate_answer('曹六', '干部选拔任用', datetime(2026, 5, 11))
    system.print_result(result3)
    
    # 测试案例4：刘二
    print("\n>>> 测试案例4：刘二（干部选拔任用，当前日期：2026-05-11）")
    result4 = system.generate_answer('刘二', '干部选拔任用', datetime(2026, 5, 11))
    system.print_result(result4)
    
    # 测试案例5：不存在的姓名（应匹配模板1）
    print("\n>>> 测试案例5：李明（不存在记录，应返回模板1）")
    result5 = system.generate_answer('李明', '干部选拔任用', datetime(2026, 5, 11))
    system.print_result(result5)


if __name__ == '__main__':
    main()
