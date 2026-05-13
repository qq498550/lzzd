# 廉政意见智答系统

## 系统概述

基于 FastAPI + SQLite 的廉政意见智能答复系统，实现违纪违规记录检索、影响期自动判断、标准模板匹配和智能答复生成。

## 功能特性

### 核心功能
- **智能查询**：输入姓名和事项类型，自动检索违纪、违规、信访记录
- **影响期判断**：自动计算处分影响期状态（已过/尚在/不适用）
- **模板匹配**：8类标准答复模板，按优先级自动匹配
- **答复生成**：动态填充变量，生成规范化答复文本
- **空记录提示**：查询姓名不存在时，返回"查询结果为空，请确认输入是否正确"

### 管理后台
- **数据概览**：统计卡片展示各类型记录数量、今日查询数，查询记录表格展示所有历史查询
- **记录管理**：违纪记录、违规记录、信访举报、答复模板的增删改查
- **操作日志**：自动记录所有增删改操作，支持查看和清空
- **数据导入导出**：支持CSV格式批量导入导出
- **登录验证**：管理员账号密码保护（默认：admin/admin123）
- **密码修改**：支持修改管理员密码

### 安全特性
- 管理后台登录验证
- 操作日志全程记录

## 技术栈

- **后端**：FastAPI + SQLAlchemy + SQLite
- **前端**：原生 HTML/CSS/JavaScript + Bootstrap
- **模板引擎**：Jinja2
- **数据验证**：Pydantic

## 项目结构

```
integrity_system/
├── app/
│   ├── api/
│   │   └── routes.py          # API路由
│   ├── core/                   # 核心配置
│   ├── models/
│   │   └── database.py        # 数据库模型
│   ├── schemas/
│   │   └── __init__.py        # Pydantic模型
│   ├── services/
│   │   └── integrity_service.py  # 核心业务逻辑
│   ├── static/                # 静态文件
│   ├── templates/
│   │   ├── index.html         # 查询首页
│   │   └── admin.html         # 管理后台
│   └── main.py                # 应用入口
├── data/                      # 数据库文件
└── requirements.txt           # 依赖列表
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
cd integrity_system
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问系统

- **查询首页**：http://localhost:8000/
- **管理后台**：http://localhost:8000/admin（默认账号：admin，密码：admin123）
- **API文档**：http://localhost:8000/docs

## API接口

### 智能查询
```bash
POST /api/query/
{
    "name": "张三",
    "matter_type": "干部选拔任用",
    "current_date": "2026-05-11"  # 可选
}
```

### 数据管理
- `GET/POST /api/discipline/` - 违纪记录
- `GET/POST /api/violation/` - 违规记录
- `GET/POST /api/petition/` - 信访举报
- `GET/POST /api/template/` - 答复模板

### 查询历史
```bash
GET /api/query/logs
```

### 操作日志
```bash
GET /api/operation/logs     # 获取操作日志
DELETE /api/operation/logs   # 清空操作日志
```

### 管理员接口
```bash
POST /api/admin/login               # 管理员登录
POST /api/admin/change-password      # 修改管理员密码
```

## 答复模板说明

| 模板编号 | 适用场景 | 结论 |
|---------|---------|------|
| T1 | 无任何记录 | 不持异议 |
| T2 | 有举报但核查后采信本人说明 | 不持异议 |
| T3 | 有举报但核查未发现证据 | 不持异议 |
| T4 | 仅受批评教育等组织处理（已过影响期） | 不持异议 |
| T5/T6 | 受处分且已过影响期 | 不持异议 |
| T7 | 信访举报正在办理中 | 建议暂缓提拔 |
| T8 | 尚在处分影响期内 | 建议不宜作为拟提拔人选 |

## 数据库表结构

### OperationLog（操作日志）
| 字段 | 类型 | 说明 |
|-----|------|------|
| id | Integer | 主键 |
| module | String | 模块名称 |
| action | String | 操作类型（创建/修改/删除） |
| record_id | Integer | 关联记录ID |
| record_name | String | 记录名称 |
| description | String | 操作描述 |
| operator | String | 操作人 |
| created_at | DateTime | 创建时间 |

### QueryLog（查询日志）
| 字段 | 类型 | 说明 |
|-----|------|------|
| id | Integer | 主键 |
| query_name | String | 查询姓名 |
| matter_type | String | 事项类型 |
| result_template | String | 匹配模板 |
| conclusion | String | 查询结论 |
| query_time | DateTime | 查询时间 |

## 示例数据

系统启动时会自动初始化8个标准答复模板。可通过管理后台添加测试数据：

### 测试案例1：无记录
- 查询姓名：李明（数据库中不存在）
- 预期结果：**查询结果为空，请确认输入是否正确。**

### 测试案例2：已过影响期
- 添加违纪记录：王五，警告处分，2025-04-13，影响期截止2026-01-01
- 查询姓名：王五
- 预期结果：模板T6，不持异议

### 测试案例3：尚在影响期
- 添加违纪记录：张三，记过处分，2026-01-01，影响期截止2027-01-01
- 查询姓名：张三
- 预期结果：模板T8，建议不宜作为拟提拔人选

### 测试案例4：正在办理
- 添加信访举报：赵六，状态：办理中
- 查询姓名：赵六
- 预期结果：模板T7，建议暂缓提拔

## 注意事项

1. 首次启动会自动创建SQLite数据库并初始化模板数据
2. 数据库文件位于 `data/integrity.db`
3. 管理后台需要登录，默认账号：`admin`，密码：`admin123`
4. 所有增删改操作会自动记录到操作日志
5. 影响期判断基于当前日期（可手动指定）
6. 多条记录时，任一记录尚在影响期内则优先匹配T8模板