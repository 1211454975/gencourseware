import re  # 新增正则表达式模块导入
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
        return hashlib.md5(f"{content}_{self.difficulty}".encode()).hexdigest()  # 增加难度参数

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
        max_length = max_length or CONTENT_CONFIG.get('max_chunk_length', 2000)
        if not content:
            return []
        # 删除重复的max_length赋值
            
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

    def _validate_slide_content(self, slide_data: Dict):
        """深度内容校验"""
        error_messages = []
        
        # 更新必要字段列表
        required_fields = ['title', 'concept_structure', 'case_study', 'content']  # 增加content字段
        for field in required_fields:
            if field not in slide_data:
                error_messages.append(f"缺少必要字段: {field}")
        
        # 概念结构校验
        if len(slide_data.get('concept_structure', [])) < 3:
            error_messages.append("概念结构至少需要3个递进式要点")
            
        # 案例研究健壮性增强
        # 默认案例名称截取处理
        default_title = (slide_data.get('title', '未命名') or '未命名').strip()[:20]  
        slide_data['case_study'] = {
            "name": f"默认案例-{default_title}",
            "analysis": ["背景分析", "实施流程", "成果验证"]  # 结构化默认内容
        }
        if not slide_data.get('case_study', {}).get('name') or not slide_data.get('case_study', {}).get('analysis'):
                    error_messages.append("案例研究需要名称和详细分析")
                    
        # 可视化建议校验
        valid_charts = {'柱状图', '折线图', '流程图', '思维导图', '饼图', '散点图', '关系图'}  # 新增常见图表类型
        if not set(slide_data.get('visualization', [])).intersection(valid_charts):
            error_messages.append(f"可视化类型必须包含以下至少一项：{valid_charts}")  # 更新错误提示
            
        if error_messages:
            logger.warning("；".join(error_messages))
            if not slide_data.get('visualization'):
                slide_data['visualization'] = ['流程图']
            # 修改递归校验为单次修正
            if 'concept_structure' not in slide_data:  # 添加必要字段补全
                slide_data['concept_structure'] = ["基础概念", "核心原理", "应用场景"]
            return  # 移除递归调用避免死循环

