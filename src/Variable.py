import random


def is_terminal(token):
    if token.startswith("\""):
        return True
    return False


class Variable:
    var_counter = 0

    def __init__(self, grammar, all_rules):
        self.grammar = grammar
        left_right = all_rules.split("=::")
        self.name = left_right[0].strip()
        self.RHS = left_right[1].strip().replace("\"eps\"", "\"\"")
        self.all = all_rules.strip()
        self.rules = self.RHS.split("|")
        self.isLoop = self.RHS.startswith("{") and self.RHS.endswith("}")
        self.isOptional = self.RHS.startswith("[") and self.RHS.endswith("]")
        self.isValid = True
        self.adjust_loops()
        self.adjust_optionals()
        self.isValid = self.is_grammar()
        self.all = f"{self.name} =:: {"|".join(self.rules)}"
        self.find_terminals()

    def adjust_loops(self):
        if self.isLoop:
            return

        for z in range(len(self.rules)):
            thisRule = self.rules[z].split(",")
            for i in range(len(thisRule)):
                thisRule[i] = thisRule[i].strip()

                if thisRule[i].startswith("{"):
                    if thisRule[i].endswith("}"):
                        rand_name = random.randint(0, 9)
                        self.rules[z] = self.rules[z].replace(thisRule[i], str(rand_name))
                        self.grammar.allVars.append(
                            Variable(self.grammar, f"{rand_name}=:: {thisRule[i]}")
                        )

                    else:
                        if i != len(thisRule) - 1:
                            rand_name = random.randint(0, 9)
                            self.rules[z] = self.rules[z].replace(f"{thisRule[i]},{thisRule[i + 1]}", str(rand_name))
                            self.grammar.allVars.append(
                                Variable(self.grammar, f"{rand_name}=:: {thisRule[i]},{thisRule[i + 1]}")
                            )

    def adjust_optionals(self):
        if self.isOptional:
            self.rules[0] = self.rules[0].strip("[")
            self.rules[0] = self.rules[0].strip("]")
            self.rules.append("\"\"")
            return

        for z in range(len(self.rules)):
            thisRule = self.rules[z].split(",")
            for i in range(len(thisRule)):
                thisRule[i] = thisRule[i].strip()

                if thisRule[i].startswith("["):
                    if thisRule[i].endswith("]"):
                        rand_name = random.randint(0, 9)
                        self.rules[z] = self.rules[z].replace(thisRule[i], str(rand_name))
                        thisRule[i] = thisRule[i].strip("[")
                        thisRule[i] = thisRule[i].strip("]")
                        self.grammar.allVars.append(
                            Variable(self.grammar, f"{rand_name}=:: {thisRule[i]} | \"\"")
                        )

                    else:
                        if i != len(thisRule) - 1:
                            rand_name = random.randint(0, 9)
                            self.rules[z] = self.rules[z].replace(f"{thisRule[i]},{thisRule[i + 1]}", str(rand_name))
                            thisRule[i] = thisRule[i].strip("[")
                            thisRule[i + 1] = thisRule[i + 1].strip("]")
                            self.grammar.allVars.append(
                                Variable(self.grammar, f"{rand_name}=:: {thisRule[i]},{thisRule[i + 1]} | \"\"")
                            )

    def find_terminals(self):
        for rule in self.rules:
            this_rule = rule.split(",")
            for token in this_rule:
                token.strip(" ")
                if token.startswith("{") or token.endswith("}"):
                    token = token.strip("{")
                    token = token.strip("}")
                elif token.startswith("[") or token.endswith("]"):
                    token = token.strip("[")
                    token = token.strip("]")
                if is_terminal(token) and not self.grammar.terminals.__contains__(token):
                    self.grammar.terminals.append(token)

    def ends_with_terminal(self, token):
        token = token.strip(" ")
        if token.startswith("{") and token.endswith("}"):
            token = token.strip("{")
            token = token.strip("}")
        elif token.startswith("[") and token.endswith("]"):
            token = token.strip("[")
            token = token.strip("]")
        if is_terminal(token):
            return True
        if "," not in token:
            var = self.grammar.find_var(token.strip(" "))
            if var is None:
                raise Exception("Not all variables are defined")
            return var.isValid
        thisRule = token.split(",")
        ans = True
        for section in thisRule:
            ans = ans and self.ends_with_terminal(section)
        return ans

    def is_grammar(self):
        allContainV = True
        for i in range(len(self.rules)):
            thisRule = self.rules[i].split(",")
            thisContains = False
            for j in range(len(thisRule)):
                thisRule[j] = thisRule[j].strip(" ")
                if not thisRule[j].startswith("\""):
                    if self.name in thisRule[j]:
                        thisContains = True
            if not thisContains:
                allContainV = False
                break
        return not allContainV

    def is_deterministic(self, first_chars):
        if not self.isValid:
            return first_chars, True
        for i in range(len(self.rules)):
            thisRule = self.rules[i].strip(" ")
            thisRule = thisRule.strip("{")
            thisRule = thisRule.strip("}")
            thisRule = thisRule.strip("[")
            thisRule = thisRule.strip("]")
            if thisRule.startswith("\""):
                if first_chars.__contains__(thisRule[1]):
                    return first_chars, False
                first_chars.append(thisRule[1])
            else:
                rule_sections = thisRule.split(",")
                rule_sections[0] = rule_sections[0].strip(" ")
                rule_sections[0] = rule_sections[0].strip("{")
                rule_sections[0] = rule_sections[0].strip("}")
                rule_sections[0] = rule_sections[0].strip(" ")
                rule_sections[0] = rule_sections[0].strip("[")
                rule_sections[0] = rule_sections[0].strip("]")
                rule_sections[0] = rule_sections[0].strip(" ")
                var = self.grammar.find_var(rule_sections[0])
                first_chars, status = var.is_deterministic(first_chars)
                if not status:
                    return first_chars, False
        return first_chars, True

    def is_regular(self):
        for i in range(len(self.rules)):
            thisRule = self.rules[i].split(",")
            for j in range(len(thisRule)):
                thisRule[j] = thisRule[j].strip(" ")
                if not thisRule[j].startswith("\""):
                    if self.name in thisRule[j] and j != 0 and j != len(thisRule) - 1:
                        return False
        return True

    def generate_var(self, graph, token=None):
        unique_id = Variable.var_counter
        Variable.var_counter += 1
        var = self.grammar.find_var(self.name)
        self.grammar.visitedVars[self.grammar.allVars.index(var)] = True

        if not self.isValid:
            node_name = f"dead_{unique_id}" if token is None else f"dead_{unique_id}{token}"
            node_color = "blue"

            graph.add_node(node_name, color=node_color)
            return f"{node_name}"

        node_name = f"{self.name}_{unique_id}" if token is None else f"{self.name}_{unique_id}{token}"
        node_color_s = "lightgreen" if self.name == self.grammar.start else "lightblue"
        node_color_s = "pink" if self.name == self.grammar.start and self.isLoop else node_color_s
        node_color_f = "pink" if self.name == self.grammar.start else "lightblue"

        graph.add_node(node_name, color=node_color_s)

        if self.isLoop:
            self.iterate_through_rules(graph, node_name, node_name)
        else:
            final_node = f"{node_name}_f"
            graph.add_node(final_node, color=node_color_f)
            self.iterate_through_rules(graph, node_name, final_node)

        return node_name

    def iterate_through_rules(self, graph, prev_var, last_var):
        og_prev = prev_var
        og_last = last_var
        for i in range(len(self.rules)):
            thisRule = self.rules[i].split(",")
            transition = ""
            prev_var = og_prev
            last_var = og_last
            death_of_rule = False
            for j in range(len(thisRule)):
                thisRule[j] = thisRule[j].strip("{")
                thisRule[j] = thisRule[j].strip("}")
                thisRule[j] = thisRule[j].strip(" ")
                if is_terminal(thisRule[j]):
                    transition = transition.strip("\"")
                    thisRule[j] = thisRule[j].strip("\"")
                    transition = f"\"{transition}{thisRule[j]}\""
                else:
                    var = self.grammar.find_var(thisRule[j])
                    if var is None:
                        raise Exception("Undefined Variable")
                    node_name = var.generate_var(graph, "\'")
                    if "dead" in node_name:
                        transition = transition.strip(" ")
                        transition = transition if transition != "" and transition != "\"\"" else "eps"
                        graph.add_edge(prev_var, node_name, label=transition)
                        death_of_rule = True
                        continue
                    transition = transition if transition != "" and transition != "\"\"" else "eps"
                    graph.add_edge(prev_var, node_name, label=transition)
                    prev_var = f"{node_name}_f" if f"{node_name}_f" in graph.nodes else f"{node_name}"
                    transition = ""
            if not death_of_rule:
                transition = transition if transition != "" and transition != "\"\"" else "eps"
                graph.add_edge(prev_var, last_var, label=transition)

    def print(self):
        print(f"{self.all}")
