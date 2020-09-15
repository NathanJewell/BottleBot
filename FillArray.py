import yaml
from Filler import Filler
from flask import Flask, request, jsonify, abort
import threading

default_config_file = "BasicFillConfig.yaml"
default_config = None
with open(default_config_file, "r") as dconf:
    default_config = yaml.load(dconf)

filler_names = ["Lab", "Collie", "Poodle"]

fillers = []

for name in filler_names:
    config = None
    try:
        #found existing config for ("name")
        with open("config/{}_config.yaml".format(name), "r") as specific_config:
            config = yaml.load(specific_config)
    except Exception as e:
        #no config found
        config = default_config

    fillers.append(Filler(name, config))

fillerdict = dict(zip(filler_names, fillers))

app = Flask(__name__, static_url_path='', static_folder='site/static')

@app.route('/names')
def names():
    return jsonify({ "names" : filler_names })

@app.route('/stats/<name>')
def stats(name):
    if name in fillerdict:
        return jsonifyf(fillerdict[name].status_json())
    else:
        abort(400, "Filler with name {} does not exist.".format(name))

@app.route('/status/<name>', methods=['POST'])
def setstatus(name):
    if name in fillerdict:
        filler = fillerdict[name]
        if not request.json or not 'status' in request.json:
            abort(400, "No request data.")
        try:
            success = filler.set_status(request.status)
            if success != 1:
                raise Exception
        except Exception as e:
            abort(400, "Desired status not recognized")
        return jsonify(filler.status_json())
    else:
        abort(400, "Filler with name {} does not exist.".format(name))

threading.Thread(target=app.run).start()






