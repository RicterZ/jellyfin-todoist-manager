# Jellyfin Webhook Receiver

一个使用FastAPI构建的web服务，用于接收和处理Jellyfin的webhook事件。

## 功能特性

- ✅ 接收 **Item Added** 事件（新项目添加）
- ✅ 接收 **Playback Start** 事件（开始播放）
- 📊 详细的事件信息输出
- 🔍 完整的请求体日志记录
- 🏥 健康检查端点
- 📚 自动生成的API文档

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

## API端点

- `GET /` - 服务状态和基本信息
- `POST /webhook` - 接收Jellyfin webhook事件
- `GET /health` - 健康检查
- `GET /docs` - 自动生成的API文档

## Jellyfin配置

在Jellyfin管理界面中配置webhook：

1. 进入 **控制台** → **网络** → **Webhooks**
2. 添加新的webhook
3. 设置URL为: `http://your-server:8000/webhook`
4. 选择要发送的事件类型：
   - Item Added
   - Playback Start

## 事件输出示例

### Item Added 事件
```
==================================================
📁 ITEM ADDED 事件
==================================================
📺 服务器: My Jellyfin Server (abc123)
📅 时间: 2024-01-15T10:30:00Z
🎬 项目名称: 电影名称
🆔 项目ID: item123
📂 项目类型: Movie
📁 项目路径: /media/movies/电影名称.mkv
⏱️  时长: 120.5 分钟
📅 制作年份: 2024
🎭 类型: 动作, 科幻
🏷️  标签: 4K, HDR
📝 简介: 这是一部精彩的电影...
==================================================
```

### Playback Start 事件
```
==================================================
▶️  PLAYBACK START 事件
==================================================
📺 服务器: My Jellyfin Server (abc123)
📅 时间: 2024-01-15T10:35:00Z
👤 用户: 用户名 (user123)
🎬 项目名称: 电影名称
🆔 项目ID: item123
📂 项目类型: Movie
📁 项目路径: /media/movies/电影名称.mkv
💻 客户端: Jellyfin Web
📱 设备名称: Chrome
🆔 设备ID: device123
🔢 应用版本: 10.8.0
⏱️  时长: 120.5 分钟
📍 播放位置: 0.0 分钟
📅 制作年份: 2024
🎭 类型: 动作, 科幻
==================================================
```

## 开发说明

服务使用Pydantic模型来验证和解析Jellyfin发送的webhook数据，确保数据的完整性和类型安全。所有接收到的原始数据都会被记录到日志中，方便调试和监控。

## 扩展功能

你可以根据需要扩展服务功能：

- 添加数据库存储
- 集成通知服务（邮件、Slack等）
- 添加更多事件类型支持
- 实现事件过滤和条件处理
# jellyfin-todoist-manager
