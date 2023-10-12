from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_cors import CORS

import sys
sys.path.append('backend')
from backend import Backend

import json


app = Flask(__name__)
CORS(app)


# API


@app.route('/api/clouds', methods=['GET'])
def api_clouds_get():
    ctx = Backend()
    ctx.save_ctx('db')
    return ctx.get_clouds()


@app.route('/api/cloud/<int:id>/sync', methods=['POST'])
def api_cloud_sync(id: int):
    ctx = Backend()
    ctx.save_ctx('db')
    return ctx.cloud_sync(id)


@app.route('/api/cloud/<int:id>', methods=['DELETE'])
def api_cloud_delete(id: int):
    ctx = Backend()
    ctx.save_ctx('db')
    return ctx.cloud_delete(id)


@app.route('/api/cloud', methods=['POST'])
def api_cloud_add():
    reqCloud = request.get_json()
    ctx = Backend()
    ctx.save_ctx('db')
    return ctx.cloud_add(reqCloud)


@app.route('/api/map', methods=['GET'])
def api_cloud_map():
    ctx = Backend()
    ctx.save_ctx('db')
    return ctx.cloud_map()


@app.route('/api/vm/<int:vm_id>/links')
def api_get_vm_links(vm_id: int):
    ctx = Backend()
    ctx.save_ctx('db')
    return ctx.get_vm_links(vm_id)


@app.route('/api/storages', methods=['GET'])
def api_storages_list():
    ctx = Backend()
    ctx.save_ctx('db')
    return ctx.storages_list()


@app.route('/api/classifiers', methods=['GET'])
def api_classifiers_list():
    ctx = Backend()
    ctx.save_ctx('db')
    return ctx.classifiers_list()


@app.route('/api/classification', methods=['POST'])
def api_classification_build():
    # get data from frontend
    sel = request.get_json()
    ctx = Backend()
    ctx.save_ctx('db')
    return ctx.classification_build(sel)


@app.route('/api/classification2', methods=['POST'])
def api_classification_build2():
    # get data from frontend
    sel = request.get_json()
    ctx = Backend()
    ctx.save_ctx('db')
    return ctx.classification_build2(sel)


@app.route('/api/analyzation', methods=['GET'])
def api_analyze_links():
    ctx = Backend()
    ctx.save_ctx('db')
    return ctx.analyze_links()


@app.route('/api/header-info', methods=['GET'])
def api_get_header_info():
    ctx = Backend()
    ctx.save_ctx('db')
    return ctx.get_header_info()


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
