# B站兴趣控制系统 - bilibili-interest-control

一个基于Nemo2011/bilibili-api的B站兴趣控制系统，帮助你突破算法信息茧房，主动控制自己的兴趣方向。

## 🎯 核心功能

### 1. 灵活的兴趣控制系统
- ✅ 自然语言指令切换兴趣焦点（如"聚焦AI"、"切换到编程"）
- ✅ 主动推荐目标领域优质内容
- ✅ 过滤算法推荐的非目标内容
- ✅ 惰性提醒机制，监测并纠正偏离目标的行为

### 2. 内容立场识别系统
- ✅ 管理UP主偏好，记录喜欢的UP主
- ✅ 语义分析内容观点，过滤特定立场
- ✅ 示例：过滤像素范(UID:15741969)关于"AI取代程序员"的观点
- ✅ 支持自定义过滤规则

### 3. 友好的CLI界面
- ✅ 提供完整的命令行工具
- ✅ 支持所有核心功能
- ✅ 易于扩展和配置

## 🚀 快速开始

### 安装依赖
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 初始化配置
```bash
bic init
```

### 设置兴趣焦点
```bash
# 聚焦AI领域
bic intent "聚焦AI"

# 切换到编程学习
bic intent "切换到编程"
```

### 推荐内容
```bash
# 推荐20个符合当前兴趣的视频
bic recommend --limit 20
```

### 管理UP主偏好
```bash
# 添加喜欢的UP主
bic up add --uid 15741969 --name 像素范 --liked

# 添加不喜欢的UP主
bic up add --uid 12345 --name 某UP主 --disliked
```

### 设置立场过滤规则
```bash
# 过滤像素范关于"AI取代程序员"的观点
bic stance add --uid 15741969 --block "AI取代程序员"
bic stance add --uid 15741969 --block "程序员会被AI替代"
```

### 记录观看行为
```bash
bic log-watch --title "某娱乐视频" --up "某UP主" --uid 12345
```

### 查看当前配置
```bash
bic show-config
```

## 📦 技术特性

- **基于Nemo2011/bilibili-api**：成熟的B站API接口
- **异步API支持**：高效的网络请求
- **模块化设计**：易于扩展新功能
- **配置持久化**：自动保存用户偏好
- **友好的错误处理**：清晰的错误提示
- **支持多焦点切换**：预设AI、编程、游戏、影视等领域

## 📁 项目结构

```
bilibili-interest-control/
├── src/
│   └── bili_interest_control/
│       ├── __init__.py
│       ├── __main__.py
│       ├── bilibili_adapter.py    # B站API适配层
│       ├── cli.py                 # 命令行界面
│       ├── config_store.py        # 配置存储
│       ├── engine.py              # 核心引擎
│       ├── models.py              # 数据模型
│       ├── nlp.py                 # 自然语言处理
│       ├── reminder.py            # 惰性提醒
│       └── stance.py              # 立场过滤
├── pyproject.toml
├── README.md
└── .gitignore
```

## 🎨 预设兴趣领域

- **AI领域**：AI、人工智能、大模型、机器学习、LLM、Agent
- **编程领域**：编程、Python、后端、算法、系统设计、开发
- **游戏领域**：游戏、手游、PC游戏、主机游戏、电竞
- **影视领域**：电影、电视剧、综艺、动漫、剧集

## 📋 配置文件

配置文件位于 `~/.config/bic/config.json`，包含：
- 活跃兴趣焦点
- 各兴趣领域配置
- UP主偏好列表
- 立场过滤规则
- 提醒阈值设置

## 🚧 未来规划

- [ ] 支持更多B站API功能
- [ ] 添加Web UI界面
- [ ] 支持多账号管理
- [ ] 添加机器学习模型进行更精准的内容分析
- [ ] 支持自定义兴趣模板
- [ ] 添加内容收藏功能
- [ ] 支持导出推荐列表

## 📄 License

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**摆脱算法束缚，主动掌控你的兴趣！** 🎉
