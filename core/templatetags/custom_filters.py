import hashlib
from django import template

register = template.Library()

@register.filter(name='md5')
def md5(value):
    """Aplica o hash MD5 a uma string"""
    return hashlib.md5(value.strip().lower().encode('utf-8')).hexdigest()
