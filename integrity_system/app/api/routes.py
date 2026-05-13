"""
廉政意见智答系统 - API 路由模块
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Form, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
import json
import io
import csv

from app.models.database import get_db
from app.schemas import (
    DisciplineRecordCreate, DisciplineRecordResponse, DisciplineRecordUpdate,
    ViolationRecordCreate, ViolationRecordResponse, ViolationRecordUpdate,
    PetitionReportCreate, PetitionReportResponse, PetitionReportUpdate,
    AnswerTemplateCreate, AnswerTemplateResponse, AnswerTemplateUpdate,
    QueryRequest, QueryResponse
)
from app.services.integrity_service import IntegrityService

router = APIRouter()

# 简单的管理员账号验证（实际生产环境应使用更安全的认证方式）
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def verify_admin_credentials(username: str, password: str) -> bool:
    """验证管理员账号"""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


# ==================== 违纪记录管理 ====================
@router.post("/discipline/", response_model=DisciplineRecordResponse, tags=["违纪记录"])
def create_discipline_record(record: DisciplineRecordCreate, db: Session = Depends(get_db)):
    """创建违纪记录"""
    from app.models.database import DisciplineRecord
    db_record = DisciplineRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("/discipline/", response_model=List[DisciplineRecordResponse], tags=["违纪记录"])
def list_discipline_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取违纪记录列表"""
    from app.models.database import DisciplineRecord
    records = db.query(DisciplineRecord).offset(skip).limit(limit).all()
    return records


