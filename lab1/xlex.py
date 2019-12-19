import re
_op_prior_rank = {'|':0,'&':1,'*':2,'(':-1,')':-1}
class Stack:
    def __init__(self):
        self.op_stack =[] # operation stack 
        self.output = []
    def push(self,c):
        # get the top from the stack 
        if self.op_stack == []:
            _stack_top = None
        else:
            _stack_top = self.op_stack[-1] 
        # push the op into stack 
        if c == '(':
            self.op_stack.append(c)
        elif c == '&' or c == '*' or c == '|':
            # with the higher priority stack top ,pop up;
            while(_stack_top != None  and  _op_prior_rank[c]  <= _op_prior_rank[_stack_top]):
                _pop_out = self.op_stack.pop() 
                self.output.append(_pop_out)
                if self.op_stack != []:
                    _stack_top = self.op_stack[-1] 
                else:
                    _stack_top = None 
            self.op_stack.append(c)
        elif c == ')':
            # pop all the element till the '('
            _pop_out = self.op_stack.pop()
            while (_pop_out != '('):
                self.output.append(_pop_out)
                _pop_out = self.op_stack.pop()
        elif c == '\#':
            # reach the end,pop all in op stack to output
            while(True):
                if(self.op_stack != []):
                    _pop_out = self.op_stack.pop()
                    self.output.append(_pop_out)
                else:
                    break
        else:
            # other letters`
            self.output.append(c) 
    def get_result(self):
        return self.output

#dd 
class Expr():
    def __init__(self,start_node,accept_node):
        self.start_node = start_node
        self.accept_node = accept_node
# interpet the oss list into nfa structure 
class NFA(dict):
    def __init__(self):
        self._i = -1
        self.start_node = -1
        self.accept_node = -1
    def new_node(self):
        self._i = self._i + 1
        self[self._i] = []
        return   self._i
    def add_edge(self,node,ch,to_node):
        self[node].append((to_node,ch))

class DFA(dict):
    def __init__(self):
        self.start_node = -1
        self.accept_nodes = []
    def new_node(self,node):
        self[node] = []
    def add_edge(self,node,ch,to_node):
        self[node].append((to_node,ch))
    def set_accept_node(self,node):
        self.accept_nodes.append(node)
    def transfer(self,node,c):
        _next_state = -1
        for edge in self[node]:
            if edge[1] == c:
                _next_state = edge[0]
        return _next_state



 
# transfer re string to operation-suffix-structure(oss)
# rules 1. when encounter a "not operation" char ,put in output queue directly
# rules 2. when encounter a ")" ,pop all element from the operations stack till the ")"
# rules 3. when enconter operation,i.e '&','|','*',if the priority of the top-op--stack >= it, pop up the top 
# into the out_put queue,till the top <= it,
# rules 4. when reach the end, pop all in the op-stack into the output queue
# the priority sequence * > & > |
def re_to_OSS(re):
    # flags to assist for adding '&'
    need_op = False
    re= re+'\#'
    re_stack = Stack()
    re = iter(list(re))
    try:
        c  = re.next()
        while(True):
            if c == '(':
                if need_op:
                    re_stack.push('&')
                    need_op =  False
                re_stack.push(c)
            elif c  == ')':
                re_stack.push(c)
                need_op = True
            elif c ==  '|':
                need_op = False
                re_stack.push(c)
            elif c == '*':
                need_op = True
                re_stack.push(c)
            else:
                if c == "\\":
                    c = c + re.next()
                if c != "\\#":
                    if need_op:
                        re_stack.push('&')
                        need_op = False
                    else:
                        need_op =True
                re_stack.push(c)
            c = re.next()
    except StopIteration:
        return   re_stack.get_result()


# expr: [start_node,end_node]
def OSS_to_NFA(oss_list):
    nfa = NFA()
    expr_stack  = []
    for c in oss_list:
        if c ==  '&':
            expr_2 = expr_stack.pop()
            expr_1 = expr_stack.pop()
            # add new edge to expr_2 
            nfa.add_edge(expr_1.accept_node,'\e',expr_2.start_node)
            # 2 expr merges as 1
            new_expr = Expr(expr_1.start_node,expr_2.accept_node)
            expr_stack.append(new_expr)
        elif c == '|':
            # new node_1 ,node_2
            expr_2 = expr_stack.pop()
            expr_1 = expr_stack.pop()
            node_1 = nfa.new_node() #new start node
            nfa.add_edge(node_1,'\e',expr_2.start_node)
            nfa.add_edge(node_1,'\e',expr_1.start_node)
            node_2 = nfa.new_node() #new accept node
            nfa.add_edge(expr_2.accept_node,'\e',node_2)
            nfa.add_edge(expr_1.accept_node,'\e',node_2)
            new_expr = Expr(node_1,node_2)
            expr_stack.append(new_expr)
        elif c == '*':
            expr = expr_stack.pop()
            node_1 = nfa.new_node() #new start node
            node_2 = nfa.new_node() #new accept node
            nfa.add_edge(node_1,'\e',expr.start_node)
            nfa.add_edge(node_1,'\e',node_2)
            nfa.add_edge(expr.accept_node,'\e',expr.start_node)
            nfa.add_edge(expr.accept_node,'\e',node_2)
            new_expr = Expr(node_1,node_2)
            expr_stack.append(new_expr)
        else:
            # plain-char 
            node_1 = nfa.new_node() #start node
            node_2 = nfa.new_node()# end node
            nfa.add_edge(node_1,c,node_2)
            #push in  stack for later use
            expr = Expr(node_1,node_2)
            expr_stack.append(expr)
    expr  = expr_stack.pop()
    nfa.start_node = expr.start_node
    nfa.accept_node = expr.accept_node
    return nfa 

