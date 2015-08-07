# -*- coding:utf-8 -*-
from flask import render_template
from cm_console.api import app


@app.route('/webfront/hello', methods=['GET', ])
def index():
    return render_template('hello.html')
