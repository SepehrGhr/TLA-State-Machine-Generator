import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import to_pydot


class Grammar:
    def __init__(self):
        self.allVars = []
        self.start = None
        self.G = nx.MultiDiGraph()
        self.visitedVars = []
        self.terminals = []
        self.ogGrammar = []
        self.ogVariables = []

    def adjust(self, start):
        self.start = start
        for i in range(len(self.allVars)):
            if self.allVars[i].name == start:
                temp = self.allVars[i]
                self.allVars[i] = self.allVars[0]
                self.allVars[0] = temp

    def set_visited(self):
        for i in range(len(self.allVars)):
            self.visitedVars.append(False)

    def generate_state_machine(self):
        self.set_visited()
        start = self.allVars[0]
        start.generate_var(self.G, "")
        node_colors = [data["color"] for _, data in self.G.nodes(data=True)]
        pos = nx.spring_layout(self.G)
        nx.draw(self.G, pos, with_labels=True, node_size=2000, node_color=node_colors, font_size=10)
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=nx.get_edge_attributes(self.G, "label"))

        pydot_graph = to_pydot(self.G)

        for node in pydot_graph.get_nodes():
            node_name = node.get_name()
            color = self.G.nodes[node_name]["color"]
            node.set_style("filled")
            node.set_fillcolor(color)

        pydot_graph.set_graph_defaults(dpi=300)
        pydot_graph.write_png("state_machine.png")
        plt.clf()
        img = plt.imread("state_machine.png")

        plt.imshow(img)
        plt.axis("off")
        plt.show()
        self.write_results_to_file()

    def find_var(self, name):
        for i in range(len(self.allVars)):
            if self.allVars[i].name == name:
                return self.allVars[i]
        return None

    def num_of_states(self):
        return len(self.G.nodes)

    def unreachable_states(self):
        unreachableStates = []
        for i in range(len(self.allVars)):
            if not self.visitedVars[i]:
                unreachableStates.append(self.allVars[i].name)
        return unreachableStates

    def dead_states(self):
        deadStates = [node for node in self.G.nodes() if self.G.out_degree(node) == 0 and self.G.nodes[node].get("color") != "pink"]
        return deadStates

    def write_results_to_file(self):

        with open("state_machine_details.txt", "w") as file:

            file.write(f"Grammar : \n")
            for var in self.ogGrammar:
                file.write(f"{var}\n")
            file.write(f"\n")

            file.write(f"Variables : \n")
            for i, var in enumerate(self.ogVariables):
                rest = ", " if i != len(self.ogVariables)-1 else ""
                file.write(f"{var}{rest}")
            file.write(f"\n\n")

            file.write(f"Terminals : \n")
            for i, var in enumerate(self.terminals):
                rest = ", " if i != len(self.terminals) - 1 else ""
                var = var.strip("\"")
                file.write(f"{var}{rest}")
            file.write(f"\n\n")

            file.write(f"Number of States: {self.num_of_states()}\n")

            file.write(f"Number of Transitions: {self.num_of_transitions()}\n")

            unreachable_states = self.unreachable_states()

            if len(unreachable_states) != 0:
                file.write(f"Unreachable Variables: {', '.join(unreachable_states)}\n")
            else:
                file.write("Unreachable Variables: None\n")

            dead_states = self.dead_states()
            if len(dead_states) != 0:
                file.write(f"Dead States: {', '.join(dead_states)}\n")
            else:
                file.write("Dead States: None\n")

            file.write(f"is Grammar Deterministic : {self.is_deterministic()}\n")
            file.write(f"is State Machine Deterministic : {self.is_machine_deterministic()}")

    def is_deterministic(self):
        for i in range(len(self.allVars)):
            first_chars = []
            if not self.allVars[i].is_deterministic(first_chars)[1]:
                return False
        return True

    def has_duplicate_edge_labels(self):
        for node in self.G.nodes():
            label_to_targets = {}

            for _, target, data in self.G.out_edges(node, data=True):
                label = data.get("label")

                if label in label_to_targets:

                    if target not in label_to_targets[label]:
                        return True
                else:
                    label_to_targets[label] = set()

                label_to_targets[label].add(target)

        return False

    def is_machine_deterministic(self):
        return not self.has_duplicate_edge_labels()

    def num_of_transitions(self):
        return len(self.G.edges)
