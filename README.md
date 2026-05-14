# 廉政意见智答系统

基于 FastAPI + SQLite 的廉政意见智能答复系统，用于党政机关/国企的干部廉政审查意见自动生成。系统可根据查询对象的姓名和事项类型，自动检索相关记录并匹配标准答复模板，生成规范化廉政审查意见。

## 核心功能

| 功能 | 说明 |
|------|------|
| **智能查询** | 输入姓名，自动检索违纪、违规、信访举报记录 |
| **事项类型** | 支持干部选拔任用、表彰奖励、职级晋升、交流任职等查询类型 |
| **影响期判断** | 自动计算处分影响期状态（已过/尚在/不适用） |
| **模板匹配** | 16类标准答复模板（T1-T8选拔任用，G1-G8其他查询），按优先级自动匹配 |
| **答复生成** | 动态填充变量，生成规范化答复文本 |
| **记录管理** | 违纪/违规/信访记录的增删改查 |
| **导入导出** | 支持 Excel 格式批量导入导出 |
| **操作日志** | 自动记录所有操作，支持审计追溯 |
| **数据库备份恢复** | 支持完整数据库导出备份和恢复 |
| **管理后台** | 统一管理所有数据和系统设置 |

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI + SQLAlchemy |
| 数据库 | SQLite |
| 前端 | HTML/CSS/JavaScript + Bootstrap |
| 模板引擎 | Jinja2 |
| 数据验证 | Pydantic + Pydantic-settings |
| Excel处理 | openpyxl |

## 项目结构

