import os
from typing import List, Dict
from moviepy.editor import ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import tempfile
import platform
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.utils.logger import setup_logger
from config import OUTPUT_DIR, TEMP_DIR, VIDEO_CONFIG

logger = setup_logger(__name__)

class VideoGenerator:
    def __init__(self, slides: List[Dict], duration: int):
        if not slides:
            raise ValueError("幻灯片列表不能为空")
            
        # 检查幻灯片数据类型
        if not isinstance(slides, list):
            raise ValueError(f"幻灯片数据必须是列表类型，当前类型: {type(slides)}")
            
        self.slides = slides
        self.total_duration = duration * 60  # 转换为秒
        self.slide_duration = self.total_duration / len(slides)
        
        # 确保路径是字符串类型
        logger.debug(f"OUTPUT_DIR 类型: {type(OUTPUT_DIR)}")
        logger.debug(f"OUTPUT_DIR 值: {OUTPUT_DIR}")
        logger.debug(f"TEMP_DIR 类型: {type(TEMP_DIR)}")
        logger.debug(f"TEMP_DIR 值: {TEMP_DIR}")
        
        self.output_dir = str(OUTPUT_DIR)
        self.temp_dir = str(TEMP_DIR)
        
        logger.debug(f"self.output_dir 类型: {type(self.output_dir)}")
        logger.debug(f"self.output_dir 值: {self.output_dir}")
        logger.debug(f"self.temp_dir 类型: {type(self.temp_dir)}")
        logger.debug(f"self.temp_dir 值: {self.temp_dir}")
        
        self._setup_directories()
        
        # 使用配置文件中的视频设置
        self.width = VIDEO_CONFIG['width']
        self.height = VIDEO_CONFIG['height']
        self.fps = VIDEO_CONFIG['fps']
        self.background_color = VIDEO_CONFIG['background_color']
        self.text_color = VIDEO_CONFIG['text_color']
        self.title_font_size = VIDEO_CONFIG['title_font_size']
        self.content_font_size = VIDEO_CONFIG['content_font_size']
        
        self._load_fonts()

    def _load_fonts(self):
        """加载字体文件"""
        try:
            # 根据操作系统选择默认字体
            if platform.system() == 'Windows':
                font_path = os.path.join("C:", os.sep, "Windows", "Fonts", "msyh.ttc")  # 微软雅黑
            elif platform.system() == 'Darwin':  # macOS
                font_path = os.path.join(os.sep, "System", "Library", "Fonts", "PingFang.ttc")
            else:  # Linux
                font_path = os.path.join(os.sep, "usr", "share", "fonts", "truetype", "dejavu", "DejaVuSans.ttf")
            
            font_path = str(font_path)  # 确保是字符串
            if not os.path.exists(font_path):
                # 如果找不到系统字体，使用默认字体
                self.title_font = ImageFont.load_default()
                self.content_font = ImageFont.load_default()
                logger.warning(f"未找到系统字体 {font_path}，使用默认字体")
            else:
                self.title_font = ImageFont.truetype(font_path, self.title_font_size)
                self.content_font = ImageFont.truetype(font_path, self.content_font_size)
        except Exception as e:
            logger.error(f"加载字体时出错: {str(e)}")
            self.title_font = ImageFont.load_default()
            self.content_font = ImageFont.load_default()

    def _setup_directories(self):
        """设置输出和临时目录"""
        for dir_path in [self.output_dir, self.temp_dir]:
            dir_path = str(dir_path)  # 确保是字符串
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    def _create_slide_clip(self, slide: Dict, index: int) -> ImageClip:
        """创建单个幻灯片的视频片段"""
        try:
            # 确保幻灯片数据是字典类型
            if not isinstance(slide, dict):
                raise ValueError(f"幻灯片数据必须是字典类型，当前类型: {type(slide)}")
            
            # 确保必要的字段存在且为字符串类型
            title = str(slide.get('title', ''))
            content = str(slide.get('content', ''))
            
            # 创建图片剪辑
            logger.debug(f"临时目录类型: {type(self.temp_dir)}")
            logger.debug(f"临时目录值: {self.temp_dir}")
            
            try:
                # 创建包含标题和内容的图片
                with Image.new('RGB', (self.width, self.height), self.background_color) as image:
                    draw = ImageDraw.Draw(image)
                    
                    # 绘制标题
                    if title:
                        title_width = draw.textlength(title, font=self.title_font)
                        title_x = (self.width - title_width) // 2
                        draw.text((title_x, 50), title, font=self.title_font, fill=self.text_color)
                    
                    # 绘制内容
                    if content:
                        content_lines = self._wrap_text(content, self.content_font, self.width - 200)
                        y = 200
                        for line in content_lines:
                            draw.text((100, y), line, font=self.content_font, fill=self.text_color)
                            y += 50
                    
                    # 保存图片
                    image_path = os.path.join(self.temp_dir, f"slide_{index:03d}_with_text.png")
                    image.save(image_path)
                    logger.debug(f"保存带文本的图片到: {image_path}")
                
                # 创建视频片段
                clip = ImageClip(image_path)
                clip = clip.set_duration(self.slide_duration)
                logger.debug("成功创建视频片段")
                
                return clip
                
            except Exception as e:
                logger.error(f"创建幻灯片图片时出错: {str(e)}")
                raise
            
        except Exception as e:
            logger.error(f"创建幻灯片 {index} 时出错: {str(e)}")
            logger.error(f"幻灯片数据: {slide}")
            raise

    def generate(self) -> str:
        """生成完整的视频"""
        logger.info("开始生成视频")
        
        try:
            # 检查幻灯片数据
            if not isinstance(self.slides, list):
                raise ValueError(f"幻灯片数据必须是列表类型，当前类型: {type(self.slides)}")
            
            # 创建所有幻灯片的视频片段
            clips = []
            for i, slide in enumerate(self.slides):
                try:
                    logger.info(f"处理第 {i+1}/{len(self.slides)} 个幻灯片")
                    logger.debug(f"幻灯片数据: {slide}")
                    
                    # 检查幻灯片数据
                    if not isinstance(slide, dict):
                        raise ValueError(f"幻灯片数据必须是字典类型，当前类型: {type(slide)}")
                    
                    clip = self._create_slide_clip(slide, i)
                    clips.append(clip)
                except KeyboardInterrupt:
                    logger.info("生成过程被用户中断")
                    break
                except Exception as e:
                    logger.error(f"处理幻灯片 {i+1} 时出错: {str(e)}")
                    continue
            
            if not clips:
                raise ValueError("没有生成任何视频片段")
            
            # 连接所有视频片段
            final_video = concatenate_videoclips(clips)
            
            # 生成输出文件路径
            output_dir = str(self.output_dir)  # 确保是字符串
            output_path = os.path.join(output_dir, "output.mp4")
            logger.debug(f"输出路径: {output_path}")
            
            try:
                # 导出视频
                final_video.write_videofile(
                    output_path,
                    fps=self.fps,
                    codec='libx264',
                    audio=False,
                    logger=None  # 禁用 moviepy 的进度输出
                )
                
                logger.info(f"视频生成完成: {output_path}")
                return output_path
            except KeyboardInterrupt:
                logger.info("视频导出过程被用户中断")
                raise
                
        except Exception as e:
            logger.error(f"生成视频时出错: {str(e)}")
            raise
        finally:
            # 清理临时文件
            self._cleanup_temp_files()

    def _cleanup_temp_files(self):
        """清理临时文件"""
        try:
            temp_dir = str(self.temp_dir)  # 确保是字符串
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    if file.startswith("slide_") and file.endswith(".png"):
                        try:
                            file_path = os.path.join(temp_dir, file)
                            os.remove(file_path)
                        except Exception as e:
                            logger.warning(f"清理临时文件 {file} 时出错: {str(e)}")
        except Exception as e:
            logger.error(f"清理临时文件时出错: {str(e)}")

    def _create_slide_image(self, slide: Dict, temp_dir: str, index: int) -> str:
        """创建幻灯片图片"""
        try:
            # 确保临时目录是字符串
            logger.debug(f"输入临时目录类型: {type(temp_dir)}")
            logger.debug(f"输入临时目录值: {temp_dir}")
            temp_dir = str(temp_dir)
            logger.debug(f"转换后临时目录类型: {type(temp_dir)}")
            logger.debug(f"转换后临时目录值: {temp_dir}")
            
            # 确保幻灯片数据是字典类型
            if not isinstance(slide, dict):
                raise ValueError(f"幻灯片数据必须是字典类型，当前类型: {type(slide)}")
            
            # 确保临时目录存在
            if not os.path.exists(temp_dir):
                logger.debug(f"创建临时目录: {temp_dir}")
                os.makedirs(temp_dir)
                
            # 创建空白图片
            with Image.new('RGB', (self.width, self.height), self.background_color) as image:
                draw = ImageDraw.Draw(image)
                logger.debug("成功创建空白图片")
                
                # 根据幻灯片类型绘制内容
                slide_type = str(slide.get('type', 'content'))  # 确保类型是字符串
                logger.debug(f"幻灯片类型: {slide_type}")
                
                try:
                    if slide_type == 'title':
                        self._draw_title_slide(draw, slide, self.title_font, self.content_font)
                    elif slide_type == 'toc':
                        self._draw_toc_slide(draw, slide, self.title_font, self.content_font)
                    elif slide_type == 'content':
                        self._draw_content_slide(draw, slide, self.title_font, self.content_font)
                    elif slide_type == 'summary':
                        self._draw_summary_slide(draw, slide, self.title_font, self.content_font)
                    else:
                        logger.warning(f"未知的幻灯片类型: {slide_type}，使用内容类型")
                        self._draw_content_slide(draw, slide, self.title_font, self.content_font)
                    logger.debug("成功绘制幻灯片内容")
                except Exception as e:
                    logger.error(f"绘制幻灯片内容时出错: {str(e)}")
                    raise
                
                # 保存图片，使用索引确保文件名唯一
                try:
                    output_path = os.path.join(temp_dir, f"slide_{index:03d}_{slide_type}.png")
                    logger.debug(f"输出路径类型: {type(output_path)}")
                    logger.debug(f"输出路径值: {output_path}")
                    
                    # 确保输出目录存在
                    output_dir = os.path.dirname(output_path)
                    if not os.path.exists(output_dir):
                        logger.debug(f"创建输出目录: {output_dir}")
                        os.makedirs(output_dir)
                    
                    # 保存图片
                    image.save(output_path)
                    logger.debug(f"成功保存图片到: {output_path}")
                    
                    # 验证文件是否成功保存
                    if not os.path.exists(output_path):
                        raise FileNotFoundError(f"图片文件未能成功保存: {output_path}")
                    
                    return output_path
                except Exception as e:
                    logger.error(f"保存图片时出错: {str(e)}")
                    raise
            
        except Exception as e:
            logger.error(f"创建幻灯片图片时出错: {str(e)}")
            logger.error(f"幻灯片数据: {slide}")
            raise

    def _draw_title_slide(self, draw: ImageDraw.ImageDraw, slide: Dict,
                         title_font: ImageFont.FreeTypeFont,
                         content_font: ImageFont.FreeTypeFont):
        """绘制标题页"""
        try:
            # 绘制标题
            title = slide.get('title', '')
            if title:
                title_width = draw.textlength(title, font=title_font)
                title_x = (self.width - title_width) // 2
                draw.text((title_x, self.height // 3), title,
                         font=title_font, fill=self.text_color)
            
            # 绘制副标题或内容
            subtitle = slide.get('subtitle', '')
            if not subtitle and 'content' in slide:
                subtitle = slide['content']  # 如果没有副标题，使用内容作为副标题
                
            if subtitle:
                subtitle_width = draw.textlength(subtitle, font=content_font)
                subtitle_x = (self.width - subtitle_width) // 2
                draw.text((subtitle_x, self.height // 2), subtitle,
                         font=content_font, fill=self.text_color)
        except Exception as e:
            logger.error(f"绘制标题页时出错: {str(e)}")
            raise

    def _draw_toc_slide(self, draw: ImageDraw.ImageDraw, slide: Dict,
                       title_font: ImageFont.FreeTypeFont,
                       content_font: ImageFont.FreeTypeFont):
        """绘制目录页"""
        try:
            # 绘制标题
            title = slide.get('title', '')
            if title:
                title_width = draw.textlength(title, font=title_font)
                title_x = (self.width - title_width) // 2
                draw.text((title_x, 100), title,
                         font=title_font, fill=self.text_color)
            
            # 绘制目录项
            sections = slide.get('sections', [])
            if not sections and 'key_points' in slide:
                sections = slide['key_points']  # 如果没有目录项，使用关键点作为目录
                
            y = 200
            for section in sections:
                draw.text((100, y), f"• {section}",
                         font=content_font, fill=self.text_color)
                y += 60
        except Exception as e:
            logger.error(f"绘制目录页时出错: {str(e)}")
            raise

    def _draw_content_slide(self, draw: ImageDraw.ImageDraw, slide: Dict,
                          title_font: ImageFont.FreeTypeFont,
                          content_font: ImageFont.FreeTypeFont):
        """绘制内容页"""
        try:
            # 绘制标题
            title = slide.get('title', '')
            if title:
                title_width = draw.textlength(title, font=title_font)
                title_x = (self.width - title_width) // 2
                draw.text((title_x, 100), title,
                         font=title_font, fill=self.text_color)
            
            # 绘制内容
            content = slide.get('content', '')
            if content:
                content_lines = self._wrap_text(content, content_font, self.width - 200)
                y = 200
                for line in content_lines:
                    draw.text((100, y), line,
                             font=content_font, fill=self.text_color)
                    y += 50
                    
                # 如果有关键点，在内容下方显示
                if 'key_points' in slide and slide['key_points']:
                    y += 30  # 添加一些间距
                    for point in slide['key_points']:
                        draw.text((100, y), f"• {point}",
                                 font=content_font, fill=self.text_color)
                        y += 40
        except Exception as e:
            logger.error(f"绘制内容页时出错: {str(e)}")
            raise

    def _draw_summary_slide(self, draw: ImageDraw.ImageDraw, slide: Dict,
                          title_font: ImageFont.FreeTypeFont,
                          content_font: ImageFont.FreeTypeFont):
        """绘制总结页"""
        try:
            # 绘制标题
            title = slide.get('title', '')
            if title:
                title_width = draw.textlength(title, font=title_font)
                title_x = (self.width - title_width) // 2
                draw.text((title_x, 100), title,
                         font=title_font, fill=self.text_color)
            
            # 绘制总结内容
            content = slide.get('content', '')
            if content:
                content_lines = self._wrap_text(content, content_font, self.width - 200)
                y = 200
                for line in content_lines:
                    draw.text((100, y), line,
                             font=content_font, fill=self.text_color)
                    y += 50
                    
                # 如果有示例，在内容下方显示
                if 'examples' in slide and slide['examples']:
                    y += 30  # 添加一些间距
                    for example in slide['examples']:
                        draw.text((100, y), f"• {example}",
                                 font=content_font, fill=self.text_color)
                        y += 40
        except Exception as e:
            logger.error(f"绘制总结页时出错: {str(e)}")
            raise

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """文本自动换行，支持中英文"""
        if not text:
            return []
            
        lines = []
        current_line = []
        current_width = 0
        
        for char in text:
            char_width = font.getlength(char)
            
            # 处理换行符
            if char == '\n':
                if current_line:
                    lines.append(''.join(current_line))
                    current_line = []
                    current_width = 0
                continue
            
            # 处理空格
            if char.isspace():
                if current_line:
                    lines.append(''.join(current_line))
                    current_line = []
                    current_width = 0
                continue
            
            # 检查是否需要换行
            if current_width + char_width > max_width:
                if current_line:
                    lines.append(''.join(current_line))
                    current_line = []
                    current_width = 0
            
            current_line.append(char)
            current_width += char_width
        
        # 添加最后一行
        if current_line:
            lines.append(''.join(current_line))
        
        return lines 