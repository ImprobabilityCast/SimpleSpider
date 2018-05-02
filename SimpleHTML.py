from collections import deque

import tokenizer
from HTMLNode import HTMLNode


class SimpleHTML:
    
    _zeroChildNames = frozenset({'meta', 'link', 'hr', 'br'})
    
    def __init__(self, htmlText):
        self.parseDoc(tokenizer.tokenize(htmlText))

    def parseDoc(self, chars):
        if chars.popleft() == '<':
            second = chars.popleft()
            if second == '?':
                SimpleHTML.extractThruToStr(chars, '?>')
                self.parseDoc(chars)
            elif second == '!':
                SimpleHTML.extractThruToStr(chars, '>')
                self.parseDoc(chars)
            else:
                chars.appendleft(second)
                self.doc = SimpleHTML.parseHTML(chars)

    @staticmethod
    def extractThruToStr(chars, tokens):
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

    # '>' or '/>' must be a suffix of achars
    @staticmethod
    def parseAttributes(achars):
        result = dict()
        while len(achars) > 0 and achars[0] != '>' and achars[0] != '/':
            name = achars.popleft()
            value = deque()
            if achars[0] == '=':
                achars.popleft()
                sep = achars.popleft()
                while True:
                    partial = SimpleHTML.extractThruToStr(achars, sep)
                    partial.pop()
                    value.extend(partial)
                    if len(partial) > 0 and value[-1] == '\\':
                        value.append(sep)
                    else:
                        break
            result[name] = ''.join(value)
        return result

    # length of chars must be > 0
    @staticmethod
    def parseHTML(chars):
        node = HTMLNode(chars.popleft().lower())

        # parse attributes
        attributes = SimpleHTML.extractThruToStr(chars, '>')
        node.attributes = SimpleHTML.parseAttributes(attributes)

        # if not self-closing tag or something like a meta tag
        if attributes[0] == '>' and node.name not in SimpleHTML._zeroChildNames:
            # ignore script nodes
            if node.name == 'script' or node.name == 'style':
                SimpleHTML.extractThruToStr(chars, ['<', '/', node.name, '>'])
                return node
            
            while len(chars) > 0:
                # skip text nodes
                SimpleHTML.extractThruToStr(chars, '<')

                if chars[0] == '!':
                    # skip comments
                    SimpleHTML.extractThruToStr(chars, '-->')
                elif chars[0] == '/':
                    SimpleHTML.extractThruToStr(chars, '>')
                    break
                else:
                    node.appendChild(SimpleHTML.parseHTML(chars))

        return node


