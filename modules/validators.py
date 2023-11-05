from rest_framework import serializers
import re


class TitleValidation:
    """Класс валидирует поле <title> модели Module на отсутствие запрещенных слов. Если таковы имеются, то
    возбудится исключение."""

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        errors = {}
        banned_words = r'(.*)(биржа|казино|криптовалюта|крипта|дешево|бесплатно|обман|полиция|радар)(.*)'
        current_title = value.get('title')
        if re.match(banned_words, current_title, flags=re.IGNORECASE):
            errors['banned_words'] = 'Нельзя публиковать запрещенные материалы'
        if errors:
            raise serializers.ValidationError(errors)
