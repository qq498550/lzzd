"""
廉政意见智答系统 - 主应用入口
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import os

from app.core.config import settings
from app.models.database import init_db, get_db, AnswerTemplate, SessionLocal
from app.api.routes import router


def initialize_default_templates(db: Session) -> None:
    """初始化默认答复模板"""
    
    default_templates = [
        {
            "template_code": "T1",
            "template_name": "无记录模板",
            "scenario_type": "无任何违纪违规记录",
            "matter_type": "干部选拔任用",
            "template_content": "经审核，未收到过{person_name}同志的信访举报。对{person_name}同志作为拟{matter_type}人选不持异议。",
            "priority": 1
        },
        {
            "template_code": "T2",
            "template_name": "举报查否模板",
            "scenario_type": "有举报但核查后采信本人说明",
            "matter_type": "干部选拔任用",
            "template_content": "经审核，收到反映{person_name}同志的信访举报，已核查完毕并采信本人说明。对{person_name}同志作为拟{matter_type}人选不持异议。",
            "priority": 2
        },
        {
            "template_code": "T3",
            "template_name": "举报无证据模板",
            "scenario_type": "有举报但核查未发现证据",
            "matter_type": "干部选拔任用",
            "template_content": "经审核，收到反映{person_name}同志的信访举报，经核查未发现相关证据。对{person_name}同志作为拟{matter_type}人选不持异议。",
            "priority": 3
        },
        {
            "template_code": "T4",
            "template_name": "组织处理模板",
            "scenario_type": "仅受批评教育等组织处理",
            "matter_type": "干部选拔任用",
            "template_content": "经审核，{person_name}同志于{date}因{reason}受到{type}处理（已过影响期）。对{person_name}同志作为拟{matter_type}人选不持异议。",
            "priority": 4
        },
        {
            "template_code": "T5",
            "template_name": "已过影响期模板（单一）",
            "scenario_type": "受处分且已过影响期",
            "matter_type": "干部选拔任用",
            "template_content": "经审核，未收到过{person_name}同志的信访举报。此外，{date}{person_name}同志因{reason}问题，受到{type}处分（已过影响期）。对{person_name}同志作为拟{matter_type}人选不持异议。",
            "priority": 5
        },
        {
            "template_code": "T6",
            "template_name": "已过影响期模板（多条）",
            "scenario_type": "受多处分开已过影响期",
            "matter_type": "干部选拔任用",
            "template_content": "经审核，未收到过{person_name}同志的信访举报。此外，{date}{person_name}同志因{reason}问题，受到{type}处分（已过影响期）。对{person_name}同志作为拟{matter_type}人选不持异议。",
            "priority": 6
        },
        {
            "template_code": "T7",
            "template_name": "正在办理模板",
            "scenario_type": "信访举报正在办理中",
            "matter_type": "干部选拔任用",
            "template_content": "经审核，目前收到反映{person_name}同志的信访举报正在办理中，建议暂缓{matter_type}。",
            "priority": 7
        },
        {
            "template_code": "T8",
            "template_name": "影响期内模板",
            "scenario_type": "尚在处分影响期内",
            "matter_type": "干部选拔任用",
            "template_content": "经审核，{person_name}同志于{date}因{reason}问题，受到{type}处分（尚在影响期内），建议不宜作为拟{matter_type}人选。",
            "priority": 8
        }
    ]
    
    for tpl in default_templates:
        existing = db.query(AnswerTemplate).filter(
            AnswerTemplate.template_code == tpl["template_code"]
        ).first()
        if not existing:
            db_template = AnswerTemplate(**tpl, is_active=True)
            db.add(db_template)
    
    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    init_db()
    
    # 确保数据目录存在
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    
    # 初始化默认模板数据
    db = SessionLocal()
    try:
        initialize_default_templates(db)
    finally:
        db.close()
    
    yield


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# 确保静态文件和模板目录存在
os.makedirs(settings.STATIC_DIR, exist_ok=True)
os.makedirs(settings.TEMPLATES_DIR, exist_ok=True)

# 挂载静态文件和模板引擎
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

# 注册 API 路由
app.include_router(router, prefix="/api")


@app.get("/", response_class=HTMLResponse, tags=["前端页面"])
async def home(request: Request):
    """首页 - 查询界面"""
    return templates.TemplateResponse(name="index.html", context={"request": request})


@app.get("/admin", response_class=HTMLResponse, tags=["前端页面"])
async def admin_panel(request: Request):
    """管理后台"""
    return templates.TemplateResponse(name="admin.html", context={"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
