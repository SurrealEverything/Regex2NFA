# -*- coding: utf-8 -*-
"""
Created on Thu Feb 28 22:19:23 2019

@author: gabih
"""
stateCounts = 0


class NFAState:

    # idx
    # isFinal
    # onChar
    # onEmpty

    def __init__(self):
        global stateCounts
        self.idx = stateCounts
        stateCounts += 1
        self.isFinal = False
        self.onChar = [[] for x in range(256)]
        self.onEmpty = []

    def addCharEdge(self, c, nxt):
        """
         Add a transition edge from this state to next which consumes
        the character c.
        """
        self.onChar[ord(c)].append(nxt)

    def addEmptyEdge(self, nxt):
        """
        Add a transition edge from this state to next that does not consume a
        character.
        """
        self.onEmpty.append(nxt)

    def matches(self, s, visited=[]):
        """
        When matching, we work character by character.

        If we're out of characters in the string, we'll check to
        see if this state is final, or if we can get to a final
        state from here through empty edges.

        If we're not out of characters, we'll try to consume a
        character and then match what's left of the string.

        If that fails, we'll ask if empty-edge neighbors can match
        the entire string.

        If that fails, the match fails.

        Note: Because we could have a circular loop of empty
        transitions, we'll have to keep track of the states we
        visited through empty transitions so we don't end up
        looping forever.
        """

        if self in visited:
            """
            We've found a path back to ourself through empty edges;
            stop or we'll go into an infinite loop.
            """
            return False

        """
        In case we make an empty transition, we need to add this
        state to the visited list.
        """
        visited.append(self)

        if len(s) == 0:
            """
            The string is empty, so we match this string only if
            this state is a final state, or we can reach a final
            state without consuming any input.
            """
            if (self.isFinal):
                return True

            """
            Since this state is not final, we'll ask if any
            neighboring states that we can reach on empty edges can
            match the empty string.
            """
            for nxt in self.onEmpty:
                if nxt.matches("", visited):
                    return True

            return False

        else:
            """
            In this case, the string is not empty, so we'll pull
            the first character off and check to see if our
            neighbors for that character can match the remainder of
            the string.
            """

            c = ord(s[0])

            for nxt in self.onChar[c]:
                if len(s) > 1:
                    if nxt.matches(s[1:]):
                        return True
                else:
                    if nxt.matches(""):
                        return True

            """
            It looks like we weren't able to match the string by
            consuming a character, so we'll ask our
            empty-transition neighbors if they can match the entire
            string.
            """
            for nxt in self.onEmpty:
                if nxt.matches(s, visited):
                    return True

            return False

    def printState(self):

        print('STATE ' + str(self.idx)
              + (' (final):' if self.isFinal else ':'))

        null = True

        if self.onEmpty != []:
            print('On empty: ')
            null = False
        for nxt in self.onEmpty:
            print(nxt.idx)

        for charId, val in enumerate(self.onChar):
            if val != []:
                null = False
                print('On "' + chr(charId) + '": ')
                for nxt in self.onChar[charId]:
                    print(nxt.idx)

        if null:
            print('NULL')

        print('\n')

    def printFromState(self, visited=[]):

        if self in visited:
            return visited

        visited.append(self)

        self.printState()

        for nxt in self.onEmpty:
            visited = nxt.printFromState(visited)

        for charId, val in enumerate(self.onChar):
            for nxt in val:
                visited = nxt.printFromState(visited)

        return visited


class NFA:
    """
    Here, an NFA is represented by a startingState and a finalState.

    Any NFA can be represented by an NFA with a single finalState state by
    creating a special finalState state, and then adding empty transitions
    from all final states to the special one.
    """

    # idx
    # startingState
    # finalState

    def __init__(self, *args):
        if len(args) == 0:
            self = self.empty()
        else:
            startingState = args[0]
            finalState = args[1]
            self.startingState = startingState
            self.finalState = finalState

    def matches(self, s):
        return self.startingState.matches(s)

    def empty():
        """empty() : Creates an NFA which matches the empty string."""
        startingState = NFAState()
        finalState = NFAState()
        startingState.addEmptyEdge(finalState)
        finalState.isFinal = True
        return NFA(startingState, finalState)

    def char(c):
        """char() : Creates an NFA which just matches the character 'c'."""
        startingState = NFAState()
        finalState = NFAState()
        finalState.isFinal = True
        startingState.addCharEdge(c, finalState)
        return NFA(startingState, finalState)

    def kleene(nfa):
        """
        rep() : Creates an NFA which matches zero or more repetitions
        of the given NFA.
        """
        nfa.finalState.addEmptyEdge(nfa.startingState)
        nfa.startingState.addEmptyEdge(nfa.finalState)
        return nfa

    def concat(first, second):
        """
        concat() : Creates an NFA that matches a sequence of the
        two provided NFAs.
        """
        first.finalState.isFinal = False
        second.finalState.isFinal = True
        first.finalState.addEmptyEdge(second.startingState)
        return NFA(first.startingState, second.finalState)

    def union(choice1, choice2):
        """union() : Creates an NFA that matches either provided NFA."""
        choice1.finalState.isFinal = False
        choice2.finalState.isFinal = False
        startingState = NFAState()
        finalState = NFAState()
        finalState.isFinal = True
        startingState.addEmptyEdge(choice1.startingState)
        startingState.addEmptyEdge(choice2.startingState)
        choice1.finalState.addEmptyEdge(finalState)
        choice2.finalState.addEmptyEdge(finalState)
        return NFA(startingState, finalState)

    def printNFA(self):
        print('NFA:\n')
        self.startingState.printFromState()


class regExp:

    def parse(reStr):
        """"parse() : Parses string into corresponding NFA function calls"""

        operators = []
        operands = []

        for char in reStr:

            if char not in'()*|.':
                operands.append(NFA.char(char))
            elif char == '*':
                starredNFA = operands.pop()
                operands.append(NFA.kleene(starredNFA))
            elif char in '.|(':
                operators.append(char)
            else:
                opCount = 0

                opChar = operators[-1]

                if opChar == '(':
                    continue

                operators.pop()
                opCount += 1
                while operators[-1] != '(':
                    operators.pop()
                    opCount += 1

                operators.pop()

                if opChar == '.':
                    for _ in range(opCount):
                        op2 = operands.pop()
                        op1 = operands.pop()
                        operands.append(NFA.concat(op1, op2))

                elif opChar == '|':
                    for _ in range(opCount):
                        op2 = operands.pop()
                        op1 = operands.pop()
                        operands.append(NFA.union(op1, op2))

        return operands[-1]


# add () around . operations
regExp.parse('((a|(b.b))*.(c.((a.b)|(b.a))*)*)').printNFA()
