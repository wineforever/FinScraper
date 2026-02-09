# FinScraper

<div align="center">

  ![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
  ![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green.svg)
  ![License](https://img.shields.io/badge/License-MIT-yellow.svg)
  ![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

  财务报告抓取与批量下载工具 · Web UI + Python 后端

  [English](#english) | [概述](#概述) | [功能特性](#功能特性) | [快速开始](#快速开始) | [API文档](#api文档) | [详细使用指南](#详细使用指南) | [项目结构](#项目结构) | [开发指南](#开发指南) | [故障排除](#故障排除) | [贡献指南](#贡献指南) | [法律与合规](#法律与合规) | [支持与联系](#支持与联系)

</div>

---

## 📋 概述

FinScraper 是一个基于 Web 的财务报告抓取与批量下载工具，专门用于从新浪财经抓取上市公司财务报告（年报、季报、中报等）并直接下载为 PDF 格式。工具提供简洁美观的 Web 界面，支持股票代码/名称自动解析、多种报告类型筛选、按年份过滤以及单个/批量下载功能。

### 🎯 核心特性

- **智能股票解析** - 支持股票代码（如 `603325`）或名称（如 `浦发银行`）自动识别
- **多报告类型** - 年报、一季报、中报、三季报、全部类型筛选
- **年份过滤** - 按报告年份精确筛选（优先标题中的年份，回退公告日期年份）
- **批量操作** - 一键批量下载选中报告，支持浏览器多文件下载
- **直接输出** - 直接下载 PDF 格式报告，无需中间转换
- **现代化 UI** - 响应式设计，支持移动端，简洁美观的界面
- **API 支持** - 提供 RESTful API 接口，支持集成到其他系统

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- pip（Python 包管理器）
- 网络连接（用于访问新浪财经数据源）

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/yourusername/finscraper.git
   cd finscraper
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/macOS
   source .venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **启动服务**
   ```bash
   python app.py
   ```

5. **访问应用**
   打开浏览器，访问：`http://127.0.0.1:8000`

### 验证安装
启动服务后，可以通过以下方式验证安装是否成功：

1. **检查服务状态**
   ```bash
   # 检查服务是否运行
   curl http://127.0.0.1:8000/api/reports?query=000001&report_type=ndbg
   ```
   正常响应应返回JSON格式的股票信息或错误提示。

2. **访问Web界面**
   - 打开浏览器访问 `http://127.0.0.1:8000`
   - 应显示FinScraper的Web界面
   - 界面应包含搜索表单和说明文字

3. **停止服务**
   在运行服务的终端中按 `Ctrl+C` 即可停止服务。

### 配置选项
如果需要修改默认配置，可以直接编辑 `app.py` 文件：

1. **修改服务端口**
   ```python
   # 在 app.py 文件末尾修改
   uvicorn.run(app, host="127.0.0.1", port=8000)  # 修改端口号
   ```

2. **修改超时设置**
   ```python
   # 在 fetch_report_list 等函数中修改 timeout 参数
   resp = requests.get(url, headers=HEADERS, timeout=20)  # 修改超时时间
   ```

3. **修改用户代理**
   ```python
   # 在 HEADERS 字典中修改 User-Agent
   HEADERS = {
       "User-Agent": "Mozilla/5.0 ...",  # 修改为需要的User-Agent
   }
   ```

### 📸 界面预览

![image-20260209194630255](.\preview.PNG)

**主界面**：简洁的搜索表单，包含股票代码输入、报告类型选择和年份过滤。

**结果列表**：表格形式展示抓取到的报告，支持复选框选择和单个/批量下载。

## ⚙️ 功能特性

### 搜索与筛选
- **股票智能识别**：自动解析股票代码和名称，支持模糊匹配
- **报告类型**：年报 (`ndbg`)、一季报 (`yjdbg`)、中报 (`zqbg`)、三季报 (`sjdbg`)、全部类型 (`all`)
- **年份筛选**：支持 2000 年至今的年份过滤
- **实时状态**：显示抓取进度和结果统计

### 下载功能
- **单个下载**：点击单条报告的下载按钮直接获取 PDF
- **批量下载**：勾选多个报告后批量下载，自动处理浏览器多文件下载提示
- **文件名优化**：自动清理非法字符，生成规范的文件名
- **下载队列**：批量下载时自动排队，避免浏览器阻塞

### 技术特性
- **异步处理**：API 请求异步处理，提高响应速度
- **缓存机制**：PDF 链接缓存，避免重复请求
- **错误处理**：完善的错误处理和用户友好提示
- **编码兼容**：自动处理 GBK/GB18030 编码，支持中文内容

## 📖 详细使用指南

### 基本使用流程

1. **输入股票信息**
   - 在搜索框中输入股票代码（6位数字）或股票名称
   - 示例：`603325` 或 `浦发银行`

2. **选择报告类型**
   - 从下拉菜单中选择需要的报告类型
   - 可选：全部类型、年报、一季报、中报、三季报

3. **选择年份（可选）**
   - 如果需要特定年份的报告，从年份下拉菜单中选择
   - 留空则显示所有年份的报告

4. **开始抓取**
   - 点击"开始抓取"按钮，系统将获取符合条件的报告列表
   - 抓取过程中会显示实时状态

5. **下载报告**
   - **单个下载**：点击每条报告右侧的"下载"按钮
   - **批量下载**：勾选需要下载的报告（默认全选），点击"批量下载选中"按钮

### 注意事项

- **浏览器设置**：批量下载时，浏览器可能会提示"是否允许下载多个文件"，请选择"允许"
- **网络稳定性**：数据源依赖新浪财经，网络不稳定时可能抓取失败
- **数据更新**：报告列表依赖新浪财经的历史数据更新频率

## 🔧 API 文档

FinScraper 提供 RESTful API 接口，支持程序化访问。

### 基础信息
- **Base URL**: `http://127.0.0.1:8000`
- **Content-Type**: `application/json`
- **响应格式**: JSON

### 端点说明

#### 1. 获取报告列表
```
GET /api/reports
```

**查询参数**：
- `query` (必填) - 股票代码或名称
- `report_type` (必填) - 报告类型 (`ndbg`, `yjdbg`, `zqbg`, `sjdbg`, `all`)
- `year` (可选) - 年份过滤，如 `2024`

**示例请求**：
```bash
curl "http://127.0.0.1:8000/api/reports?query=603325&report_type=ndbg&year=2024"
```

**响应示例**：
```json
{
  "stock_id": "603325",
  "stock_name": "浦发银行",
  "report_type": "ndbg",
  "report_type_label": "年报",
  "year": 2024,
  "reports": [
    {
      "id": "10989480",
      "title": "2024年年度报告",
      "date": "2024-04-30",
      "detail_url": "https://vip.stock.finance.sina.com.cn/...",
      "report_year": "2024"
    }
  ]
}
```

#### 2. 下载报告 PDF
```
GET /api/report/pdf
```

**查询参数**：
- `stock_id` (必填) - 股票代码（6位数字）
- `bulletin_id` (必填) - 公告ID（从报告列表获取）
- `title` (可选) - 文件名，用于生成下载的文件名

**示例请求**：
```bash
curl -O -J "http://127.0.0.1:8000/api/report/pdf?stock_id=603325&bulletin_id=10989480&title=2024年年度报告"
```

**响应**：
- 直接返回 PDF 文件流
- 自动设置 `Content-Disposition` 头部，指定下载文件名

### 使用示例

#### Python 示例
```python
import requests

# 1. 获取报告列表
base_url = "http://127.0.0.1:8000"
response = requests.get(
    f"{base_url}/api/reports",
    params={
        "query": "603325",
        "report_type": "ndbg",
        "year": 2024
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"找到 {len(data['reports'])} 份报告")
    for report in data["reports"]:
        print(f"- {report['date']} {report['title']}")
else:
    print(f"错误: {response.status_code} - {response.text}")

# 2. 下载报告PDF
if data["reports"]:
    report = data["reports"][0]
    pdf_response = requests.get(
        f"{base_url}/api/report/pdf",
        params={
            "stock_id": data["stock_id"],
            "bulletin_id": report["id"],
            "title": report["title"]
        },
        stream=True
    )
    
    if pdf_response.status_code == 200:
        filename = report["title"].replace("/", "_") + ".pdf"
        with open(filename, "wb") as f:
            for chunk in pdf_response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"已下载: {filename}")
    else:
        print(f"下载失败: {pdf_response.status_code}")
```

#### JavaScript 示例
```javascript
// 获取报告列表
async function fetchReports() {
    const response = await fetch(
        'http://127.0.0.1:8000/api/reports?query=603325&report_type=ndbg&year=2024'
    );
    const data = await response.json();
    console.log('报告列表:', data);
    return data;
}

// 下载单个报告
async function downloadReport(stockId, bulletinId, title) {
    const params = new URLSearchParams({
        stock_id: stockId,
        bulletin_id: bulletinId,
        title: title
    });
    const url = `http://127.0.0.1:8000/api/report/pdf?${params.toString()}`;
    
    const link = document.createElement('a');
    link.href = url;
    link.download = '';
    link.click();
}
```

### 速率限制
当前版本未实施严格的速率限制，但建议：
- 避免高频请求（每秒不超过1-2个请求）
- 批量下载时添加适当延迟（如400毫秒）
- 尊重数据源（新浪财经）的服务条款

### 错误处理

| 状态码 | 错误信息 | 说明 |
|--------|----------|------|
| 400 | 股票代码格式错误 | `stock_id` 不是6位数字 |
| 400 | 报告类型不能为空 | `report_type` 参数缺失 |
| 400 | 不支持的报告类型 | `report_type` 参数值无效 |
| 404 | 未找到匹配的股票 | 股票代码或名称无法识别 |
| 404 | 未找到PDF链接 | 报告详情页中未找到PDF下载链接 |
| 500 | 服务器内部错误 | 后端处理异常 |

## 🏗️ 项目结构

```
FinScraper/
├── app.py              # 主应用程序文件（FastAPI后端）
├── requirements.txt    # Python依赖列表
├── README.md          # 项目说明文档
└── web/               # 前端文件目录
    ├── index.html     # 主页面HTML
    ├── styles.css     # 样式表
    └── app.js         # 前端JavaScript逻辑
```

### 文件说明

- **app.py**：FastAPI 应用程序，包含所有业务逻辑和 API 端点
  - 股票代码解析和验证
  - 新浪财经数据抓取和处理
  - PDF 链接提取和缓存
  - API 端点定义和错误处理

- **web/index.html**：Web 界面主页面
  - 响应式布局设计
  - 搜索表单和结果表格
  - 与后端 API 的交互接口

- **web/styles.css**：CSS 样式表
  - 现代化 UI 设计
  - 动画效果和过渡
  - 移动端适配

- **web/app.js**：前端 JavaScript
  - 表单提交和验证
  - API 调用和数据绑定
  - 批量下载处理逻辑

## 🔨 开发指南

### 环境设置

1. **安装开发依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **代码风格**
   - 遵循 PEP 8 Python 代码风格指南
   - 使用类型注解（Type Hints）
   - 保持函数和方法简洁（不超过50行）

3. **运行测试**
   ```bash
   # 启动开发服务器
   python app.py
   
   # 访问 http://127.0.0.1:8000 进行手动测试
   ```

### 添加新功能

1. **添加新的报告类型**
   - 在 `REPORT_TYPE_MAP` 和 `REPORT_TYPE_LABEL` 字典中添加映射
   - 在 `REPORT_LIST_ROUTE` 中添加对应的路由配置
   - 更新前端选择框选项

2. **修改数据源**
   - 修改 `LIST_BASE_URL` 和 `DETAIL_BASE_URL`
   - 调整 HTML 解析逻辑以适应新的页面结构

3. **增强错误处理**
   - 在相应的函数中添加 try-catch 块
   - 提供更详细的错误信息和用户提示

## 🐛 故障排除

### 新手注意事项

以下是新用户使用时容易遇到的问题和解决方案：

1. **浏览器阻止批量下载**
   - 现象：批量下载时浏览器提示"是否允许下载多个文件"
   - 解决方案：在浏览器提示中选择"允许"或"允许下载多个文件"
   - 预防：可在浏览器设置中开启"自动下载多个文件"权限

2. **股票名称搜索不准确**
   - 现象：输入股票名称时可能匹配到指数、基金等非目标结果
   - 解决方案：优先使用6位股票代码进行搜索，准确性更高
   - 示例：使用 `603325` 而非 `浦发银行`

3. **年份筛选逻辑说明**
   - 筛选基于报告标题中的年份（如"2024年年度报告"）
   - 如果标题无年份，则使用公告日期年份
   - 注意：报告年份不一定等于公告发布日期年份

4. **抓取失败或列表为空**
   - 可能原因：新浪财经数据源暂时不可用、网络问题、编码异常
   - 解决方案：稍后重试，检查网络连接，或尝试其他股票代码
   - 临时方案：直接访问新浪财经官网验证数据可用性

5. **报告类型说明**
   - `ndbg`：年报（年度报告）
   - `yjdbg`：一季报（第一季度报告）
   - `zqbg`：中报/半年报（中期报告）
   - `sjdbg`：三季报（第三季度报告）
   - `all`：全部类型

### 常见问题

#### Q1: 批量下载时浏览器阻止多文件下载
**解决方案**：在浏览器弹出的下载提示中，选择"允许下载多个文件"。不同浏览器的设置位置：
- Chrome：设置 → 隐私和安全 → 网站设置 → 更多内容设置 → 自动下载
- Firefox：设置 → 隐私与安全 → 权限 → 自动下载
- Edge：设置 → Cookie 和网站权限 → 更多权限 → 自动下载

#### Q2: 搜索股票名称时结果不准确
**解决方案**：
1. 尽量使用6位股票代码进行搜索
2. 确保股票名称拼写正确
3. 如果遇到指数或基金等非股票结果，使用代码搜索更准确

#### Q3: 抓取报告列表为空
**可能原因**：
1. 股票代码错误
2. 新浪财经数据源暂时不可用
3. 该股票在指定年份没有对应类型的报告

**解决方案**：
1. 验证股票代码是否正确
2. 稍后重试，可能是网络或数据源问题
3. 尝试其他报告类型或年份

#### Q4: 下载的PDF文件损坏或无法打开
**可能原因**：
1. PDF链接已失效
2. 网络问题导致下载不完整
3. 文件编码问题

**解决方案**：
1. 尝试重新下载
2. 通过报告详情页直接访问原始链接
3. 检查网络连接稳定性

### 错误代码参考

- **连接超时**：检查网络连接，确保可以访问新浪财经网站
- **编码错误**：系统会自动处理编码，如持续出现请检查Python环境
- **内存不足**：批量处理大量报告时，确保系统有足够内存

## 📝 贡献指南

我们欢迎任何形式的贡献，包括但不限于：

### 报告问题
- 在GitHub Issues中提交问题报告
- 提供详细的重现步骤和环境信息
- 包括错误信息和截图（如适用）

### 功能请求
- 描述清楚需求场景和使用价值
- 提供参考实现或设计思路
- 讨论技术可行性

### 提交代码
1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

### 开发规范
- 遵循现有的代码风格和项目结构
- 添加适当的注释和文档
- 确保不影响现有功能
- 测试新功能的正确性

## ⚖️ 法律与合规

### 数据来源
FinScraper 的数据来源于新浪财经（https://finance.sina.com.cn）的公开公告页面。所有报告内容的版权和使用权归原始披露主体（上市公司）及新浪财经所有。

### 使用条款
1. **合规使用**：请遵守新浪财经的 robots.txt 规则和使用条款
2. **访问频率**：避免高频访问，以免对数据源服务器造成压力
3. **商业用途**：如用于商业目的，请确保获得相应授权
4. **数据准确性**：工具仅提供数据抓取服务，不对数据内容的准确性负责

### 免责声明
- 本工具仅供学习和研究使用
- 使用者需自行承担使用风险
- 开发者不对因使用本工具导致的任何直接或间接损失负责
- 请尊重数据源的知识产权和服务条款

### 许可证
本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 📞 支持与联系

### 问题反馈
- GitHub Issues：提交问题报告和功能请求
- 邮件支持：可通过GitHub个人资料页获取维护者联系信息

### 社区
- Star 本项目以支持开发
- Fork 本项目进行自定义修改
- 分享使用经验和改进建议

---

<div align="center">

  **感谢使用 FinScraper！** 

  如果这个项目对你有帮助，请考虑给它一个 ⭐️

  [⬆️ 返回顶部](#finscraper)

---

## English

*Note: English documentation is under development. Currently the project documentation is primarily in Chinese. Contributions for English translation are welcome!*

---

*最后更新：2026年2月9日*