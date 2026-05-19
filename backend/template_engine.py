"""
模板引擎 - 简化版

提供模板字符串渲染功能，用于任务执行和验证提示词生成。
"""

import re
from typing import Dict, Any


def render_template_string(template: str, context: Dict[str, Any]) -> str:
    """
    渲染模板字符串，支持 {{variable}} 语法
    
    Args:
        template: 模板字符串，包含 {{variable}} 占位符
        context: 上下文字典，提供变量值
        
    Returns:
        渲染后的字符串
    """
    if not template:
        return ""
    
    if not context:
        return template
    
    def replace_var(match):
        var_name = match.group(1).strip()
        # 支持嵌套属性访问，如 task.name
        value = _get_nested_value(context, var_name)
        if value is None:
            return match.group(0)  # 保持原样
        if isinstance(value, (list, dict)):
            import json
            return json.dumps(value, ensure_ascii=False, indent=2)
        return str(value)
    
    # 匹配 {{variable}} 模式
    pattern = r'\{\{([^}]+)\}\}'
    result = re.sub(pattern, replace_var, template)
    
    return result


def _get_nested_value(obj: Dict[str, Any], key: str) -> Any:
    """
    获取嵌套值，支持点号分隔的路径
    
    Args:
        obj: 字典对象
        key: 键路径，如 "task.name" 或 "items.0.name"
        
    Returns:
        找到的值，或 None
    """
    if not key:
        return None
    
    keys = key.split('.')
    value = obj
    
    for k in keys:
        if value is None:
            return None
        if isinstance(value, dict):
            value = value.get(k)
        elif isinstance(value, list):
            try:
                index = int(k)
                value = value[index] if 0 <= index < len(value) else None
            except ValueError:
                return None
        else:
            return None
    
    return value


def render_template_file(template_path: str, context: Dict[str, Any]) -> str:
    """
    渲染模板文件
    
    Args:
        template_path: 模板文件路径
        context: 上下文字典
        
    Returns:
        渲染后的字符串
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        return render_template_string(template, context)
    except FileNotFoundError:
        raise FileNotFoundError(f"模板文件不存在: {template_path}")
    except Exception as e:
        raise Exception(f"渲染模板文件失败: {e}")
