# 廉政意见智答系统

基于 FastAPI + SQLite 的廉政意见智能答复系统，用于党政机关/国企的干部廉政审查意见生成。

## 核心功能

| 功能 | 说明 |
|------|------|
| 智能查询 | 输入姓名，自动检索违纪、违规、信访举报记录 |
| 影响期判断 | 自动计算处分影响期状态（已过/尚在/不适用） |
| 模板匹配 | 8类标准答复模板，按优先级自动匹配 |
| 答复生成 | 动态填充变量，生成规范化答复文本 |
| 记录管理 | 违纪/违规/信访记录的增删改查 |
| 导入导出 | 支持 Excel 格式批量导入导出 |
| 操作日志 | 自动记录所有操作，支持审计追溯 |

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI + SQLAlchemy |
| 数据库 | SQLite |
| 前端 | HTML/CSS/JavaScript + Bootstrap |
| 模板引擎 | Jinja2 |
| 数据验证 | Pydantic + Pydantic-settings |

## 项目结构

```
integrity_system/
├── app/
│   ├── __init__.py
│   ├── main.py                    # 应用入口
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # API路由 (52KB)
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # 配置管理
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py            # 数据库模型
│   ├── schemas/
│   │   ├── __init__.py           # Pydantic模型
│   │   ├── discipline_template.xlsx
│   │   ├── petition_template.xlsx
│   │   └── violation_template.xlsx
│   ├── services/
│   │   ├── __init__.py
│   │   └── integrity_service.py   # 核心业务逻辑
│   ├── static/
│   │   └── cnpc.png               # Logo
│   └── templates/
│       ├── index.html             # 查询首页
│       └── admin.html             # 管理后台
├── data/
│   └── integrity.db               # SQLite数据库
├── generate_templates.py          # 模板生成脚本
└── requirements.txt              # 依赖列表
```

## 快速开始

### 1. 安装依赖

```bash
cd integrity_system
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问系统

| 地址 | 说明 |
|------|------|
| http://localhost:8000/ | 查询首页 |
| http://localhost:8000/admin | 管理后台 |
| http://localhost:8000/docs | Swagger API文档 |

**默认账号**: `admin` / `admin123`

## 答复模板

| 模板 | 适用场景 | 结论 |
|------|----------|------|
| T1 | 无任何违纪违规记录 | 不持异议 |
| T2 | 有举报但核查后采信本人说明 | 不持异议 |
| T3 | 有举报但核查未发现证据 | 不持异议 |
| T4 | 仅受批评教育等组织处理（已过影响期） | 不持异议 |
| T5 | 受单一处分且已过影响期 | 不持异议 |
| T6 | 受多处分开且已过影响期 | 不持异议 |
| T7 | 信访举报正在办理中 | 建议暂缓提拔 |
| T8 | 尚在处分影响期内 | 建议不宜作为拟提拔人选 |

### 模板匹配优先级

```
1. 信访举报正在办理中 → T7
2. 尚在影响期内 → T8
3. 举报已核查否认 → T2/T3
4. 仅受组织处理(批评教育等) → T4
5. 已过影响期的处分记录 → T5/T6
6. 无记录 → T1
```

## 数据库表结构

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `discipline_records` | 违纪记录 | id, name, branch_company, department, position, accountability_type, accountability_date, has_influence_period, influence_end_date, reason, status |
| `violation_records` | 违规记录 | id, name, branch_company, department, position, violation_type, violation_date, has_influence_period, influence_end_date, reason, status |
| `petition_reports` | 信访举报 | id, name, branch_company, department, report_date, report_content, verification_result, organization_adoption, has_influence_period, influence_end_date, status |
| `answer_templates` | 答复模板 | id, template_code(T1-T8), template_name, scenario_type, matter_type, template_content, priority, is_active |
| `query_logs` | 查询日志 | id, query_name, matter_type, result_template, conclusion, query_time, operator |
| `operation_logs` | 操作日志 | id, module, action, record_id, record_name, description, operator, created_at |

## API 接口

### 智能查询
```bash
POST /api/query/
{
    "name": "张三",
    "matter_type": "干部选拔任用"
}
```

### 记录管理
| 方法 | 端点 | 说明 |
|------|------|------|
| GET/POST | `/api/discipline/` | 违纪记录列表/创建 |
| GET/PUT/DELETE | `/api/discipline/{id}` | 单条记录操作 |
| GET/POST | `/api/violation/` | 违规记录列表/创建 |
| GET/PUT/DELETE | `/api/violation/{id}` | 单条记录操作 |
| GET/POST | `/api/petition/` | 信访举报列表/创建 |
| GET/PUT/DELETE | `/api/petition/{id}` | 单条记录操作 |
| GET/POST | `/api/template/` | 答复模板列表/创建 |
| GET/PUT/DELETE | `/api/template/{id}` | 单条模板操作 |

### 数据导入导出
| 端点 | 说明 |
|------|------|
| `GET /api/export/{type}` | 导出 Excel (discipline/violation/petition/template) |
| `POST /api/import/{type}` | 导入记录 |
| `GET /api/template/download` | 下载导入模板 |

### 其他接口
| 端点 | 说明 |
|------|------|
| `GET /api/query/logs` | 查询历史 |
| `GET /api/query/{name}/history` | 某人查询历史 |
| `GET /api/operation/logs` | 操作日志 |
| `POST /api/admin/login` | 管理员登录 |
| `POST /api/admin/change-password` | 修改密码 |

## 注意事项

1. 首次启动自动创建数据库并初始化8个标准答复模板
2. 管理后台需登录，默认账号 `admin`，密码 `admin123`
3. 所有增删改操作自动记录到操作日志
4. 影响期判断基于当前日期，多条记录时任一在影响期内优先匹配T8

## 测试案例

### 案例1：无记录
- 查询姓名：数据库中不存在
- 结果：**查询结果为空，请确认输入是否正确**

### 案例2：已过影响期
- 添加违纪记录：警告处分，影响期截止2026-01-01
- 查询姓名：xxx
- 结果：模板T6，不持异议

### 案例3：尚在影响期
- 添加违纪记录：记过处分，影响期截止2027-01-01
- 查询姓名：xxx
- 结果：模板T8，建议不宜作为拟提拔人选

### 案例4：正在办理
- 添加信访举报：状态=办理中
- 查询姓名：xxx
- 结果：模板T7，建议暂缓提拔