```
integrity_system/
├── app/
│   ├── __init__.py
│   ├── main.py                    # 应用入口
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # API路由（50+接口）
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # 配置管理
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py            # 数据库模型
│   ├── schemas/
│   │   └── __init__.py            # Pydantic模型
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
└── requirements.txt               # 依赖列表
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

## 页面功能

### 首页 - 智能查询

- **姓名查询**：输入被查询人姓名
- **事项类型选择**：
  - 干部选拔任用
  - 表彰奖励
  - 职级晋升
  - 交流任职
  - 其他
- **查询结果展示**：
  - 显示匹配的记录详情（类型、问责情况、问责时间、影响期状态）
  - 自动生成规范化答复文本
  - 支持一键复制答复内容
- **查询历史**：自动保存查询记录

### 管理后台

**数据管理**

| 模块 | 功能 |
|------|------|
| 违纪记录 | 新增、编辑、删除、导入、导出违纪处分记录 |
| 违规记录 | 新增、编辑、删除、导入、导出违规处理记录 |
| 信访举报 | 新增、编辑、删除、导入、导出信访举报记录 |
| 答复模板 | 管理智能答复模板（T1-T8、G1-G8） |

**记录字段说明**

| 表 | 字段 | 说明 |
|----|------|------|
| 违纪/违规记录 | 姓名、分公司、部门、职务 | 基本信息 |
| 违纪/违规记录 | 处理机构、问责情况/类型、问责时间 | 处分信息 |
| 违纪/违规记录 | 有无影响期、影响期截止日期 | 影响期计算 |
| 违纪/违规记录 | 事由、备注 | 详细信息 |
| 信访举报 | 姓名、分公司、部门 | 基本信息 |
| 信访举报 | 举报日期、举报内容 | 举报信息 |
| 信访举报 | 核查结果、组织是否采信 | 核查结论 |
| 信访举报 | 有无影响期、影响期截止日期、备注 | 影响期和备注 |

**系统管理**

| 功能 | 说明 |
|------|------|
| 修改密码 | 更改管理员登录密码 |
| 数据库备份 | 导出完整数据库为 .db 文件 |
| 数据库恢复 | 上传备份文件恢复数据库 |

**日志管理**

| 功能 | 说明 |
|------|------|
| 查询日志 | 查看所有查询历史记录 |
| 操作日志 | 查看用户操作记录（增删改） |

## 答复模板

### 选拔任用模板（T1-T8）

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

### 其他查询模板（G1-G8）

| 模板 | 适用场景 | 结论 |
|------|----------|------|
| G1 | 无任何违纪违规记录 | 不持异议 |
| G2 | 有举报但核查后采信本人说明 | 不持异议 |
| G3 | 有举报但核查未发现证据 | 不持异议 |
| G4 | 仅受批评教育等组织处理（已过影响期） | 不持异议 |
| G5 | 受单一处分且已过影响期 | 不持异议 |
| G6 | 受多处分开且已过影响期 | 不持异议 |
| G7 | 信访举报正在办理中 | 建议暂缓函询 |
| G8 | 尚在处分影响期内 | 建议不宜作为函询人选 |

### 模板匹配优先级

```
1. 信访举报正在办理中 → T7/G7
2. 尚在影响期内 → T8/G8
3. 举报已核查否认（采信本人说明） → T2/G2
4. 举报已核查否认（无证据） → T3/G3
5. 仅受组织处理(批评教育等) → T4/G4
6. 已过影响期的处分记录（单一） → T5/G5
7. 已过影响期的处分记录（多条） → T6/G6
8. 无记录 → T1/G1
```

## 数据库表结构

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `discipline_records` | 违纪记录 | id, name, branch_company, department, position, processing_org, accountability_type, accountability_date, has_influence_period, influence_end_date, reason, remark |
| `violation_records` | 违规记录 | id, name, branch_company, department, position, processing_org, violation_type, violation_date, has_influence_period, influence_end_date, reason, remark |
| `petition_reports` | 信访举报 | id, name, branch_company, department, report_date, report_content, verification_result, organization_adoption, has_influence_period, influence_end_date, remark |
| `answer_templates` | 答复模板 | id, template_code(T1-T8/G1-G8), template_name, scenario_type, template_type, matter_type, template_content, priority, is_active |
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
| `GET /api/export/discipline` | 导出违纪记录 Excel |
| `GET /api/export/violation` | 导出违规记录 Excel |
| `GET /api/export/petition` | 导出信访举报 Excel |
| `GET /api/export/template` | 导出答复模板 Excel |
| `POST /api/import/discipline` | 导入违纪记录 |
| `POST /api/import/violation` | 导入违规记录 |
| `POST /api/import/petition` | 导入信访举报 |
| `GET /api/template/download` | 下载导入模板 |

### 数据库管理

| 端点 | 说明 |
|------|------|
| `GET /api/backup/export` | 导出数据库备份 |
| `POST /api/backup/import` | 从备份恢复数据库 |

### 日志查询

| 端点 | 说明 |
|------|------|
| `GET /api/query/logs` | 查询历史记录 |
| `GET /api/query/{name}/history` | 某人查询历史 |
| `GET /api/operation/logs` | 操作日志列表 |
| `DELETE /api/operation/logs` | 清空操作日志 |

### 管理员

| 端点 | 说明 |
|------|------|
| `POST /api/admin/login` | 管理员登录 |
| `POST /api/admin/change-password` | 修改密码 |

## 注意事项

1. **首次启动**：自动创建数据库并初始化16个标准答复模板（T1-T8和G1-G8）
2. **管理后台**：需登录，默认账号 `admin`，密码 `admin123`
3. **操作日志**：所有增删改操作自动记录到操作日志
4. **影响期判断**：基于当前日期自动计算，多条记录时任一在影响期内优先匹配T8/G8
5. **事项类型**：查询时选择不同事项类型，会匹配对应的模板系列
6. **数据库备份**：恢复前会自动备份当前数据库到同目录

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

### 案例5：其他查询类型
- 查询姓名：xxx，事项类型=表彰奖励
- 系统会自动匹配G系列模板

## 配置说明

系统支持通过环境变量或 `.env` 文件配置：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| APP_NAME | 廉政意见智答系统 | 应用名称 |
| DEBUG | true | 调试模式 |
| HOST | 0.0.0.0 | 服务监听地址 |
| PORT | 8000 | 服务监听端口 |
| DATABASE_URL | sqlite:///./data/integrity.db | 数据库连接 |
| ADMIN_USERNAME | admin | 管理员账号 |
| ADMIN_PASSWORD | admin123 | 管理员密码 |
