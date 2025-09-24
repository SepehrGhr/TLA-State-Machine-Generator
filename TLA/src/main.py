from TLA.src.Grammar import Grammar
from Variable import Variable

grammar = Grammar()
n = int(input("Enter the number of rules: "))
start_name = ""

for i in range(n):
    temp = input(f"Enter rule {i + 1}: ")
    if i == 0:
        start_name = temp[0]
    grammar.ogGrammar.append(temp)
    new_var = Variable(grammar, temp)
    if not new_var.is_regular():
        raise Exception("This grammar is not regular we can't generate a state machine")
    grammar.allVars.append(new_var)
    grammar.ogVariables.append(new_var.name)

grammar.adjust(start_name)
start = grammar.find_var(start_name)
ans = False
for rule in start.rules:
    ans = ans or start.ends_with_terminal(rule)

if not ans:
    raise Exception("this grammar is not correct")

# for var in grammar.allVars:
#     var.print()

grammar.generate_state_machine()
