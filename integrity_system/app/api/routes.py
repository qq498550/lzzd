"""
廉政意见智答系统 - API 路由模块
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

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


@router.get("/query/{name}/history", tags=["智能查询"])
def get_query_history(name: str, limit: int = 10, db: Session = Depends(get_db)):
    """获取某人的查询历史"""
    from app.models.database import QueryLog
    logs = db.query(QueryLog).filter(
        QueryLog.query_name.ilike(f"%{name}%")
    ).order_by(QueryLog.query_time.desc()).limit(limit).all()
    return logs
