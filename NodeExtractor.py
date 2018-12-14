from typing import ByteString
from typing import Iterable
from collections import deque

from HTMLNode import HTMLNode
import simpleHTML
import tokenizer


def extractNamedNodes(text: str, names: Iterable) -> set:
    tokens = tokenizer.tokenize(text)
    simpleHTML.skipDoc(tokens)
    result = set()
    while len(tokens) > 0:
        node = _extractNodes(tokens, names)
        if node is not None:
            result.add(node)
    return result


# length of chars must be > 0
def _extractNodes(chars: deque, names: Iterable) -> set:
    node = HTMLNode(chars.popleft().lower())

    # parse attributes
    attributes = simpleHTML.extractThruToStr(chars, '>')
    node.attributes = simpleHTML.parseAttributes(attributes)

    # if not self-closing tag or something like a meta tag
    # if attributes[0] == '>' and node.name not in simpleHTML._zeroChildNames:
        # ignore script and style nodes
    if node.name == 'script' or node.name == 'style':
        simpleHTML.discardThruToStr(chars, ['<', '/', node.name, '>'])
    
    while len(chars) > 0:
        # skip text nodes
        simpleHTML.discardThruToStr(chars, '<')

        if chars[0] == '!':
            # skip comments
            simpleHTML.discardThruToStr(chars, '-->')
        elif chars[0] == '/':
            # skip end tags
            simpleHTML.discardThruToStr(chars, '>')
        else:
            # found a new node
            break

    if node.name in names:
        return node
    else:
        return None