@router.get("/discipline/{record_id}", response_model=DisciplineRecordResponse, tags=["违纪记录"])
def get_discipline_record(record_id: int, db: Session = Depends(get_db)):
    """获取单条违纪记录"""
    from app.models.database import DisciplineRecord
    record = db.query(DisciplineRecord).filter(DisciplineRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.put("/discipline/{record_id}", response_model=DisciplineRecordResponse, tags=["违纪记录"])
def update_discipline_record(record_id: int, record: DisciplineRecordUpdate, db: Session = Depends(get_db)):
    """更新违纪记录"""
    from app.models.database import DisciplineRecord
    db_record = db.query(DisciplineRecord).filter(DisciplineRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    update_data = record.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/discipline/{record_id}", tags=["违纪记录"])
def delete_discipline_record(record_id: int, db: Session = Depends(get_db)):
    """删除违纪记录"""
    from app.models.database import DisciplineRecord
    db_record = db.query(DisciplineRecord).filter(DisciplineRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(db_record)
    db.commit()
    return {"message": "删除成功"}


# ==================== 违规记录管理 ====================
@router.post("/violation/", response_model=ViolationRecordResponse, tags=["违规记录"])
def create_violation_record(record: ViolationRecordCreate, db: Session = Depends(get_db)):
    """创建违规记录"""
    from app.models.database import ViolationRecord
    db_record = ViolationRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("/violation/", response_model=List[ViolationRecordResponse], tags=["违规记录"])
def list_violation_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取违规记录列表"""
    from app.models.database import ViolationRecord
    records = db.query(ViolationRecord).offset(skip).limit(limit).all()
    return records


@router.get("/violation/{record_id}", response_model=ViolationRecordResponse, tags=["违规记录"])
def get_violation_record(record_id: int, db: Session = Depends(get_db)):
    """获取单条违规记录"""
    from app.models.database import ViolationRecord
    record = db.query(ViolationRecord).filter(ViolationRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.put("/violation/{record_id}", response_model=ViolationRecordResponse, tags=["违规记录"])
def update_violation_record(record_id: int, record: ViolationRecordUpdate, db: Session = Depends(get_db)):
    """更新违规记录"""
    from app.models.database import ViolationRecord
    db_record = db.query(ViolationRecord).filter(ViolationRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    update_data = record.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/violation/{record_id}", tags=["违规记录"])
def delete_violation_record(record_id: int, db: Session = Depends(get_db)):
    """删除违规记录"""
    from app.models.database import ViolationRecord
    db_record = db.query(ViolationRecord).filter(ViolationRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(db_record)
    db.commit()
    return {"message": "删除成功"}


# ==================== 信访举报管理 ====================
@router.post("/petition/", response_model=PetitionReportResponse, tags=["信访举报"])
def create_petition_report(report: PetitionReportCreate, db: Session = Depends(get_db)):
    """创建信访举报记录"""
    from app.models.database import PetitionReport
    db_record = PetitionReport(**report.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("/petition/", response_model=List[PetitionReportResponse], tags=["信访举报"])
def list_petition_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取信访举报列表"""
    from app.models.database import PetitionReport
    records = db.query(PetitionReport).offset(skip).limit(limit).all()
    return records


@router.get("/petition/{report_id}", response_model=PetitionReportResponse, tags=["信访举报"])
def get_petition_report(report_id: int, db: Session = Depends(get_db)):
    """获取单条信访举报"""
    from app.models.database import PetitionReport
    report = db.query(PetitionReport).filter(PetitionReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="记录不存在")
    return report


@router.put("/petition/{report_id}", response_model=PetitionReportResponse, tags=["信访举报"])
def update_petition_report(report_id: int, report: PetitionReportUpdate, db: Session = Depends(get_db)):
    """更新信访举报"""
    from app.models.database import PetitionReport
    db_record = db.query(PetitionReport).filter(PetitionReport.id == report_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    update_data = report.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_record, key, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/petition/{report_id}", tags=["信访举报"])
def delete_petition_report(report_id: int, db: Session = Depends(get_db)):
    """删除信访举报"""
    from app.models.database import PetitionReport
    db_record = db.query(PetitionReport).filter(PetitionReport.id == report_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(db_record)
    db.commit()
    return {"message": "删除成功"}


# ==================== 答复模板管理 ====================
@router.post("/template/", response_model=AnswerTemplateResponse, tags=["答复模板"])
def create_template(template: AnswerTemplateCreate, db: Session = Depends(get_db)):
    """创建答复模板"""
    from app.models.database import AnswerTemplate
    db_template = AnswerTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/template/", response_model=List[AnswerTemplateResponse], tags=["答复模板"])
def list_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取答复模板列表"""
    from app.models.database import AnswerTemplate
    templates = db.query(AnswerTemplate).offset(skip).limit(limit).all()
    return templates


@router.get("/template/{template_id}", response_model=AnswerTemplateResponse, tags=["答复模板"])
def get_template(template_id: int, db: Session = Depends(get_db)):
    """获取单个模板"""
    from app.models.database import AnswerTemplate
    template = db.query(AnswerTemplate).filter(AnswerTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template


@router.put("/template/{template_id}", response_model=AnswerTemplateResponse, tags=["答复模板"])
def update_template(template_id: int, template: AnswerTemplateUpdate, db: Session = Depends(get_db)):
    """更新模板"""
    from app.models.database import AnswerTemplate
    db_template = db.query(AnswerTemplate).filter(AnswerTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    update_data = template.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_template, key, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/template/{template_id}", tags=["答复模板"])
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """删除模板"""
    from app.models.database import AnswerTemplate
    db_template = db.query(AnswerTemplate).filter(AnswerTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="模板不存在")
    db.delete(db_template)
    db.commit()
    return {"message": "删除成功"}


# ==================== 智能查询核心接口 ====================
@router.post("/query/", response_model=QueryResponse, tags=["智能查询"])
def intelligent_query(query: QueryRequest, db: Session = Depends(get_db)):
    """廉政意见智能查询"""
    service = IntegrityService(db)
    
    # 检索记录 - 当选择"其他"类型时，需要查询所有类型的记录
    search_results = service.search_person_records(query.name, query.matter_type)
    
    # 匹配模板
    match_result = service.match_template(search_results, query.matter_type)
    
    # 生成答复
    generated_answer = service.generate_answer(
        match_result["template_content"],
        query.name,
        query.matter_type,
        search_results
    )
    
    # 记录日志
    service.log_query(
        query_name=query.name,
        matter_type=query.matter_type,
        template_code=match_result["template_code"],
        conclusion=match_result["conclusion"]
    )
    
    return QueryResponse(
        query_name=query.name,
        matter_type=query.matter_type,
        search_results=search_results,
        matched_template=match_result["template_name"],
        template_code=match_result["template_code"],
        conclusion=match_result["conclusion"],
        generated_answer=generated_answer
    )


@router.get("/query/logs", response_model=List[dict], tags=["智能查询"])
def get_query_logs(limit: int = 100, db: Session = Depends(get_db)):
    """获取所有查询日志"""
    from app.models.database import QueryLog
    logs = db.query(QueryLog).order_by(
        QueryLog.query_time.desc()
    ).limit(limit).all()
    return logs


@router.get("/query/{name}/history", tags=["智能查询"])
def get_query_history(name: str, limit: int = 10, db: Session = Depends(get_db)):
    """获取某人的查询历史"""
    from app.models.database import QueryLog
    # 使用精确匹配查询姓名
    logs = db.query(QueryLog).filter(
        QueryLog.query_name == name
    ).order_by(QueryLog.query_time.desc()).limit(limit).all()
    return logs


# ==================== 管理员登录验证 ====================
@router.post("/admin/login", tags=["管理员"])
def admin_login(username: str = Form(...), password: str = Form(...)):
    """管理员登录验证"""
    if verify_admin_credentials(username, password):
        return {"success": True, "message": "登录成功"}
    else:
        raise HTTPException(status_code=401, detail="用户名或密码错误")


# ==================== 数据导入导出 ====================
@router.get("/export/discipline", tags=["数据导入导出"])
def export_discipline_records(db: Session = Depends(get_db)):
    """导出违纪记录为CSV"""
    from app.models.database import DisciplineRecord
    records = db.query(DisciplineRecord).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', '姓名', '部门', '职务', '处理机构', '问责情况', '问责时间', 
                     '有无影响期', '影响期截止', '事由', '状态'])
    
    for r in records:
        writer.writerow([
            r.id, r.name, r.department or '', r.position or '', r.processing_org or '',
            r.accountability_type, r.accountability_date, 
            '有' if r.has_influence_period else '无', r.influence_end_date or '',
            r.reason or '', r.status
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=违纪记录.csv"}
    )


@router.get("/export/violation", tags=["数据导入导出"])
def export_violation_records(db: Session = Depends(get_db)):
    """导出违规记录为CSV"""
    from app.models.database import ViolationRecord
    records = db.query(ViolationRecord).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', '姓名', '部门', '职务', '处理机构', '问责类型', '问责时间', 
                     '有无影响期', '影响期截止', '事由', '状态'])
    
    for r in records:
        writer.writerow([
            r.id, r.name, r.department or '', r.position or '', r.processing_org or '',
            r.violation_type, r.violation_date,
            '有' if r.has_influence_period else '无', r.influence_end_date or '',
            r.reason or '', r.status
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=违规记录.csv"}
    )


@router.get("/export/petition", tags=["数据导入导出"])
def export_petition_records(db: Session = Depends(get_db)):
    """导出信访举报记录为CSV"""
    from app.models.database import PetitionReport
    records = db.query(PetitionReport).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', '姓名', '举报日期', '举报内容', '核查结果', '组织采信', '状态'])
    
    for r in records:
        writer.writerow([
            r.id, r.name, r.report_date, r.report_content or '',
            r.verification_result or '', 
            '是' if r.organization_adoption else ('否' if r.organization_adoption is False else ''),
            r.status
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=信访举报记录.csv"}
    )


@router.get("/export/template", tags=["数据导入导出"])
def export_templates(db: Session = Depends(get_db)):
    """导出答复模板为CSV"""
    from app.models.database import AnswerTemplate
    records = db.query(AnswerTemplate).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', '模板编号', '模板名称', '适用场景', '事项类型', '模板内容', '优先级', '是否启用'])
    
    for r in records:
        writer.writerow([
            r.id, r.template_code, r.template_name, r.scenario_type, r.matter_type,
            r.template_content, r.priority, '是' if r.is_active else '否'
        ])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=答复模板.csv"}
    )


@router.get("/template/download", tags=["数据导入导出"])
def download_import_template():
    """下载导入模板"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 违纪记录模板
    writer.writerow(['=== 违纪记录导入模板 ==='])
    writer.writerow(['姓名', '部门', '职务', '处理机构', '问责情况', '问责时间 (YYYY-MM-DD)', 
                     '有无影响期 (true/false)', '影响期截止日期 (YYYY-MM-DD)', '事由', '状态 (completed/processing)'])
    writer.writerow(['张三', 'XX部门', 'XX职务', 'XX纪委', '党内警告', '2023-01-15', 
                     'true', '2024-01-15', '违反工作纪律', 'completed'])
    writer.writerow([])
    
    # 违规记录模板
    writer.writerow(['=== 违规记录导入模板 ==='])
    writer.writerow(['姓名', '部门', '职务', '处理机构', '问责类型', '问责时间 (YYYY-MM-DD)', 
                     '有无影响期 (true/false)', '影响期截止日期 (YYYY-MM-DD)', '事由', '状态 (completed/processing)'])
    writer.writerow(['李四', 'XX部门', 'XX职务', 'XX纪委', '政务记过', '2023-02-20', 
                     'true', '2024-02-20', '违反廉洁纪律', 'completed'])
    writer.writerow([])
    
    # 信访举报模板
    writer.writerow(['=== 信访举报导入模板 ==='])
    writer.writerow(['姓名', '举报日期 (YYYY-MM-DD)', '举报内容', '核查结果', '组织采信 (true/false/null)', '状态 (processing/completed/closed)'])
    writer.writerow(['王五', '2023-03-10', '反映收受礼金问题', '未发现相关证据', 'false', 'completed'])
    writer.writerow([])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=导入模板.csv"}
    )


@router.post("/import/discipline", tags=["数据导入导出"])
async def import_discipline_records(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """导入违纪记录"""
    from app.models.database import DisciplineRecord
    
    contents = await file.read()
    lines = contents.decode('utf-8').split('\n')
    
    count = 0
    for i, line in enumerate(lines[1:], start=2):  # 跳过表头
        if not line.strip():
            continue
        try:
            values = line.split(',')
            if len(values) < 6:
                continue
            
            has_period = values[6].strip().lower() == 'true' if len(values) > 6 else True
            influence_end = None
            if len(values) > 7 and values[7].strip():
                try:
                    influence_end = datetime.strptime(values[7].strip(), '%Y-%m-%d').date()
                except:
                    pass
            
            record = DisciplineRecord(
                name=values[0].strip(),
                department=values[1].strip() if len(values) > 1 and values[1].strip() else None,
                position=values[2].strip() if len(values) > 2 and values[2].strip() else None,
                processing_org=values[3].strip() if len(values) > 3 and values[3].strip() else None,
                accountability_type=values[4].strip(),
                accountability_date=datetime.strptime(values[5].strip(), '%Y-%m-%d').date(),
                has_influence_period=has_period,
                influence_end_date=influence_end,
                reason=values[8].strip() if len(values) > 8 and values[8].strip() else '',
                status=values[9].strip() if len(values) > 9 and values[9].strip() else 'completed'
            )
            db.add(record)
            count += 1
        except Exception as e:
            continue
    
    db.commit()
    return {"success": True, "message": f"成功导入 {count} 条违纪记录"}


@router.post("/import/violation", tags=["数据导入导出"])
async def import_violation_records(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """导入违规记录"""
    from app.models.database import ViolationRecord
    
    contents = await file.read()
    lines = contents.decode('utf-8').split('\n')
    
    count = 0
    for i, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        try:
            values = line.split(',')
            if len(values) < 6:
                continue
            
            has_period = values[6].strip().lower() == 'true' if len(values) > 6 else True
            influence_end = None
            if len(values) > 7 and values[7].strip():
                try:
                    influence_end = datetime.strptime(values[7].strip(), '%Y-%m-%d').date()
                except:
                    pass
            
            record = ViolationRecord(
                name=values[0].strip(),
                department=values[1].strip() if len(values) > 1 and values[1].strip() else None,
                position=values[2].strip() if len(values) > 2 and values[2].strip() else None,
                processing_org=values[3].strip() if len(values) > 3 and values[3].strip() else None,
                violation_type=values[4].strip(),
                violation_date=datetime.strptime(values[5].strip(), '%Y-%m-%d').date(),
                has_influence_period=has_period,
                influence_end_date=influence_end,
                reason=values[8].strip() if len(values) > 8 and values[8].strip() else '',
                status=values[9].strip() if len(values) > 9 and values[9].strip() else 'completed'
            )
            db.add(record)
            count += 1
        except Exception as e:
            continue
    
    db.commit()
    return {"success": True, "message": f"成功导入 {count} 条违规记录"}


@router.post("/import/petition", tags=["数据导入导出"])
async def import_petition_records(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """导入信访举报记录"""
    from app.models.database import PetitionReport
    
    contents = await file.read()
    lines = contents.decode('utf-8').split('\n')
    
    count = 0
    for i, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        try:
            values = line.split(',')
            if len(values) < 3:
                continue
            
            org_adoption = None
            if len(values) > 4 and values[4].strip():
                if values[4].strip().lower() == 'true':
                    org_adoption = True
                elif values[4].strip().lower() == 'false':
                    org_adoption = False
            
            record = PetitionReport(
                name=values[0].strip(),
                report_date=datetime.strptime(values[1].strip(), '%Y-%m-%d').date(),
                report_content=values[2].strip() if len(values) > 2 else '',
                verification_result=values[3].strip() if len(values) > 3 and values[3].strip() else None,
                organization_adoption=org_adoption,
                status=values[5].strip() if len(values) > 5 and values[5].strip() else 'processing'
            )
            db.add(record)
            count += 1
        except Exception as e:
            continue
    
    db.commit()
    return {"success": True, "message": f"成功导入 {count} 条信访举报记录"}
