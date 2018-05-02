from collections import deque
from typing import Iterable

import tokenizer
from HTMLNode import HTMLNode


_zeroChildNames = frozenset({'meta', 'link', 'hr', 'br'})

# parses html text into a tree of html nodes
def parse(text: str) -> HTMLNode:
    tokens = tokenizer.tokenize(text)
    skipDoc(tokens)
    return parseNode(tokens)

# parses tokenized html text
def skipDoc(chars: deque):
    if chars[0] == '<':
        first = chars.popleft()
        second = chars.popleft()
        if second == '?':
            discardThruToStr(chars, '?>')
            skipDoc(chars)
        elif second == '!':
            discardThruToStr(chars, '>')
            skipDoc(chars)
        else:
            chars.appendleft(second)
            chars.appendleft(first)

def extractThruToStr(chars: deque, tokens) -> deque:
    result = deque()
    currentMatch = deque()
    while len(chars) > 0 and len(currentMatch) != len(tokens):
        ch = chars.popleft()
        if tokens[len(currentMatch)] == ch:
            currentMatch.append(ch)
        else:
            currentMatch.clear()
        result.append(ch)
    return result

def discardThruToStr(chars: deque, tokens):
    currentMatch = deque()
    while len(chars) > 0 and len(currentMatch) != len(tokens):
        ch = chars.popleft()
        if tokens[len(currentMatch)] == ch:
            currentMatch.append(ch)
        else:
            currentMatch.clear()

# '>' or '/>' must be a suffix of achars
def parseAttributes(achars: deque) -> dict:
    result = dict()
    while len(achars) > 0 and achars[0] != '>' and achars[0] != '/':
        name = achars.popleft()
        value = deque()
        if achars[0] == '=':
            achars.popleft()
            sep = achars.popleft()
            while True:
                partial = extractThruToStr(achars, sep)
                partial.pop()
                value.extend(partial)
                if len(partial) > 0 and value[-1] == '\\':
                    value.append(sep)
                else:
                    break
        result[name] = ''.join(value)
    return result

# length of chars must be > 0
def parseNode(chars: deque) -> HTMLNode:
    node = HTMLNode(chars.popleft().lower())

    # parse attributes
    attributes = extractThruToStr(chars, '>')
    node.attributes = parseAttributes(attributes)

    # if not self-closing tag or something like a meta tag
    if attributes[0] == '>' and node.name not in _zeroChildNames:
        # ignore script nodes
        if node.name == 'script' or node.name == 'style':
            extractThruToStr(chars, ['<', '/', node.name, '>'])
            return node
        
        while len(chars) > 0:
            # skip text nodes
            discardThruToStr(chars, '<')

            if chars[0] == '!':
                # skip comments
                discardThruToStr(chars, '-->')
            elif chars[0] == '/':
                discardThruToStr(chars, '>')
                break
            else:
                node.childList.append(parseNode(chars))

    return node

