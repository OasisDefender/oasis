from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS

import json

from cloud          import Cloud
from db             import DB
from cloud_map      import CloudMap, cloud_map_encoder
from internet_nodes import InternetNodes, internet_nodes_encoder
from links          import Links, link_encoder
from fw_aws         import FW_AWS
from fw_azure       import FW_Azure
from fw             import FW_Selected, FW_Selected_encoder
from vm_rules       import VM_Rules

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return redirect(url_for('clouds'))


@app.route('/clouds', methods=['GET'])
def clouds():
    return clouds_with_error(msg=None)
    
@app.route('/clouds/e/<string:msg>', methods=['GET'])
def clouds_with_error(msg: str):
    context = DB()
    clouds = context.get_clouds()
    return render_template('clouds.jinja', clouds=clouds, errorMsg=msg)

@app.route('/clouds/add', methods=['POST'])
def clouds_add():
    retmsg = ""
    context = DB()
    cloud = Cloud(id=-1,
                  name=request.form['name'],
                  cloud_type=request.form['cloud_type'],
                  aws_region=request.form['aws_region'],
                  aws_key=request.form['aws_key'],
                  aws_secret_key=request.form['aws_secret_key'],
                  azure_subscription_id=request.form['azure_subscription_id'],
                  azure_tenant_id=request.form['azure_tenant_id'],
                  azure_client_id=request.form['azure_client_id'],
                  azure_client_secret=request.form['azure_client_secret'])
    context.add_cloud(cloud)
    if cloud.id > 0:
        save_cloud_id = cloud.id
        fw            = None
        if cloud.cloud_type.upper() == 'AWS':
            fw = FW_AWS()
        if cloud.cloud_type.upper() == 'AZURE':
            fw = FW_Azure()
        if fw != None:
            if cloud.id == fw.connect(cloud.id):
                fw.get_topology(cloud.id)
            else:                                
                context.delete_cloud(save_cloud_id)
                retmsg = f"Cant connect to cloud: '{cloud.name}' ({cloud.cloud_type}) - no valid credentials!"
                return redirect(url_for('clouds_with_error', msg=retmsg))
        else:                        
            context.delete_cloud(save_cloud_id)
            retmsg = f"Cloud Type: '{cloud.cloud_type}' - not supported!"
            return redirect(url_for('clouds_with_error', msg=retmsg))
    else:
        retmsg = f"DB error: cant insert new cloud! Already exists?"
        return redirect(url_for('clouds_with_error', msg=retmsg))    
    return redirect(url_for('clouds'))        


@app.route('/clouds/delete', methods=['POST'])
def clouds_delete():
    id = request.form['id']
    context = DB()
    context.delete_cloud(id)
    return redirect(url_for('clouds'))

@app.route('/cloud/<int:id>/sync', methods=['POST'])
def clouds_sync(id: int):    
    fw      = None
    context = DB()
    retmsg  = ""
    retval  = 200
    cloud: Cloud = None

    for cloud in context.get_clouds():
        if cloud.id == id:
            if cloud.cloud_type == 'AWS':
                fw = FW_AWS()
                break
            if cloud.cloud_type == 'AZURE':
                fw = FW_Azure()
                break
            retmsg = f"Cloud Type: '{cloud.cloud_type}' - not supported!"
            retval = 500
    if fw != None:
        context.sync_cloud(cloud.id)
        fw.connect(cloud.id)
        fw.get_topology(cloud.id)
    return retmsg, retval

@app.route('/vm/<int:vm_id>/links')
def get_vm_links(vm_id: int):
    l = Links(vm_id)
    l.get()
    lines = json.dumps(l, default=link_encoder, ensure_ascii=False)
    r = VM_Rules(vm_id)
    rules = json.dumps(r.to_dict())
    reply = f"{{\"links\": {lines}, \"rules\": {rules}}}"
    return reply

@app.route('/vm/<int:vm_id>/links/delete', methods=['POST'])
def links_delete(vm_id: int):
    retmsg  = ""
    retval  = 200
    ids: list[int] = request.get_json()
    rules = VM_Rules(vm_id)
    rules.delete_rules(ids)
    return retmsg, retval


