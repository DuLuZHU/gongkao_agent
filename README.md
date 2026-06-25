# 公考AI私教 📚

从"刷题机器"到"全能私教"，一个集导师、对手、秘书于一体的公务员备考AI助手。

## 核心功能

### 1. 深度真题拆解引擎

- 智能拆解：粘贴一道真题，AI自动解析题型标签、考点、思维路径
- 干扰项透析：逐一分析每个选项的对错原因和出题陷阱
- 举一反三：自动生成变式题，强化思维模式

### 2. 申论智能对练与精批

- 小角度对练：针对特定能力点进行专项练习
- 逐句精批：指出有效要点、遗漏内容和表述问题
- 逻辑提优：提供更优的逻辑组织方式
- 面试模拟：AI考官在线测评，多维度打分

### 3. 专属知识库与智能笔记

- 自动知识沉淀：题目、讲解、错题自动存入可搜索知识库
- 知识图谱：AI帮你组织零散知识点成树状结构
- 主动遗忘预警：定时推送复习提醒

### 4. 小团体对战与协作

- 自定义题库：录入各自省份真题和难题
- 对战模式：限时抢答赛，实时排行榜
- 协作式模拟面试：营造真实讨论氛围

## 技术栈

- **前端框架**: Streamlit
- **大语言模型**: DeepSeek (deepseek-v4-flash)
- **向量数据库**: ChromaDB
- **关系数据库**: SQLite
- **API客户端**: OpenAI SDK

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置环境变量

新建 `.env` 文件，填入你的 DeepSeek API Key：

```
DEEPSEEK_API_KEY=your_api_key_here
```

### 3. 运行应用

```bash
streamlit run app.py
```

### 4. 访问应用

打开浏览器访问 `http://localhost:8501`

## 项目结构

```
gongkao_agent/
├── app.py                 # Streamlit 主应用
├── config.py              # 配置文件（API Key、提示词等）
├── database.py            # SQLite 数据库操作
├── llm_client.py          # DeepSeek API 客户端
├── knowledge_base.py      # 向量知识库（ChromaDB）
├── battle_module.py       # 对战模式模块
├── requirements.txt       # Python 依赖
├── .env.example           # 环境变量示例
└── data/                  # 数据目录（自动创建）
    ├── gongkao.db         # SQLite 数据库文件
    └── chroma_db/         # ChromaDB 向量存储
```

## 使用说明

### 真题拆解

1. 在左侧导航栏选择"真题拆解"
2. 粘贴公务员考试真题到输入框
3. 点击"开始分析"，AI将输出完整的题目解析
4. 可展开"生成变式题"查看相关练习题

### 申论精批

1. 选择"完整批改"或"小角度对练"模式
2. 填写题目要求、材料和你的答案
3. 点击"提交批改"获取AI精批结果

### 面试模拟

1. 选择或输入面试题目
2. 输入你的回答
3. 点击"开始测评"，AI从内容深度、逻辑结构、事例匹配度三个维度评分

### 知识库

1. "搜索知识"：用关键词搜索你的学习笔记
2. "知识图谱"：AI帮你构建知识点树状结构
3. "添加笔记"：手动添加学习笔记和技巧

### 对战模式

1. 选择题目类型和对战时长
2. 点击"开始对战"进入限时答题
3. 完成后查看排行榜和解析

### 学习提醒

1. 查看待复习的题目
2. 点击"立即复习"进行知识点巩固
3. 可生成今日复习建议

## API 配置

本项目使用 DeepSeek API，需要在 [DeepSeek 官网](https://platform.deepseek.com/) 注册并获取 API Key。

配置参数：

- 模型：deepseek-v4-flash
- API Base URL：<https://api.deepseek.com>
- 推理模式：high reasoning\_effort

## 注意事项

1. 首次运行会自动创建数据库和向量存储目录
2. 建议使用 Python 3.10+ 版本
3. 网络需要能够访问 DeepSeek API
4. 数据存储在本地，确保有写入权限

## 开发路径

### V0 最小可行版本（1-2周）

- Streamlit 单页聊天界面
- 深度真题拆解功能
- DeepSeek API 接入

### V1 融入学习闭环（3-4周）

- 用户系统和 SQLite 数据库
- 错题本功能
- 申论模块上线

### V2 小团体与智能化（5周以后）

- 用户权限区分
- 对战模式（WebSocket）
- 向量数据库语义搜索

## License

GNU Affero General Public License v3 (AGPLv3)

## 作者信息

- **作者**：DuLuZHU
- **联系方式**：请通过 GitHub Issues 联系
- **项目地址**：<https://github.com/DuLuZHU/gongkao_agent>

## 版权声明

本项目采用 **GNU Affero General Public License v3** 开源协议。

**重要声明**：

- 本项目代码仅供学习和研究使用，禁止用于商业目的
- 任何个人或组织在使用、修改或搬运本项目代码时，必须保留原作者信息并注明出处
- 转载或分享本项目时，请务必提供指向原始仓库的链接
- 修改后的代码必须以相同的 AGPLv3 许可证发布，并公开源代码

**引用格式**：

```
公考AI私教 - 集导师、对手、秘书于一体的公务员备考AI助手
https://github.com/DuLuZHU/gongkao_agent
```

