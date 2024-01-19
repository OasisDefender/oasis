from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_cors import CORS
import json

import sys
sys.path.append('..')

from backend import Backend

userid:str = None

app = Flask(__name__)
CORS(app)


def create_json_response(statusCode: int, jsonBody: str):
    result = {
        'statusCode': statusCode,
        'headers': {
        },
        'body': None
    }
    if jsonBody:
        result['headers']['Content-Type'] = 'application/json'
        result['body'] = jsonBody
    return result


# API
@app.route('/api/init', methods=['GET'])
def api_init():
    ctx = Backend()
    ctx.save_ctx(userid)
    status, body = ctx.init_backend()
    return json.dumps(body), status

@app.route('/api/clouds', methods=['GET'])
def api_clouds_get():
    ctx = Backend()
    ctx.save_ctx(userid)
    status, body = ctx.get_clouds()
    return json.dumps(body), status


@app.route('/api/cloud/<int:id>/sync', methods=['POST'])
def api_cloud_sync(id: int):
    ctx = Backend()
    ctx.save_ctx(userid)
    status, body = ctx.cloud_sync(id)
    return json.dumps(body), status


@app.route('/api/cloud/<int:id>', methods=['DELETE'])
def api_cloud_delete(id: int):
    ctx = Backend()
    ctx.save_ctx(userid)
    status, body = ctx.cloud_delete(id)
    return json.dumps(body), status


@app.route('/api/cloud', methods=['POST'])
def api_cloud_add():
    reqCloud = request.get_json()
    ctx = Backend()
    ctx.save_ctx(userid)
    status, body = ctx.cloud_add(reqCloud)
    return json.dumps(body), status


@app.route('/api/map', methods=['GET'])
def api_cloud_map():
    ctx = Backend()
    ctx.save_ctx(userid)
    status, body = ctx.cloud_map()
    return json.dumps(body), status


@app.route('/api/vm/<int:vm_id>/links')
def api_get_vm_links(vm_id: int):
    ctx = Backend()
    ctx.save_ctx(userid)
    status, body = ctx.get_vm_links(vm_id)
    return json.dumps(body), status


@app.route('/api/storages', methods=['GET'])
def api_storages_list():
    ctx = Backend()
    ctx.save_ctx(userid)
    status, body = ctx.storages_list()
    return json.dumps(body), status


@app.route('/api/classifiers', methods=['GET'])
def api_classifiers_list():
    ctx = Backend()
    ctx.save_ctx(userid)
    status, body = ctx.classifiers_list()
    return json.dumps(body), status


@app.route('/api/classification2', methods=['POST'])
def api_classification_build2():
    # get data from frontend
    sel = request.get_json()
    ctx = Backend()
    ctx.save_ctx(userid)
    status, body = ctx.classification_build2(sel)
    return json.dumps(body), status


@app.route('/api/analyzation', methods=['GET'])
def api_analyze_links():
    ctx = Backend()
    ctx.save_ctx(userid)
    status, body = ctx.analyze_links()
    return json.dumps(body), status


@app.route('/api/analyzation/resultsvisualisation1', methods=['GET'])
def api_visualisation1():
    ctx = Backend()
    ctx.save_ctx('db')
    status, body = ctx.analyze_results1()
    return json.dumps(body), status


@app.route('/api/analyzation/resultsvisualisation2', methods=['GET'])
def api_visualisation2():
    ctx = Backend()
    ctx.save_ctx('db')
    status, body = ctx.analyze_results2()
    return json.dumps(body), status


@app.route('/api/header-info', methods=['GET'])
def api_get_header_info():
    ctx = Backend()
    ctx.save_ctx(userid)
    status, body = ctx.get_header_info()
    return json.dumps(body), status


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
