# Imports

import os
from flask import Flask, request, Response, send_from_directory
import json as js

from automata.fa.dfa import DFA
from automata.fa.nfa import NFA

from visual_automata.fa.dfa import VisualDFA
from visual_automata.fa.nfa import VisualNFA

from urllib.parse import urlparse


# Setup

app = Flask(__name__)
project_dir = os.path.dirname(os.path.abspath(__file__))

def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)

    return obj


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/pics/<path:path>')
def send_js(path):
    return send_from_directory('pics', path)


## JSON
# {
#     "states": [
#         "A", "B", "C", "D"
#         ],
#     "input_sym": [
#         "a", "b"
#     ],
#     "transitions": {
#         "A": {"a": "B", "b": "D"},
#         "B": {"a": "B", "b": "C"},
#         "C": {"a": "B", "b": "C"},
#         "D": {"a": "D", "b": "D"}
#     },
#     "initial": "A",
#     "final": ["C"]
# }

@app.route("/dfa", methods=["POST"])
def calc_DFA():
    json = request.json
    states = set(json["states"])
    input_sym = set(json["input_sym"])
    transitions = json["transitions"]
    initial = json["initial"]
    final = set(json["final"])

    dfa = DFA(
        states = states,
        input_symbols = input_sym,
        transitions = transitions,
        initial_state = initial,
        final_states = final,
        allow_partial = True
    )

    imgPath = os.path.join(project_dir, "pics")

    ## DFA
    dfa_filename = "dfa"
    visualDfa = VisualDFA(dfa)
    visualDfa.show_diagram(filename = dfa_filename, path = imgPath)

    ## Complement DFS
    complement_dfa_filename = "dfa-complement"
    complement_dfa = ~dfa
    visualDfaComplement = VisualDFA(complement_dfa)
    visualDfaComplement.show_diagram(filename = complement_dfa_filename, path = imgPath)

    # Reverse NFA
    reverse_nfa_filename = "nfa-reverse"
    nfa = NFA.from_dfa(dfa)
    n = nfa.reverse()

    n = VisualNFA(n)
    t = n.transitions
    t['new'] = t[0]
    del t[0]
    t['new']['ε'] = t['new']['']
    del t['new']['']
    n.initial_state = 'new'
    n.input_symbols.add('ε')
    n.transitions = t
    n.states.remove(0)

    n.show_diagram(filename = reverse_nfa_filename, path = imgPath) 

    o = urlparse(request.base_url)
    host = o.hostname
    port = o.port

    result = {
        "dfa_link": "http://{}:{}/pics/{}.png".format(host, port ,dfa_filename),
        "complement_dfa_link": "http://{}:{}/pics/{}.png".format(host, port, complement_dfa_filename),
        "reverse_nfa_link": "http://{}:{}/pics/{}.png".format(host, port, reverse_nfa_filename)
    }

    json_str = js.dumps(result, default = serialize_sets)

    return Response(json_str, mimetype="application/json")

# on running python app.py
if __name__ == "__main__":
    app.run(debug=True)
