#!/usr/bin/env python
from sanic import Blueprint
from sanic.exceptions import NotFound, ServerError, InvalidUsage
from sanic.response import html, redirect
from jinja2 import Environment, PackageLoader, select_autoescape

except_bp = Blueprint('except_blueprint')

# jinjia2 config
env = Environment(
    loader=PackageLoader('views.except_blueprint', '../templates/except'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']))


def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))


@except_bp.exception(NotFound)
async def ignore_404(request, exception):
    if "google3eabdadc11faf3b3" in request.url:
        return template('google3eabdadc11faf3b3.html')
    return template('404.html')


@except_bp.exception(InvalidUsage)
async def except_invalidUsage(request, exception):
    return redirect('/')


@except_bp.exception(ServerError)
async def test(request, exception):
    return redirect('/')
