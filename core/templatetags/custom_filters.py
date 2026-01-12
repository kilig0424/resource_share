from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter(name='highlight')
def highlight(text, query):
    """在文本中高亮显示搜索关键词"""
    if not text or not query:
        return text

    # 转义查询词中的特殊字符
    pattern = re.escape(query)

    # 使用正则表达式替换，不区分大小写
    highlighted = re.sub(
        f'({pattern})',
        r'<span class="highlight">\1</span>',
        str(text),
        flags=re.IGNORECASE
    )

    return mark_safe(highlighted)