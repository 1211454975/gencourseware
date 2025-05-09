# 学术论文视频课件生成器

这个项目旨在将学术论文转换为面向学生的视频课件。通过使用人工智能技术，自动提取论文中的关键内容，并生成结构化的视频课件。

## 功能特点

- 论文内容解析和关键信息提取
- 自动生成课件大纲和结构
- 生成视频脚本
- 支持多种输出格式
- 可自定义课件风格和难度级别

## 技术栈

- Python 3.8+
- OpenAI API
- FFmpeg (视频处理)
- PyPDF2 (PDF解析)
- Streamlit (Web界面)

## 安装说明

1. 克隆项目仓库
2. 安装依赖：
```bash
pip install -r requirements.txt
```
3. 配置环境变量：
   - 创建 `.env` 文件
   - 添加 OpenAI API 密钥

## 使用方法

1. 运行 Web 界面：
```bash
streamlit run app.py
```

2. 上传论文 PDF 文件
3. 选择课件生成参数
4. 等待生成结果

## 项目结构

```
.
├── app.py              # Streamlit Web 应用
├── src/               # 源代码目录
│   ├── parser/        # 论文解析模块
│   ├── generator/     # 课件生成模块
│   └── video/         # 视频处理模块
├── requirements.txt   # 项目依赖
└── README.md         # 项目说明文档
``` 