def eps_closure(node,nfa,closure):
    closure.append(node)
    _all_set = nfa[node]
    for edge in _all_set:
        if edge[1] == '\e' and edge[0] not in closure:
            eps_closure(edge[0],nfa,closure)

# subset construction algo
def NFA_to_DFA(nfa):
    dfa = DFA()
    work_list = []
    Q = []
    q0 = []
    eps_closure(nfa.start_node,nfa,q0)
    Q.append(q0)
    work_list.append(q0)
    # add q0 in DFA
    dfa.new_node(Q.index(q0))
    dfa.start_node = Q.index(q0)
    while(work_list != []):
        head = work_list[0]
        work_list.remove(head)
        # loop all ascii (0-255) 
        for a in range(0,0xFF):
            move_a = []
            for node in head:
                edges = nfa[node]
                for edge in edges:
                    if edge[1] != '\e' and edge[1] == chr(a):
                        move_a.append(edge[0])
            if(move_a != []):
                q = []
                for node in move_a:
                    eps_closure(node,nfa,q)
                if q not in Q:
                    # put q in Q, add q in worklist,then add new node in DFA , make char a-transfer egde
                    Q.append(q)
                    work_list.append(q)
                    dfa.new_node(Q.index(q))
                    if nfa.accept_node in q:
                        dfa.set_accept_node(Q.index(q)) # set this subset as an accept node
                    dfa.add_edge(Q.index(head),chr(a),Q.index(q))
                else:
                    dfa.add_edge(Q.index(head),chr(a),Q.index(q))
    return dfa        

def g_index(G,node):
    index = -1
    for g in G:
        if node in g:
            index = G.index(g)
            break
    return index
         
# using the char c to split the group g
def split_group(g, G,c ,dfa):
    _d  = {}
    for node in g:
        next_state = dfa.transfer(node,c)
        # the index of g contains next_state
        index = g_index(G,next_state)
        if _d.has_key(index):
            _d[index].append(node)
        else:
            _d[index] = [node]
    return _d.values()


    

# minimize the nodes in DFA    
# hopcroft algo.
def minimize_DFA(dfa):
    N  = [] # not accept 
    A = [] # accept
    for k in dfa.keys():
        if k in dfa.accept_nodes:
            A.append(k)
        else:
            N.append(k)
    G = [N,A,[-1]] # add the dead status (-1) group 
    G_new = []
    # splited the group until no char a can split
    while(True):
        for g in G:
            # skip single node g and dead state node ([-1]) 
            if len(g) <= 1 or g == [-1]:
                G_new.append(g)
            else:
                for c in range(0,0xFF):
                    # splited_g looks like  [[],[]]
                    splited_g = split_group(g,G,chr(c),dfa)
                    if len(splited_g)  > 1 :
                        break
                G_new.extend(splited_g)
        if G != G_new:
            G = G_new
            G_new = []
        else:
            break
    G.pop() # pop the [-1]
    # orgnize the new mini DFA 
    # set the sub-group g as the new dfa's node 
    # select one node in g,add go through it's  old dfa's edge,
    # transfer these edges as new dfa edge 
    mini_dfa =  DFA()
    for g in G:
        node = g[0]
        new_node = G.index(g)
        new_edges = []
        edges = dfa[node]
        for edge in edges:
            new_edge = (g_index(G,edge[0]),edge[1])
            if new_edge not in new_edges:
                new_edges.append(new_edge)
        mini_dfa[new_node] = new_edges
    mini_dfa.start_node = g_index(G,dfa.start_node)
    for accept_node in dfa.accept_nodes:
        new_accept_node = g_index(G,accept_node)
        if new_accept_node not in mini_dfa.accept_nodes:
            mini_dfa.accept_nodes.append(new_accept_node)
    return mini_dfa    

class Pattern_Table(list):
    def __init__(self):
        self.start_node = -1
        self.accept_nodes = []
def DFA_to_table(dfa):
    pt = Pattern_Table()
    nodes = dfa.keys()
    nodes.sort()
    for node in nodes:
        pt.append([-1]*256)
        edges = dfa[node]
        for edge in edges:
            pt[node][ord(edge[1])] = edge[0]
    pt.start_node = dfa.start_node
    pt.accept_nodes = dfa.accept_nodes 
    return pt

class Pattern():
    def __init__(self,re):
        _oss = re_to_OSS(re)
        _nfa = OSS_to_NFA(_oss)
        _dfa = NFA_to_DFA(_nfa)
        _mini_dfa = minimize_DFA(_dfa)
        self._pattern_table = DFA_to_table(_mini_dfa)

    def match(self,str):
        _len = len(str)
        forward = 0
        for lex_begin in range(0,len(str)):
            forward  = lex_begin 
            state  = self._pattern_table.start_node
            stack  = []
            while(state != -1 and forward < len(str)):
                c  = str[forward]
                if state in self._pattern_table.accept_nodes:
                    stack = []
                stack.append(state)
                state = self._pattern_table[state][ord(c)]
                forward = forward + 1  
            while(state not in self._pattern_table.accept_nodes and stack != []):
                state = stack.pop()
                forward = forward - 1
            if( forward != lex_begin):
                return (lex_begin,forward)
        return (-1)
            

p = Pattern('(if)*')
print p.match("ifififififi")
    