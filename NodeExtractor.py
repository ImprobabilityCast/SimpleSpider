from typing import ByteString
from typing import Iterable
from collections import deque

from HTMLNode import HTMLNode
import simpleHTML
import tokenizer


def extractNamedNodes(text: str, names: Iterable) -> set:
    tokens = tokenizer.tokenize(text)
    simpleHTML.skipDoc(tokens)
    return _extractNodes(tokens, names)


# length of chars must be > 0
def _extractNodes(chars: deque, names: str) -> set:
    node = HTMLNode(chars.popleft().lower())
    result = set()

    # parse attributes
    attributes = simpleHTML.extractThruToStr(chars, '>')
    node.attributes = simpleHTML.parseAttributes(attributes)

    if node.name in names:
        result.add(node)

    # if not self-closing tag or something like a meta tag
    if attributes[0] == '>' and node.name not in simpleHTML._zeroChildNames:
        # ignore script nodes
        if node.name == 'script' or node.name == 'style':
            simpleHTML.discardThruToStr(chars, ['<', '/', node.name, '>'])
            return result
        
        while len(chars) > 0:
            # skip text nodes
            simpleHTML.discardThruToStr(chars, '<')

            if chars[0] == '!':
                # skip comments
                simpleHTML.discardThruToStr(chars, '-->')
            elif chars[0] == '/':
                simpleHTML.discardThruToStr(chars, '>')
                break
            else:
                result.update(_extractNodes(chars, names))

    return result