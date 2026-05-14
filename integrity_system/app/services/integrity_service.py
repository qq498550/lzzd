from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.database import DisciplineRecord, ViolationRecord, PetitionReport, AnswerTemplate, QueryLog
from app.schemas import SearchResult


class IntegrityService:
    """廉政意见智答核心服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def search_person_records(self, name: str, matter_type: str = None) -> List[SearchResult]:
        """检索某人的所有违纪、违规、信访记录"""
        results = []
        
        # 当选择"其他"类型时，需要查询包含"表彰奖励","职级晋升","交流任职","其他"四个类型的内容
        # 但这里的search_person_records是查询违纪、违规、信访记录，这些记录本身没有matter_type字段
        # 所以无论matter_type是什么，都返回该人的所有记录
        # matter_type的过滤逻辑在match_template中处理
        
        # 查询违纪记录 - 使用精确匹配而非模糊查询
        discipline_records = self.db.query(DisciplineRecord).filter(
            DisciplineRecord.name == name
        ).all()
        
        for record in discipline_records:
            influence_status = self._check_influence_period(
                record.has_influence_period,
                record.influence_end_date
            )
            results.append(SearchResult(
                record_type="discipline",
                name=record.name,
                department=record.department,
                position=record.position,
                processing_org=record.processing_org,
                accountability_type=record.accountability_type,
                accountability_date=record.accountability_date,
                has_influence_period=record.has_influence_period,
                influence_end_date=record.influence_end_date,
                reason=record.reason,
                remark=record.remark if hasattr(record, 'remark') else '',
                influence_status=influence_status
            ))
        
        # 查询违规记录 - 使用精确匹配而非模糊查询
        violation_records = self.db.query(ViolationRecord).filter(
            ViolationRecord.name == name
        ).all()
        
        for record in violation_records:
            influence_status = self._check_influence_period(
                record.has_influence_period,
                record.influence_end_date
            )
            results.append(SearchResult(
                record_type="violation",
                name=record.name,
                department=record.department,
                position=record.position,
                processing_org=record.processing_org,
                accountability_type=record.violation_type,
                accountability_date=record.violation_date,
                has_influence_period=record.has_influence_period,
                influence_end_date=record.influence_end_date,
                reason=record.reason,
                remark=record.remark if hasattr(record, 'remark') else '',
                influence_status=influence_status
            ))
        
        # 查询信访举报记录 - 使用精确匹配而非模糊查询
        petition_records = self.db.query(PetitionReport).filter(
            PetitionReport.name == name
        ).all()
        
        for record in petition_records:
            # 信访举报的影响期状态特殊处理
            if record.verification_result:
                influence_status = "已办结"
            else:
                influence_status = "正在办理中"
            
            results.append(SearchResult(
                record_type="petition",
                name=record.name,
                department=None,
                position=None,
                processing_org="信访部门",
                accountability_type="信访举报",
                accountability_date=record.report_date,
                has_influence_period=False,
                influence_end_date=None,
                reason=record.report_content[:100] + "..." if len(record.report_content) > 100 else record.report_content,
                remark=record.remark if hasattr(record, 'remark') else '',
                influence_status=influence_status
            ))
        
        # 按时间排序
        results.sort(key=lambda x: x.accountability_date or date.min, reverse=True)
        
        return results
    
    def _check_influence_period(self, has_period: bool, end_date: Optional[date]) -> str:
        """判断影响期状态"""
        if not has_period or end_date is None:
            return "已过影响期"
        
        current_date = date.today()
        if current_date > end_date:
            return "已过影响期"
        else:
            return "尚在影响期内"
    
    def match_template(self, search_results: List[SearchResult], matter_type: str) -> Dict[str, Any]:
        """根据检索结果匹配答复模板"""
        
        # 当选择"其他"类型时，需要查询包含"表彰奖励","职级晋升","交流任职","其他"四个类型的内容
        # 由于违纪、违规、信访记录本身没有matter_type字段，所以search_person_records返回该人的所有记录
        # 这里的query_matter_types变量目前主要用于逻辑说明，实际过滤在业务层处理
        query_matter_types = [matter_type]
        if matter_type == "其他":
            query_matter_types = ["干部选拔任用", "表彰奖励", "职级晋升", "交流任职", "其他"]
        
        # 优先级判断逻辑
        has_processing_petition = any(
            r.record_type == "petition" and r.influence_status == "正在办理中" 
            for r in search_results
        )
        
        has_in_progress_influence = any(
            r.influence_status == "尚在影响期内" 
            for r in search_results
        )
        
        has_completed_records = any(
            r.record_type in ["discipline", "violation"] and r.influence_status == "已过影响期"
            for r in search_results
        )
        
        has_petition_completed = any(
            r.record_type == "petition" and r.influence_status == "已办结"
            for r in search_results
        )
        
        # 检查是否有举报但核查否认+组织采信
        has_petition_denied = any(
            r.record_type == "petition" and 
            r.influence_status == "已办结" and
            "未发现" in r.reason
            for r in search_results
        )
        
        # 仅受批评教育/谈话提醒（组织处理）
        has_only_organizational_handling = (
            has_completed_records and 
            not has_in_progress_influence and
            all(
                r.accountability_type in ["批评教育", "谈话提醒", "诫勉谈话", "责令检查"]
                for r in search_results if r.record_type in ["discipline", "violation"]
            )
        )
        
        # 模板匹配
        template_code = None
        template_name = None
        conclusion = None
        
        if not search_results:
            # 模板1：无任何记录
            template_code = "T1"
            template_name = "无记录模板"
            conclusion = "不持异议"
        elif has_processing_petition:
            # 模板7：举报正在办理中
            template_code = "T7"
            template_name = "正在办理模板"
            conclusion = "建议暂缓提拔"
        elif has_in_progress_influence:
            # 模板8：尚在影响期内
            template_code = "T8"
            template_name = "影响期内模板"
            conclusion = "建议不宜作为拟提拔人选"
        elif has_petition_denied:
            # 模板2或3：举报已核查但无问题
            template_code = "T2"
            template_name = "举报查否模板"
            conclusion = "不持异议"
        elif has_only_organizational_handling:
            # 模板4：仅组织处理
            template_code = "T4"
            template_name = "组织处理模板"
            conclusion = "不持异议"
        elif has_completed_records:
            # 模板5或6：已过影响期
            template_code = "T6"
            template_name = "已过影响期模板"
            conclusion = "不持异议"
        elif has_petition_completed:
            # 模板2或3
            template_code = "T3"
            template_name = "举报无证据模板"
            conclusion = "不持异议"
        else:
            # 默认模板1
            template_code = "T1"
            template_name = "无记录模板"
            conclusion = "不持异议"
        
        # 获取模板内容
        template_record = self.db.query(AnswerTemplate).filter(
            AnswerTemplate.template_code == template_code,
            AnswerTemplate.is_active == True
        ).first()
        
        template_content = ""
        if template_record:
            template_content = template_record.template_content
        else:
            template_content = self._get_default_template(template_code)
        
        return {
            "template_code": template_code,
            "template_name": template_name,
            "conclusion": conclusion,
            "template_content": template_content
        }
    
    def _get_default_template(self, template_code: str) -> str:
        """获取默认模板内容"""
        templates = {
            "T1": "经审核，未收到过{person_name}同志的信访举报。对{person_name}同志作为拟{matter_type}人选不持异议。",
            "T2": "经审核，收到反映{person_name}同志的信访举报，已核查完毕并采信本人说明。对{person_name}同志作为拟{matter_type}人选不持异议。",
            "T3": "经审核，收到反映{person_name}同志的信访举报，经核查未发现相关证据。对{person_name}同志作为拟{matter_type}人选不持异议。",
            "T4": "经审核，{person_name}同志于{date}因{reason}受到{type}处理（已过影响期）。对{person_name}同志作为拟{matter_type}人选不持异议。",
            "T5": "经审核，未收到过{person_name}同志的信访举报。此外，{date}{person_name}同志因{reason}问题，受到{type}处分（已过影响期）。对{person_name}同志作为拟{matter_type}人选不持异议。",
            "T6": "经审核，未收到过{person_name}同志的信访举报。此外，{date}{person_name}同志因{reason}问题，受到{type}处分（已过影响期）。对{person_name}同志作为拟{matter_type}人选不持异议。",
            "T7": "经审核，目前收到反映{person_name}同志的信访举报正在办理中，建议暂缓{matter_type}。",
            "T8": "经审核，{person_name}同志于{date}因{reason}问题，受到{type}处分（尚在影响期内），建议不宜作为拟{matter_type}人选。"
        }
        return templates.get(template_code, "")
    
    def generate_answer(self, template_content: str, person_name: str, 
                       matter_type: str, search_results: List[SearchResult]) -> str:
        """生成最终答复文本"""
        
        # 找出最新的处分记录用于填充
        latest_discipline = None
        for r in search_results:
            if r.record_type in ["discipline", "violation"]:
                if latest_discipline is None or (r.accountability_date and 
                    (latest_discipline.accountability_date is None or 
                     r.accountability_date > latest_discipline.accountability_date)):
                    latest_discipline = r
        
        # 格式化日期
        date_str = ""
        type_str = ""
        reason_str = ""
        
        if latest_discipline and latest_discipline.accountability_date:
            date_str = latest_discipline.accountability_date.strftime("%Y年%m月")
            type_str = latest_discipline.accountability_type or ""
            reason_str = latest_discipline.reason or ""
        
        # 替换变量
        answer = template_content.format(
            person_name=person_name,
            matter_type=matter_type,
            date=date_str,
            type=type_str,
            reason=reason_str
        )
        
        return answer
    
    def log_query(self, query_name: str, matter_type: str, 
                  template_code: str, conclusion: str, operator: str = "system"):
        """记录查询日志"""
        try:
            print(f"[DEBUG] 开始记录日志: query_name={query_name}, matter_type={matter_type}, template_code={template_code}")
            log = QueryLog(
                query_name=query_name,
                matter_type=matter_type,
                result_template=template_code,
                conclusion=conclusion,
                operator=operator
            )
            self.db.add(log)
            self.db.commit()
            print(f"[DEBUG] 日志记录成功!")
        except Exception as e:
            self.db.rollback()
            print(f"[ERROR] 记录查询日志失败: {e}")
