"""
F-003: 解析知识图谱结构
知识图谱 Markdown 解析器

功能职责：
- 解析 Markdown 标题层级（# → ## → ### → ####）
- 提取学科、学期、章节、知识点信息
- 解析知识点属性（难度等级、前置知识点、描述）
- 构建知识图谱数据结构
- 验证知识点数量≤10,000

版本: v1.0
更新时间: 2026-05-08
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ParsedKnowledgePoint:
    """解析后的知识点"""
    name: str
    chapter_name: str
    semester_name: str
    subject_name: str
    difficulty_level: int = 3  # 默认中等难度
    prerequisite_name: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = 0


@dataclass
class ParsedChapter:
    """解析后的章节"""
    name: str
    semester_name: str
    subject_name: str
    sort_order: int = 0


@dataclass
class ParsedSemester:
    """解析后的学期"""
    name: str
    subject_name: str
    sort_order: int = 0


@dataclass
class ParsedSubject:
    """解析后的学科"""
    name: str
    description: Optional[str] = None


@dataclass
class KnowledgeGraphParseResult:
    """知识图谱解析结果"""
    success: bool
    message: str
    stats: Dict[str, int] = field(default_factory=dict)
    subject: Optional[ParsedSubject] = None
    semesters: List[ParsedSemester] = field(default_factory=list)
    chapters: List[ParsedChapter] = field(default_factory=list)
    knowledge_points: List[ParsedKnowledgePoint] = field(default_factory=list)


class KnowledgeGraphParser:
    """
    知识图谱 Markdown 解析器
    
    支持的 Markdown 结构：
    - 一级标题(#): 学科
    - 二级标题(##): 学期
    - 三级标题(###): 章节
    - 四级标题(####): 知识点
    
    知识点属性支持：
    - difficulty: 难度等级 (1-5)
    - prerequisite: 前置知识点
    - description: 描述内容
    """
    
    MAX_KNOWLEDGE_POINTS = 10000
    
    def __init__(self):
        self._reset_state()
    
    def _reset_state(self):
        """重置解析状态"""
        self.current_subject: Optional[ParsedSubject] = None
        self.current_semester: Optional[ParsedSemester] = None
        self.current_chapter: Optional[ParsedChapter] = None
        self.current_kp_name: Optional[str] = None
        self.current_kp_difficulty: int = 3
        self.current_kp_prerequisite: Optional[str] = None
        self.current_kp_description: List[str] = []
        
        # 排序计数器
        self.semester_order: int = 0
        self.chapter_order: int = 0
        self.kp_order: int = 0
        
        # 解析结果存储
        self.semesters: List[ParsedSemester] = []
        self.chapters: List[ParsedChapter] = []
        self.knowledge_points: List[ParsedKnowledgePoint] = []
    
    def parse(self, content: str) -> KnowledgeGraphParseResult:
        """
        解析 Markdown 格式的知识图谱
        
        Args:
            content: Markdown 格式的知识图谱内容
            
        Returns:
            KnowledgeGraphParseResult: 解析结果
        """
        logger.info("开始解析 Markdown 知识图谱")
        self._reset_state()
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # 一级标题：学科 (#)
            h1_match = re.match(r'^#\s+(.+)$', line)
            if h1_match:
                self._handle_subject(i, h1_match.group(1).strip())
                continue
            
            # 二级标题：学期 (##)
            h2_match = re.match(r'^##\s+(.+)$', line)
            if h2_match:
                self._handle_semester(i, h2_match.group(1).strip())
                continue
            
            # 三级标题：章节 (###)
            h3_match = re.match(r'^###\s+(.+)$', line)
            if h3_match:
                self._handle_chapter(i, h3_match.group(1).strip())
                continue
            
            # 四级标题：知识点 (####)
            h4_match = re.match(r'^####\s+(.+)$', line)
            if h4_match:
                self._handle_knowledge_point(i, h4_match.group(1).strip())
                continue
            
            # 解析知识点属性（非标题行）
            if self.current_kp_name and line_stripped:
                self._parse_knowledge_point_property(i, line_stripped)
        
        # 保存最后一个知识点
        self._save_current_knowledge_point()
        
        # 验证解析结果
        return self._validate_result()
    
    def _handle_subject(self, line_num: int, name: str):
        """处理学科标题"""
        # 保存前一个知识点
        self._save_current_knowledge_point()
        
        # 如果已有学科，记录警告（单次导入只支持一个学科）
        if self.current_subject:
            logger.warning(f"第{line_num}行：检测到多个学科，将只保留第一个学科 '{self.current_subject.name}'")
            return
        
        self.current_subject = ParsedSubject(name=name)
        logger.info(f"解析到学科: {name}")
    
    def _handle_semester(self, line_num: int, name: str):
        """处理学期标题"""
        # 保存前一个知识点
        self._save_current_knowledge_point()
        self.current_kp_name = None
        
        if not self.current_subject:
            logger.warning(f"第{line_num}行：检测到学期 '{name}' 但缺少学科定义")
            return
        
        self.semester_order += 1
        self.current_semester = ParsedSemester(
            name=name,
            subject_name=self.current_subject.name,
            sort_order=self.semester_order
        )
        self.semesters.append(self.current_semester)
        logger.info(f"解析到学期: {name}")
        
        # 重置章节和知识点计数器
        self.chapter_order = 0
        self.kp_order = 0
    
    def _handle_chapter(self, line_num: int, name: str):
        """处理章节标题"""
        # 保存前一个知识点
        self._save_current_knowledge_point()
        self.current_kp_name = None
        
        if not self.current_semester:
            logger.warning(f"第{line_num}行：检测到章节 '{name}' 但缺少学期定义")
            return
        
        self.chapter_order += 1
        self.current_chapter = ParsedChapter(
            name=name,
            semester_name=self.current_semester.name,
            subject_name=self.current_subject.name,
            sort_order=self.chapter_order
        )
        self.chapters.append(self.current_chapter)
        logger.info(f"解析到章节: {name}")
        
        # 重置知识点计数器
        self.kp_order = 0
    
    def _handle_knowledge_point(self, line_num: int, name: str):
        """处理知识点标题"""
        # 保存前一个知识点
        self._save_current_knowledge_point()
        
        if not self.current_chapter:
            logger.warning(f"第{line_num}行：检测到知识点 '{name}' 但缺少章节定义")
            return
        
        self.current_kp_name = name
        logger.debug(f"解析到知识点: {name}")
    
    def _parse_knowledge_point_property(self, line_num: int, line: str):
        """解析知识点属性"""
        # 难度等级：difficulty: 1-5 或 难度: 1-5
        diff_match = re.match(r'^(difficulty|难度)[:：]?\s*([1-5])$', line, re.IGNORECASE)
        if diff_match:
            self.current_kp_difficulty = int(diff_match.group(2))
            logger.debug(f"难度等级: {self.current_kp_difficulty}")
            return
        
        # 前置知识点：prerequisite: 知识点名称 或 前置: 知识点名称
        prereq_match = re.match(r'^(prerequisite|前置|前置知识点)[:：]?\s*(.+)$', line, re.IGNORECASE)
        if prereq_match:
            self.current_kp_prerequisite = prereq_match.group(2).strip()
            logger.debug(f"前置知识点: {self.current_kp_prerequisite}")
            return
        
        # 描述：description: 描述内容 或直接是描述文本
        desc_match = re.match(r'^(description|描述)[:：]?\s*(.*)$', line, re.IGNORECASE)
        if desc_match:
            desc_text = desc_match.group(2).strip()
            if desc_text:
                self.current_kp_description.append(desc_text)
            return
        
        # 其他非空行作为描述的一部分（不以特殊符号开头）
        if not re.match(r'^(#|\*|\-|\d+\.)', line):
            self.current_kp_description.append(line)
    
    def _save_current_knowledge_point(self):
        """保存当前知识点到列表"""
        if self.current_kp_name and self.current_chapter:
            # 合并描述文本
            description_text = '\n'.join(self.current_kp_description).strip() if self.current_kp_description else None
            
            kp = ParsedKnowledgePoint(
                name=self.current_kp_name,
                chapter_name=self.current_chapter.name,
                semester_name=self.current_semester.name,
                subject_name=self.current_subject.name,
                difficulty_level=self.current_kp_difficulty,
                prerequisite_name=self.current_kp_prerequisite,
                description=description_text,
                sort_order=self.kp_order
            )
            self.knowledge_points.append(kp)
            self.kp_order += 1
            
            # 重置知识点属性
            self._reset_knowledge_point_attrs()
    
    def _reset_knowledge_point_attrs(self):
        """重置知识点属性"""
        self.current_kp_name = None
        self.current_kp_difficulty = 3
        self.current_kp_prerequisite = None
        self.current_kp_description = []
    
    def _validate_result(self) -> KnowledgeGraphParseResult:
        """验证解析结果"""
        # 验证知识点数量
        if len(self.knowledge_points) > self.MAX_KNOWLEDGE_POINTS:
            return KnowledgeGraphParseResult(
                success=False,
                message=f"知识点数量超限：{len(self.knowledge_points)}个，最大允许{self.MAX_KNOWLEDGE_POINTS}个",
                stats=self._get_stats()
            )
        
        # 验证完整结构
        if not self.current_subject:
            return KnowledgeGraphParseResult(
                success=False,
                message="缺少学科定义，必须包含至少一个一级标题（#）",
                stats=self._get_stats()
            )
        
        if not self.semesters:
            return KnowledgeGraphParseResult(
                success=False,
                message="缺少学期定义，必须包含至少一个二级标题（##）",
                stats=self._get_stats()
            )
        
        if not self.chapters:
            return KnowledgeGraphParseResult(
                success=False,
                message="缺少章节定义，必须包含至少一个三级标题（###）",
                stats=self._get_stats()
            )
        
        if not self.knowledge_points:
            return KnowledgeGraphParseResult(
                success=False,
                message="缺少知识点定义，必须包含至少一个四级标题（####）",
                stats=self._get_stats()
            )
        
        logger.info(f"Markdown解析完成: {self._get_stats()}")
        
        return KnowledgeGraphParseResult(
            success=True,
            message="Markdown知识图谱解析成功",
            stats=self._get_stats(),
            subject=self.current_subject,
            semesters=self.semesters,
            chapters=self.chapters,
            knowledge_points=self.knowledge_points
        )
    
    def _get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            "subject_count": 1 if self.current_subject else 0,
            "semester_count": len(self.semesters),
            "chapter_count": len(self.chapters),
            "knowledge_point_count": len(self.knowledge_points)
        }


def parse_knowledge_graph_markdown(content: str) -> KnowledgeGraphParseResult:
    """
    解析 Markdown 格式的知识图谱（便捷函数）
    
    Args:
        content: Markdown 格式的知识图谱内容
        
    Returns:
        KnowledgeGraphParseResult: 解析结果
    """
    parser = KnowledgeGraphParser()
    return parser.parse(content)


# ============================================================================
# 单元测试
# ============================================================================

if __name__ == "__main__":
    # 测试用例
    test_content = """# 数学

## 七年级上

### 第一章 有理数

#### 正整数
难度: 3
前置: 无
description: 正整数是大于0的整数

#### 负整数
难度: 4
前置: 正整数
description: 负整数是小于0的整数
"""
    
    result = parse_knowledge_graph_markdown(test_content)
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    print(f"Stats: {result.stats}")
    print(f"Subject: {result.subject}")
    print(f"Semesters: {len(result.semesters)}")
    print(f"Chapters: {len(result.chapters)}")
    print(f"Knowledge Points: {len(result.knowledge_points)}")