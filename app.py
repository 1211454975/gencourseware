import streamlit as st
import os
from dotenv import load_dotenv
import tempfile
from src.parser.pdf_parser import PDFParser
from src.generator.content_generator import ContentGenerator
from src.video.video_generator import VideoGenerator

# 加载环境变量
load_dotenv()

st.set_page_config(
    page_title="学术论文视频课件生成器",
    page_icon="🎓",
    layout="wide"
)

def format_content(content: dict) -> str:
    """将解析后的内容格式化为字符串"""
    formatted_text = f"{content['title']}\n\n"
    formatted_text += f"作者: {', '.join(content['authors'])}\n\n"
    formatted_text += f"摘要:\n{content['abstract']}\n\n"
    
    for section in content['sections']:
        formatted_text += f"{section['title']}\n{section['content']}\n\n"
    
    return formatted_text

def main():
    st.title("学术论文视频课件生成器")
    st.write("上传学术论文，自动生成面向学生的视频课件")

    # 文件上传
    uploaded_file = st.file_uploader("上传PDF论文", type=['pdf'])
    
    if uploaded_file is not None:
        # 保存上传的文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            pdf_path = tmp_file.name

        # 课件生成参数
        st.subheader("课件生成参数")
        col1, col2 = st.columns(2)
        
        with col1:
            difficulty = st.select_slider(
                "难度级别",
                options=["入门", "基础", "中级", "高级"],
                value="基础"
            )
            
        with col2:
            duration = st.slider(
                "预计视频时长（分钟）",
                min_value=5,
                max_value=60,
                value=15
            )

        # 生成按钮
        if st.button("生成课件"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # 1. 解析PDF
                status_text.text("正在解析PDF文件...")
                parser = PDFParser(pdf_path)
                content = parser.parse()
                formatted_content = format_content(content)
                progress_bar.progress(20)
                
                # 2. 生成课件内容
                status_text.text("正在生成课件内容...")
                generator = ContentGenerator(formatted_content, difficulty)
                slides = generator.generate()
                
                if not slides:
                    raise ValueError("未能生成任何幻灯片内容")
                
                progress_bar.progress(60)
                
                # 3. 生成视频
                status_text.text("正在生成视频...")
                video_gen = VideoGenerator(slides, duration)
                video_path = video_gen.generate()
                progress_bar.progress(100)
                
                # 显示结果
                status_text.text("课件生成完成！")
                st.success("课件生成完成！")
                st.video(video_path)
                
            except Exception as e:
                st.error(f"生成过程中出现错误: {str(e)}")
                status_text.text("生成失败")
            finally:
                # 清理临时文件
                os.unlink(pdf_path)

if __name__ == "__main__":
    main() 