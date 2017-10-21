#!/usr/bin/env python
import sys
import os

sys.path.append(os.path.dirname(os.getcwd()))

from sanic import Sanic
from sanic.response import redirect

from instdd.config import HOST, BASE_DIR
from instdd.views.instdd_blueprint import instdd_bp
from instdd.views.except_blueprint import except_bp
from instdd.views.wechat_blueprint import wechat_bp

app = Sanic(__name__)
app.config.REQUEST_TIMEOUT = 600
app.static('/static', BASE_DIR + '/static/')
app.blueprint(instdd_bp)
app.blueprint(except_bp)
app.blueprint(wechat_bp)


@app.middleware('request')
async def check_request(request):
    host = request.headers.get('host', None)
    if not host or host not in HOST:
        return redirect('http://www.google.com')


if __name__ == "__main__":
    app.run(host="127.0.0.1", workers=1, port=8001, debug=True)
