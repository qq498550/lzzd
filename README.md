# 廉政意见智答系统 (Integrity Answer System)

一个基于 FastAPI + SQLite 的廉政意见智能答复系统，实现违纪违规记录检索、影响期自动判断、标准模板匹配和智能答复生成。

## 📋 目录

- [系统概述](#系统概述)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [API 接口](#api-接口)
- [答复模板说明](#答复模板说明)
- [使用示例](#使用示例)
- [注意事项](#注意事项)
- [扩展建议](#扩展建议)

## 系统概述

本系统专为组织人事部门设计，用于在干部选拔任用、评优评先等场景中，快速生成规范化的廉政意见答复。系统通过智能检索违纪、违规、信访记录，自动判断处分影响期状态，并匹配相应的标准答复模板，大幅提高工作效率和答复规范性。

## 功能特性

### 核心功能
- **智能查询**：输入姓名和事项类型，自动检索违纪、违规、信访记录
- **影响期判断**：自动计算处分影响期状态（已过/尚在/不适用）
- **模板匹配**：8 类标准答复模板，按优先级自动匹配
- **答复生成**：动态填充变量，生成规范化答复文本
- **查询历史**：记录每次查询操作，支持追溯查看

### 管理后台
- 📊 **数据概览仪表板**：实时展示各类数据统计
- 👤 **违纪记录管理**：增删改查违纪处分信息
- 📝 **违规记录管理**：增删改查违规处理信息
- 📬 **信访举报管理**：增删改查信访举报及核查情况
- 📄 **答复模板管理**：自定义维护答复模板
- 📜 **查询日志查看**：追踪所有查询操作记录

## 技术栈

| 组件 | 技术选型 |
|------|----------|
| **后端框架** | FastAPI >= 0.100.0 |
| **ASGI 服务器** | Uvicorn >= 0.23.0 |
| **ORM** | SQLAlchemy >= 2.0.0 |
| **数据库** | SQLite |
| **数据验证** | Pydantic >= 2.0.0 |
| **模板引擎** | Jinja2 >= 3.1.0 |
| **前端** | HTML5 + CSS3 + 原生 JavaScript |
| **数据处理** | Pandas + OpenPyXL |

## 项目结构

```
integrity_system/
├── app/
│   ├── api/
│   │   └── routes.py          # API 路由定义
│   ├── core/
│   │   └── config.py          # 应用配置管理
│   ├── models/
│   │   └── database.py        # 数据库模型定义
│   ├── schemas/
│   │   └── __init__.py        # Pydantic 数据模型
│   ├── services/
│   │   └── integrity_service.py  # 核心业务逻辑
│   ├── templates/
│   │   ├── index.html         # 查询首页
│   │   └── admin.html         # 管理后台
│   ├── data/
│   │   └── integrity.db       # SQLite 数据库文件
│   └── main.py                # 应用入口
├── requirements.txt           # Python 依赖列表
└── README.md                  # 项目文档
```

## 快速开始

### 1. 环境要求

- Python >= 3.8
- pip 包管理器

### 2. 安装依赖

```bash
cd integrity_system
pip install -r requirements.txt
```

### 3. 启动服务

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问系统

服务启动后，可通过以下地址访问：

| 页面 | URL |
|------|-----|
| 🏠 查询首页 | http://localhost:8000/ |
| ⚙️ 管理后台 | http://localhost:8000/admin |
| 📖 API 文档 | http://localhost:8000/docs |
| 🔍 ReDoc 文档 | http://localhost:8000/redoc |

## API 接口

### 智能查询

**请求**
```bash
POST /api/query/
Content-Type: application/json

{
    "name": "张三",
    "matter_type": "干部选拔任用",
    "current_date": "2026-05-11"  // 可选，默认为当前日期
}
```

**响应**
```json
{
    "name": "张三",
    "matter_type": "干部选拔任用",
    "has_records": true,
    "template_code": "T8",
    "template_name": "处分影响期内模板",
    "conclusion": "建议不宜作为拟提拔人选",
    "answer_text": "经审核，张三同志于 2026-01-01 因违反工作纪律受到记过处分（尚在影响期内）。建议不宜作为拟干部选拔任用人选。",
    "records": {
        "discipline": [...],
        "violation": [...],
        "petition": [...]
    }
}
```

### 数据管理接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/discipline/` | GET/POST | 违纪记录管理 |
| `/api/discipline/{id}` | GET/PUT/DELETE | 单条违纪记录操作 |
| `/api/violation/` | GET/POST | 违规记录管理 |
| `/api/violation/{id}` | GET/PUT/DELETE | 单条违规记录操作 |
| `/api/petition/` | GET/POST | 信访举报管理 |
| `/api/petition/{id}` | GET/PUT/DELETE | 单条信访记录操作 |
| `/api/template/` | GET/POST | 答复模板管理 |
| `/api/template/{id}` | GET/PUT/DELETE | 单个模板操作 |

### 查询历史

```bash
GET /api/query/{name}/history
```

## 答复模板说明

系统内置 8 个标准答复模板，按优先级自动匹配：

| 模板编号 | 模板名称 | 适用场景 | 结论 |
|---------|---------|---------|------|
| T1 | 无记录模板 | 无任何违纪违规记录 | 不持异议 |
| T2 | 举报查否模板 | 有举报但核查后采信本人说明 | 不持异议 |
| T3 | 举报无证据模板 | 有举报但核查未发现证据 | 不持异议 |
| T4 | 组织处理模板 | 仅受批评教育等组织处理（已过影响期） | 不持异议 |
| T5 | 轻处分已过影响期模板 | 警告/严重警告处分且已过影响期 | 不持异议 |
| T6 | 重处分已过影响期模板 | 撤职/留用察看/开除处分且已过影响期 | 不持异议 |
| T7 | 正在办理模板 | 信访举报正在办理中 | 建议暂缓提拔 |
| T8 | 处分影响期内模板 | 尚在处分影响期内 | 建议不宜作为拟提拔人选 |

**匹配规则**：
1. 优先检查是否有正在办理的信访举报（T7）
2. 其次检查是否尚在处分影响期内（T8）
3. 再根据处分类型和影响期状态匹配 T4-T6
4. 最后匹配无记录或查否情况（T1-T3）

## 使用示例

### 示例 1：查询无记录人员

```bash
curl -X POST "http://localhost:8000/api/query/" \
  -H "Content-Type: application/json" \
  -d '{"name": "李明", "matter_type": "干部选拔任用"}'
```

**预期结果**：模板 T1，结论"不持异议"

### 示例 2：查询已过影响期人员

1. 先添加一条违纪记录：
```bash
curl -X POST "http://localhost:8000/api/discipline/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "王五",
    "punishment_type": "警告",
    "reason": "违反工作纪律",
    "punishment_date": "2025-04-13",
    "influence_end_date": "2026-01-01"
  }'
```

2. 查询该人员（当前日期晚于影响期截止日）：
```bash
curl -X POST "http://localhost:8000/api/query/" \
  -H "Content-Type: application/json" \
  -d '{"name": "王五", "matter_type": "干部选拔任用", "current_date": "2026-05-11"}'
```

**预期结果**：模板 T5/T6，结论"不持异议"

### 示例 3：查询尚在影响期人员

```bash
curl -X POST "http://localhost:8000/api/discipline/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张三",
    "punishment_type": "记过",
    "reason": "违反廉洁纪律",
    "punishment_date": "2026-01-01",
    "influence_end_date": "2027-01-01"
  }'
```

查询时（当前日期在影响期内）：
```bash
curl -X POST "http://localhost:8000/api/query/" \
  -H "Content-Type: application/json" \
  -d '{"name": "张三", "matter_type": "干部选拔任用"}'
```

**预期结果**：模板 T8，结论"建议不宜作为拟提拔人选"

### 示例 4：查询正在办理信访举报人员

```bash
curl -X POST "http://localhost:8000/api/petition/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "赵六",
    "report_content": "反映收受礼金问题",
    "status": "办理中",
    "receive_date": "2026-04-01"
  }'
```

**预期结果**：模板 T7，结论"建议暂缓提拔"

## 注意事项

1. **首次启动**：系统会自动创建 SQLite 数据库并初始化 8 个标准答复模板
2. **数据库位置**：数据库文件位于 `app/data/integrity.db`
3. **模糊查询**：支持姓名模糊匹配查询
4. **影响期判断**：基于当前日期自动判断，也可手动指定日期进行历史回溯
5. **多记录处理**：当存在多条记录时，任一记录尚在影响期内则优先匹配 T8 模板
6. **数据备份**：定期备份 `app/data/integrity.db` 文件以防数据丢失

## 扩展建议

- 📥 **批量导入**：对接 Excel 文件批量导入历史数据
- 🔐 **权限管理**：增加用户登录和角色权限控制
- ⚙️ **配置化**：支持更多事项类型的动态配置
- 📄 **PDF 导出**：生成正式 PDF 格式答复函
- 🔗 **系统集成**：对接组织人事系统 API
- 📊 **统计分析**：增加数据分析和可视化报表
- 🔔 **消息通知**：重要事项提醒和通知功能

## 许可证

本项目仅供内部使用，未经授权不得外传。

## 联系方式

如有问题或建议，请联系系统管理员。