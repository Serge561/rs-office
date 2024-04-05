"""asdasdasdasdas."""

from django import template

register = template.Library()


@register.simple_tag
def breadcrumb_schema():
    """sadsdasdasd."""
    return "http://schema.org/BreadcrumbList"


@register.inclusion_tag("includes/breadcrumbs/breadcrumb_home.html")
def breadcrumb_home(url="home", title=""):
    """asdasdasdasd."""
    return {"url": url, "title": title}


@register.inclusion_tag("includes/breadcrumbs/breadcrumb_item.html")
def breadcrumb_item(url, title, position):
    """asdasdasdasd."""
    return {"url": url, "title": title, "position": position}


@register.inclusion_tag("includes/breadcrumbs/breadcrumb_active.html")
def breadcrumb_active(url, title, position):
    """asdasdasdasd."""
    return {"url": url, "title": title, "position": position}
