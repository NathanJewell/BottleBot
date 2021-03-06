import yaml
from Filler import Filler
from flask import Flask, request, jsonify, abort
import threading
import sys

default_config_file = sys.argv[1] if len(sys.argv) > 1 else "BasicFillConfig.yaml"
default_config = None
with open(default_config_file, "r") as dconf:
    default_config = yaml.load(dconf)

filler_names = [k['name'] for k in default_config["filler_list"]]

fillers = []
pin_order = ["proximity_gpio", "fill_gpio", "co2_gpio", "beer_gpio"]

for nameindex, name in enumerate(filler_names):
    config = None
    try:
        #found existing config for ("name")
        with open("config/{}.yaml".format(name), "r") as specific_config:
            config = yaml.load(specific_config)
    except Exception as e:
        #no config found
        config = default_config

    pins = [default_config["filler_list"][nameindex][pin_name] for pin_name in pin_order]
    fillers.append(Filler(name, config, pins))

fillerdict = dict(zip([n.lower() for n in filler_names], fillers))
print(fillerdict)

app = Flask(__name__, static_url_path='', static_folder='site/static')

@app.route('/names')
def names():
    return jsonify({ "names" : filler_names })

@app.route('/stats/<name>')
def stats(name):
    if name.lower() in fillerdict:
        return jsonify(fillerdict[name.lower()].status_json())
    else:
        abort(400, "Filler with name {} does not exist.".format(name))

@app.route('/status/<name>', methods=['POST'])
def setstatus(name):
    if name.lower() in fillerdict:
        filler = fillerdict[name.lower()]
        if not request.json or not 'status' in request.json:
            abort(400, "No request data.")
        try:
            success = filler.set_status(request.json['status'])
            if success != 1:
                raise Exception
        except Exception as e:
            abort(400, "Desired status not recognized: '{}'".format(request.json['status']))
        return jsonify(filler.status_json())
    else:
        abort(400, "Filler with name {} does not exist.".format(name))

@app.route('/trigger/<name>', methods=['POST'])
def triggerfill(name):
    if name.lower() in filldict:
        filler = fillerdict[name.lower()]

    else:
        abort(400, "Filler with name {} does not exist.".format(name))

@app.route('/pdb')
def pdb():
   """Enter python debugger in terminal"""

   import sys
   print("\n'/pdb' endpoint hit. Dropping you into python debugger. globals:")
   print("%s\n" % dir(sys.modules[__name__]))
   import pdb; pdb.set_trace()

   return 'After PDB debugging session, now execution continues...'

@app.after_request # blueprint can also be app~~
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = '*'
    return response

app.run()
#threading.Thread(target=app.run).start()






