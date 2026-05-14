from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


# ==================== 违纪记录相关 ====================
class DisciplineRecordBase(BaseModel):
    name: str = Field(..., description="姓名")
    branch_company: Optional[str] = Field(None, description="分公司")
    department: Optional[str] = Field(None, description="部门")
    position: Optional[str] = Field(None, description="职务")
    processing_org: Optional[str] = Field(None, description="处理机构")
    accountability_type: str = Field(..., description="问责情况")
    accountability_date: date = Field(..., description="问责时间")
    has_influence_period: bool = Field(True, description="有无影响期")
    influence_end_date: Optional[date] = Field(None, description="影响期截止日期")
    reason: str = Field(..., description="事由")
    remark: Optional[str] = Field("", description="备注")


class DisciplineRecordCreate(DisciplineRecordBase):
    pass


class DisciplineRecordUpdate(BaseModel):
    name: Optional[str] = None
    branch_company: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    processing_org: Optional[str] = None
    accountability_type: Optional[str] = None
    accountability_date: Optional[date] = None
    has_influence_period: Optional[bool] = None
    influence_end_date: Optional[date] = None
    reason: Optional[str] = None
    remark: Optional[str] = None


class DisciplineRecordResponse(DisciplineRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 违规记录相关 ====================
class ViolationRecordBase(BaseModel):
    name: str = Field(..., description="姓名")
    branch_company: Optional[str] = Field(None, description="分公司")
    department: Optional[str] = Field(None, description="部门")
    position: Optional[str] = Field(None, description="职务")
    processing_org: Optional[str] = Field(None, description="处理机构")
    violation_type: str = Field(..., description="问责类型")
    violation_date: date = Field(..., description="问责时间")
    has_influence_period: bool = Field(True, description="有无影响期")
    influence_end_date: Optional[date] = Field(None, description="影响期截止日期")
    reason: str = Field(..., description="事由")
    remark: Optional[str] = Field("", description="备注")


class ViolationRecordCreate(ViolationRecordBase):
    pass


class ViolationRecordUpdate(BaseModel):
    name: Optional[str] = None
    branch_company: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    processing_org: Optional[str] = None
    violation_type: Optional[str] = None
    violation_date: Optional[date] = None
    has_influence_period: Optional[bool] = None
    influence_end_date: Optional[date] = None
    reason: Optional[str] = None
    remark: Optional[str] = None


class ViolationRecordResponse(ViolationRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 信访举报相关 ====================
class PetitionReportBase(BaseModel):
    name: str = Field(..., description="姓名")
    branch_company: Optional[str] = Field(None, description="分公司")
    department: Optional[str] = Field(None, description="部门")
    report_date: date = Field(..., description="举报日期")
    report_content: str = Field(..., description="举报内容")
    verification_result: Optional[str] = Field(None, description="核查结果")
    organization_adoption: Optional[bool] = Field(None, description="组织是否采信")
    has_influence_period: bool = Field(False, description="有无影响期")
    influence_end_date: Optional[date] = Field(None, description="影响期截止日期")
    remark: Optional[str] = Field("", description="备注")


class PetitionReportCreate(PetitionReportBase):
    pass


class PetitionReportUpdate(BaseModel):
    name: Optional[str] = None
    branch_company: Optional[str] = None
    department: Optional[str] = None
    report_date: Optional[date] = None
    report_content: Optional[str] = None
    verification_result: Optional[str] = None
    organization_adoption: Optional[bool] = None
    has_influence_period: Optional[bool] = None
    influence_end_date: Optional[date] = None
    remark: Optional[str] = None


class PetitionReportResponse(PetitionReportBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 答复模板相关 ====================
class AnswerTemplateBase(BaseModel):
    template_code: str = Field(..., description="模板编号")
    template_name: str = Field(..., description="模板名称")
    scenario_type: str = Field(..., description="适用场景")
    matter_type: str = Field(..., description="事项类型")
    template_content: str = Field(..., description="模板内容")
    priority: int = Field(0, description="优先级")
    is_active: bool = Field(True, description="是否启用")


class AnswerTemplateCreate(AnswerTemplateBase):
    pass


class AnswerTemplateUpdate(BaseModel):
    template_code: Optional[str] = None
    template_name: Optional[str] = None
    scenario_type: Optional[str] = None
    matter_type: Optional[str] = None
    template_content: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class AnswerTemplateResponse(AnswerTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== 查询请求相关 ====================
class QueryRequest(BaseModel):
    name: str = Field(..., description="查询姓名")
    matter_type: str = Field("干部选拔任用", description="事项类型")
    current_date: Optional[date] = Field(None, description="当前日期（默认今天）")


class SearchResult(BaseModel):
    record_type: str  # discipline/violation/petition
    name: str
    department: Optional[str]
    position: Optional[str]
    processing_org: Optional[str]
    accountability_type: Optional[str]  # 问责情况/类型
    accountability_date: Optional[date]
    has_influence_period: bool
    influence_end_date: Optional[date]
    reason: str
    status: str
    influence_status: str  # 已过影响期/尚在影响期内/不适用


class QueryResponse(BaseModel):
    query_name: str
    matter_type: str
    search_results: List[SearchResult]
    matched_template: Optional[str]
    template_code: Optional[str]
    conclusion: str
    generated_answer: str


# ==================== 操作日志相关 ====================
class OperationLogBase(BaseModel):
    module: str = Field(..., description="模块：discipline/violation/petition/template")
    action: str = Field(..., description="操作：create/update/delete")
    record_id: Optional[int] = Field(None, description="操作记录的ID")
    record_name: Optional[str] = Field(None, description="操作记录的主要内容")
    description: Optional[str] = Field(None, description="操作描述")
    operator: str = Field("系统管理员", description="操作人")


class OperationLogCreate(OperationLogBase):
    pass


class OperationLogResponse(OperationLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