@app.route('/cloudmap')
def cloud_map():
    map = CloudMap()
    map.get()
    vpcs = json.dumps(map, default=cloud_map_encoder, ensure_ascii=False)
    
    inodes = InternetNodes()
    inodes.get()
    internetNodes = json.dumps(inodes, default=internet_nodes_encoder, ensure_ascii=False)
    
    db = DB()
    services = db.get_service_names()
    
    return render_template('cloud_map.jinja', vpcs=vpcs, internetNodes=internetNodes, services=services)

@app.route('/cloudmap/addrule', methods=['POST'])
def add_rule():
    data: list[dict] = []
    data = request.get_json()
    for d in data:
        print(d)
        #jsn = json.loads(d)
        fw = FW_Selected(d)
        #print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}]: {json.dumps(fw, default=FW_Selected_encoder, ensure_ascii=False)}")
        fw.add_rules()
        fw.sync_rules()

    #print(data)
    return "success", 200

# API

@app.route('/api/clouds', methods=['GET'])
def api_clouds_get():
    context = DB()
    clouds = context.get_clouds()
    # ICloudView
    return [ c.to_dict() for c in clouds ]

@app.route('/api/cloud/<int:id>/sync', methods=['POST'])
def api_cloud_sync(id: int):
    fw      = None
    context = DB()
    retmsg  = ""
    retval  = 200
    cloud: Cloud = None

    for cloud in context.get_clouds():
        if cloud.id == id:
            if cloud.cloud_type == 'AWS':
                fw = FW_AWS()
                break
            if cloud.cloud_type == 'AZURE':
                fw = FW_Azure()
                break
            retmsg = f"Cloud Type: '{cloud.cloud_type}' - not supported!"
            retval = 500
    if fw != None:
        context.sync_cloud(cloud.id)
        fw.connect(cloud.id)
        fw.get_topology(cloud.id)
    return retmsg, retval

@app.route('/api/cloud/<int:id>', methods=['DELETE'])
def api_cloud_delete(id: int):    
    context = DB()
    context.delete_cloud(id)
    return "", 200

@app.route('/api/cloud', methods=['POST'])
def api_cloud_add():
    context = DB()
    reqCloud = request.get_json()
    reqCloud["cloud_type"] = reqCloud["cloud_type"].upper()
    
    # Sanitize
    cloud_type = reqCloud['cloud_type']
    if cloud_type == "AWS":
        cloud = Cloud(id=-1,
                    name=reqCloud['name'],
                    cloud_type=reqCloud['cloud_type'],
                    aws_region=reqCloud['aws_region'],
                    aws_key=reqCloud['aws_key'],
                    aws_secret_key=reqCloud['aws_secret_key'],
                    azure_subscription_id=None,
                    azure_tenant_id=None,
                    azure_client_id=None,
                    azure_client_secret=None)
    elif cloud_type == "AZURE":
        cloud = Cloud(id=-1,
                    name=reqCloud['name'],
                    cloud_type=reqCloud['cloud_type'],
                    aws_region=None,
                    aws_key=None,
                    aws_secret_key=None,
                    azure_subscription_id=reqCloud['azure_subscription_id'],
                    azure_tenant_id=reqCloud['azure_tenant_id'],
                    azure_client_id=reqCloud['azure_client_id'],
                    azure_client_secret=reqCloud['azure_client_secret'])
    else:
        return "Unsupported cloud type", 500
    
    # Add to DB
    context.add_cloud(cloud)
    if cloud.id <= 0:    
        return "Can't insert new cloud! Already exists?", 500
    
    # Test cloud    
    save_cloud_id = cloud.id
    fw            = None
    if cloud.cloud_type == 'AWS':
        fw = FW_AWS()
    if cloud.cloud_type == 'AZURE':
        fw = FW_Azure()
    if fw != None:
        if cloud.id == fw.connect(cloud.id):
            fw.get_topology(cloud.id)
        else:                                
            context.delete_cloud(save_cloud_id)
            return f"Can't connect to cloud: '{cloud.name}' ({cloud.cloud_type}). Bad credentials?", 500   
    
    return cloud.to_dict(), 200

@app.route('/api/map')
def api_cloud_map():
    map = CloudMap()
    map.get()
    vpcs = cloud_map_encoder(map)

    inodes = InternetNodes()
    inodes.get()
    internetNodes = internet_nodes_encoder(inodes) 

    result = {
        "vpcs": vpcs,
        "inodes": internetNodes
    }
    
    return json.dumps(result, ensure_ascii=False), 200
    

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
