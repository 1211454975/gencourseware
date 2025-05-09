import os
import json
import time
from typing import List, Dict
import requests
from ..utils.logger import setup_logger
from config import CACHE_DIR, API_CONFIG, CONTENT_CONFIG

logger = setup_logger(__name__)

class ContentGenerator:
    def __init__(self, content: str, difficulty: str):
        if not content or not content.strip():
            raise ValueError("内容不能为空")
            
        self.content = content
        self.difficulty = difficulty
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        
        if not self.api_key:
            raise ValueError("未设置 DEEPSEEK_API_KEY 环境变量")
            
        self.api_url = API_CONFIG['url']
        self.cache_dir = CACHE_DIR
        self._setup_cache()

    def _setup_cache(self):
        """设置缓存目录"""
        self.cache_dir = str(self.cache_dir)  # 确保是字符串
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_key(self, content: str) -> str:
        """生成缓存键"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Dict:
        """从缓存获取内容"""
        cache_file = os.path.join(str(self.cache_dir), f"{cache_key}.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _save_to_cache(self, cache_key: str, data: Dict):
        """保存内容到缓存"""
        cache_file = os.path.join(str(self.cache_dir), f"{cache_key}.json")
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _split_content(self, content: str, max_length: int = None) -> List[str]:
        """将内容分割成较小的块"""
        if not content:
            return []
            
        max_length = max_length or CONTENT_CONFIG['max_chunk_length']
            
        # 使用更智能的分割方法
        sentences = []
        current_sentence = ""
        
        for char in content:
            current_sentence += char
            if char in ['。', '！', '？', '.', '!', '?']:
                sentences.append(current_sentence.strip())
                current_sentence = ""
                
        if current_sentence:
            sentences.append(current_sentence.strip())
            
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk)
            
        logger.info(f"内容已分割为 {len(chunks)} 个块")
        return chunks

    def _generate_slide(self, content_chunk: str) -> Dict:
        """生成单个幻灯片内容"""
        if not content_chunk or not content_chunk.strip():
            logger.warning("跳过空内容块")
            return None
            
        cache_key = self._get_cache_key(content_chunk)
        cached_result = self._get_from_cache(cache_key)
        
        if cached_result:
            logger.info("使用缓存内容")
            return cached_result

        prompt = f"""请将以下学术内容转换为面向{self.difficulty}水平学生的课件幻灯片。
请严格按照以下 JSON 格式返回，不要添加任何其他内容：
{{
    "title": "幻灯片标题",
    "content": "幻灯片内容（使用简单的语言和例子）",
    "type": "content",
    "key_points": ["关键点1", "关键点2", "..."],
    "examples": ["示例1", "示例2", "..."]
}}

内容：{content_chunk}"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": API_CONFIG['model'],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": API_CONFIG['temperature'],
            "response_format": {"type": "json_object"}
        }

        try:
            logger.info("正在调用 API 生成幻灯片...")
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            if 'choices' not in result or not result['choices']:
                raise ValueError("API 响应格式错误：未找到 choices 字段")
                
            content = result['choices'][0]['message']['content']
            logger.debug(f"API 响应内容: {content}")
            
            # 尝试清理和格式化内容
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            try:
                slide_data = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"JSON 解析错误: {str(e)}")
                logger.error(f"原始内容: {content}")
                # 尝试使用更宽松的解析方式
                try:
                    import ast
                    # 将单引号替换为双引号
                    content = content.replace("'", '"')
                    # 尝试作为 Python 字典评估
                    slide_data = ast.literal_eval(content)
                    slide_data = json.loads(json.dumps(slide_data))
                except Exception as e2:
                    logger.error(f"备选解析方法也失败: {str(e2)}")
                    raise ValueError("API 返回的内容不是有效的 JSON 格式")
            
            # 验证必要的字段
            required_fields = ['title', 'content', 'type']
            for field in required_fields:
                if field not in slide_data:
                    raise ValueError(f"幻灯片数据缺少必要字段: {field}")
            
            # 确保所有字段都是正确的类型
            if not isinstance(slide_data['title'], str):
                slide_data['title'] = str(slide_data['title'])
            if not isinstance(slide_data['content'], str):
                slide_data['content'] = str(slide_data['content'])
            if not isinstance(slide_data['type'], str):
                slide_data['type'] = 'content'
            if 'key_points' not in slide_data or not isinstance(slide_data['key_points'], list):
                slide_data['key_points'] = []
            if 'examples' not in slide_data or not isinstance(slide_data['examples'], list):
                slide_data['examples'] = []
            
            # 保存到缓存
            self._save_to_cache(cache_key, slide_data)
            
            return slide_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API 请求错误: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"生成幻灯片时出错: {str(e)}")
            raise

    def generate(self) -> List[Dict]:
        """生成完整的课件内容"""
        logger.info("开始生成课件内容")
        
        # 分割内容
        content_chunks = self._split_content(self.content)
        if not content_chunks:
            raise ValueError("内容分割后为空")
            
        slides = []
        
        # 批量处理内容块
        for i, chunk in enumerate(content_chunks):
            logger.info(f"处理第 {i+1}/{len(content_chunks)} 个内容块")
            try:
                slide = self._generate_slide(chunk)
                if slide:
                    slides.append(slide)
                # 添加延迟以避免API限制
                time.sleep(1)
            except Exception as e:
                logger.error(f"处理内容块时出错: {str(e)}")
                continue
        
        if not slides:
            raise ValueError("未能生成任何有效的幻灯片")
            
        # 验证幻灯片数量
        if len(slides) < CONTENT_CONFIG['min_slides']:
            logger.warning(f"生成的幻灯片数量（{len(slides)}）少于最小要求（{CONTENT_CONFIG['min_slides']}）")
        elif len(slides) > CONTENT_CONFIG['max_slides']:
            logger.warning(f"生成的幻灯片数量（{len(slides)}）超过最大限制（{CONTENT_CONFIG['max_slides']}）")
            
        logger.info(f"课件生成完成，共生成 {len(slides)} 个幻灯片")
        return slides 