# 在_generate_slide方法中添加校验
    def _generate_slide(self, content_chunk: str) -> Dict:
        # 增强的prompt模板
        prompt = f"""请严格按JSON格式生成结构化课件内容，必须包含以下字段：
        1. title (字符串): 不超过15字的精准标题
        2. concept_structure (数组): 3-5个递进式概念要点
        3. case_study (对象): 
            - name (案例名称)
            - analysis (案例分析步骤数组)
        4. visualization (数组): 从{['流程图','思维导图','柱状图']}中选择
        5. content (字符串): 详细讲解内容（不少于3个自然段）

        生成要求：
        - 使用中文标点符号
        - 避免专业术语堆砌
        - 案例需结合现实场景

        当前主题：{content_chunk}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": API_CONFIG['model'],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,  # 降低随机性
            "max_tokens": 1500,   # 限制生成长度
            "response_format": {"type": "json_object"}
        }

        try:
            logger.info(f"正在生成幻灯片，内容块长度：{len(content_chunk)}")
            response = requests.post(self.api_url, headers=headers, json=data, timeout=25)
            
            # 增强错误处理
            try:
                response.raise_for_status()
                raw_content = response.json()['choices'][0]['message']['content']
                
                # 新增正则清洗
                cleaned_content = re.sub(r'(?i)^```json|```$', '', raw_content).strip()
                
                slide_data = json.loads(cleaned_content)
                self._validate_slide_content(slide_data)
                
                # 内容兜底机制
                if not slide_data.get('content'):
                    slide_data['content'] = "\n".join(slide_data['concept_structure'])
                
                return slide_data

            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败，原始响应：{raw_content}")  # 记录原始响应
                return self._create_fallback_slide(content_chunk)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常：{str(e)}")
            return self._create_fallback_slide(content_chunk)

    def _create_fallback_slide(self, content: str) -> Dict:
        """应急幻灯片模板"""
        # return {
        #     "title": "内容生成失败",
        #     "content": content[:500],  # 截取原始内容
        #     "concept_structure": ["概念解析失败", "请联系管理员"],
        #     "case_study": {
        #         "name": "紧急案例",
        #         "analysis": ["问题描述", "临时方案"]
        #     },
        #     "visualization": ["流程图"]
        # }

        prompt = f"""请严格按JSON格式生成结构化课件内容，必须包含以下字段：
        1. title (字符串): 不超过15字的精准标题
        2. concept_structure (数组): 3-5个递进式概念要点
        3. case_study (对象): 
            - name (案例名称)
            - analysis (案例分析步骤数组)
        4. visualization (数组): 从{['流程图','思维导图','柱状图']}中选择
        5. content (字符串): 详细讲解内容（不少于3个自然段）

        生成要求：
        - 使用中文标点符号
        - 避免专业术语堆砌
        - 案例需结合现实场景

        当前主题：{content}
        """

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
                self._validate_slide_content(slide_data)  # 新增校验调用
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
            
            
            
            if 'key_points' not in slide_data or not isinstance(slide_data['key_points'], list):
                slide_data['key_points'] = []
            if 'examples' not in slide_data or not isinstance(slide_data['examples'], list):
                slide_data['examples'] = []
            
            # 保存到缓存
            # 生成缓存键，解决 cache_key 未定义的问题
            cache_key = self._get_cache_key(content)
            self._save_to_cache(cache_key, slide_data)
            
            return slide_data  # 确保此处有正确缩进
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API 请求错误: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"生成幻灯片时出错: {str(e)}")
            raise

    def _analyze_complexity(self, content_chunk: str) -> int:
        try:
            # 数学公式检测权重0.2
            formula_pattern = r"\$.*?\$|\\\(.*?\\\)"
            has_formula = bool(re.search(formula_pattern, content_chunk))
            
            # 专业术语权重0.4（4个核心术语）
            technical_terms = ["原理", "模型", "算法", "架构"]
            term_count = sum(1 for term in technical_terms if term in content_chunk)
            
            # 代码检测权重0.3 + 语句长度权重0.3
            code_pattern = r"\b(def|class|import|print)\b"
            has_code = bool(re.search(code_pattern, content_chunk))
            
            # 综合计算（总权重1.2）
            # 计算平均句子长度
            sentences = [s for s in content_chunk.split('。') if s]
            # 当前平均句子长度的计算方式可能不够准确
            sentences = [s for s in content_chunk.split('。') if s]
            avg_length = sum(len(s) for s in sentences) / len(sentences) if sentences else 0  # <-- 需要优化的部分
            # 合并所有权重系数（总权重系数1.2，通过min/max限制在合理范围）
            complexity_score = (term_count * 0.4) + (has_formula * 0.2) + (has_code * 0.3) + (avg_length / 50 * 0.3)
                    
            return min(max(int(complexity_score * 10), 1), 10)  # 确保最终得分在1-10之间
        except Exception as e:
            logger.error(f"复杂度分析失败: {str(e)}")
            return 5  # 返回默认值前添加日志记录

# 在generate方法中应用复杂度分析
    def generate(self) -> List[Dict]:
        # 修改配置访问方式
        min_slides = CONTENT_CONFIG.get('min_slides', 3)
        max_slides = CONTENT_CONFIG.get('max_slides', 10)
        
        # 假设 slides 是通过分割内容并生成幻灯片得到的，这里需要先定义或获取 slides
        # 以下代码假设先调用分割内容和生成幻灯片的方法
        content_chunks = self._split_content(self.content)
        slides = []
        for chunk in content_chunks:
            try:
                slide = self._generate_slide(chunk)
                slides.append(slide)
            except Exception as e:
                logger.error(f"生成幻灯片时出错: {str(e)}")

        if len(slides) < min_slides:
            logger.warning(f"生成的幻灯片数量（{len(slides)}）少于最小要求（{min_slides}）")
        elif len(slides) > max_slides:
            logger.warning(f"生成的幻灯片数量（{len(slides)}）超过最大限制（{max_slides}）")
            
        logger.info(f"课件生成完成，共生成 {len(slides)} 个幻灯片")
        return slides