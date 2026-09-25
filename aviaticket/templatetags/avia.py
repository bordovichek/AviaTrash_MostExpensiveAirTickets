from datetime import timedelta

from django import template

register = template.Library()

NBSP = " "


@register.filter
def rub(value) -> str:
    """12500 → «12 500 ₽»."""
    if value in (None, ""):
        return ""
    return f"{int(value):,}".replace(",", NBSP) + f"{NBSP}₽"


@register.filter
def plural_ru(number, forms: str) -> str:
    """{{ 5|plural_ru:"рейс,рейса,рейсов" }} → «рейсов»."""
    one, few, many = forms.split(",")
    number = abs(int(number))
    if number % 10 == 1 and number % 100 != 11:
        return one
    if 2 <= number % 10 <= 4 and not 12 <= number % 100 <= 14:
        return few
    return many


@register.filter
def duration(value: timedelta | None) -> str:
    """timedelta(hours=2, minutes=5) → «2 ч 05 мин»."""
    if value is None:
        return ""
    minutes = int(value.total_seconds()) // 60
    hours, minutes = divmod(minutes, 60)
    if not hours:
        return f"{minutes}{NBSP}мин"
    return f"{hours}{NBSP}ч {minutes:02d}{NBSP}мин"


@register.filter
def transfers(count: int) -> str:
    if not count:
        return "Прямой рейс"
    return f"{count}{NBSP}{plural_ru(count, 'пересадка,пересадки,пересадок')}"
