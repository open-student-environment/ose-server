from flask_cors import CORS
from flask import Flask
from flask_restful import Resource, Api
from ose.statement import load_statements
from ose.agent import load_agents
from ose.environment import Environment, get_active_agents, filter_by_users

app = Flask(__name__)
api = Api(app)
cors = CORS(app, origin="*") 

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

all_nodes = set()

for v in adjancy.values():
	if v is not []:
		for i in v:
			all_nodes.add(i)

adjancy = {k: list(v) for k, v in adjancy.items()}

leafs  = all_nodes.difference(set(adjancy.keys()))

for l in leafs:
	adjancy[l] = []


# env.plot_group_activity(153565, keep_inactive=False)

class GetNodes(Resource):
    def get(self):
        return nodes


class GetAdjancy(Resource):
    def get(self):
        return adjancy


api.add_resource(GetNodes, '/nodes')
api.add_resource(GetAdjancy, '/adjancy')

if __name__ == '__main__':
    app.run(debug=True)
