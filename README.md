# GenCourseWare - AI 课程内容生成系统

GenCourseWare 是一个基于人工智能的课程内容生成系统，能够自动生成高质量的课程内容，包括文本、图片和视频。

## 功能特点

- 自动生成课程大纲和内容
- 支持多种课程类型（理论、实践、混合）
- 自动生成课程图片和视频
- 支持中英文内容生成
- 智能缓存系统，提高生成效率
- 完整的错误处理和日志记录

## 系统要求

- Python 3.8 或更高版本
- Windows/macOS/Linux 操作系统
- 足够的磁盘空间用于存储生成的内容
- 网络连接（用于访问 AI API）

## 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/GenCourseWare.git
cd GenCourseWare
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
# Windows
set GENCOURSEWARE_STORAGE_DIR=E:\ai-gen\GenCourseWare\storage

# Linux/macOS
export GENCOURSEWARE_STORAGE_DIR=/path/to/GenCourseWare/storage
```

## 使用方法

1. 启动系统：
```bash
python main.py
```

2. 在浏览器中访问：
```
http://localhost:5000
```

3. 使用界面：
   - 输入课程主题
   - 选择课程类型
   - 设置生成参数
   - 点击生成按钮

## 目录结构

```
GenCourseWare/
├── src/
│   ├── generator/     # 内容生成模块
│   ├── video/         # 视频生成模块
│   ├── image/         # 图片生成模块
│   └── utils/         # 工具函数
├── storage/
│   ├── cache/         # 缓存文件
│   ├── output/        # 输出文件
│   └── temp/          # 临时文件
├── config.py          # 配置文件
├── main.py           # 主程序
└── requirements.txt   # 依赖列表
```

## 配置说明

系统的主要配置在 `config.py` 文件中：

- `API_CONFIG`: API 相关配置
- `VIDEO_CONFIG`: 视频生成配置
- `IMAGE_CONFIG`: 图片生成配置
- `CACHE_CONFIG`: 缓存配置

## 注意事项

1. 确保有足够的磁盘空间
2. 保持网络连接稳定
3. 定期清理临时文件
4. 检查日志文件了解系统状态

## 常见问题

1. 生成失败
   - 检查网络连接
   - 确认 API 密钥有效
   - 查看日志文件

2. 视频生成问题
   - 确保有足够的磁盘空间
   - 检查临时目录权限
   - 验证图片生成是否成功

3. 缓存问题
   - 检查缓存目录权限
   - 确认缓存配置正确
   - 必要时清理缓存

## 开发说明

1. 代码规范
   - 遵循 PEP 8 规范
   - 使用类型注解
   - 添加适当的注释

2. 错误处理
   - 使用 try-except 捕获异常
   - 记录详细的错误日志
   - 提供友好的错误提示

3. 测试
   - 单元测试
   - 集成测试
   - 性能测试

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

- 项目维护者：[parsifalster]
- 邮箱：[1211454975@qq.com]
- 项目地址：[https://github.com/yourusername/GenCourseWare] 