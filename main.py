import json
from flask_cors import CORS
from flask import Flask
from flask_restful import Resource, Api
from ose.statement import load_statements
from ose.agent import load_agents
from ose.environment import Environment, get_active_agents, filter_by_users

app = Flask(__name__)
api = Api(app)
cors = CORS(app, origin="*")

with open('./data/etab.json') as f:
    etab = json.load(f)

statements = load_statements(
    '../open-student-environment/data'
    '/statements-brneac3-20180301-20180531'
    '.json')
agents = load_agents(
    '../open-student-environment/data'
    '/accounts-brneac3-0-20180630.json')

env = Environment(agents, statements)
nodes, adjancy = env.nodes, env.structure

active_agents = get_active_agents(statements)
nodes, adjancy = filter_by_users(nodes, adjancy, active_agents)

etab = [e for e in etab if e['numero_uai'] in nodes]

nodes = [{'name': n, 'type': nodes[n]} for children in adjancy.values() for n in children]
for node in nodes:
    if node['name'] not in adjancy:
        adjancy[node['name']] = []

adjancy = {k: list(v) for k, v in adjancy.items()}


class GetNodes(Resource):
    def get(self):
        return nodes


class GetAdjancy(Resource):
    def get(self):
        return adjancy


class GetEtab(Resource):
    def get(self):
        return etab


api.add_resource(GetNodes, '/nodes')
api.add_resource(GetAdjancy, '/adjancy')
api.add_resource(GetEtab, '/etab')

if __name__ == '__main__':
    app.run(debug=True)
