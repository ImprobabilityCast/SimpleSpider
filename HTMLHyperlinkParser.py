from collections import deque

# recursively parse HTML from string
# if a closing tag is found, but it does not match the current one
# "go back" and find the last tag that matches it, treat everything between
# as plaintext.
# look out for self closing tags

# Testing - Try these pages:
#   http://localhost/php-manual-en/function.filter-input.html
#
# Also, compare number of matches with regex split

# Poor grammar
#
# DOCUMENT: { < ? xml PLAIN_TEXT ? > } { <! DOCTYPE PLAIN_TEXT > } HTML
#
# HTML : TAG | PLAIN_TEXT
# TAG : !-- PLAIN_TEXT -- | HTML_TAG
# HTML_TAG : < TAG_NAME { ATTRIBUTE } /> | < TAG_NAME { ATTRIBUTE } > HTML </ SAME_TAG_NAME >
# TAG_NAME : TEXT
# ATTRIBUTE : TEXT = ATTR_VALUE
# ATTR_VALUE : ' PLAIN_TEXT ' | " PLAIN_TEXT "
# PLAIN_TEXT : anything
# TEXT : no WHITESPACE
#
# WHITESPACE ' ' | &nbsp; | '\r' | '\n' | '\t'

# Tokenize? - No.
# TERMINAL_SYMBOLS : ' " / < > = !
#  TEXT WHITESPACE

# parse(string, index)

class HTMLNode:
    def __init__(self, nodeName):
        self.name = nodeName
        self.childList = []
        self.attributes = dict()
        self.parent = None

    def appendChild(self, node):
        self.childList.append(node)
        node.parent = self


class Tokenizer:
    def __init__(self):
        self.removeTokens = set(["\n", "\r", "\t", " "])
        self.breakOnTokens = set(["<", ">", "?", "!", "/", "-"])

    def nextTokenOrTrash(self, text, idx):
        pos = idx
        isToken = text[idx] in self.removeTokens
        while (pos < len(text) and (isToken == (text[pos] in self.removeTokens))
                and text[pos] not in self.breakOnTokens):
            pos += 1
        if pos == idx:
            pos += 1
        return text[idx:pos]

    def tokenize(self, text):
        result = deque()
        idx = 0
        while idx < len(text):
            token = self.nextTokenOrTrash(text, idx)
            idx += len(token)
            if token[0] not in self.removeTokens:
                result.append(token)
        return result


class HTMLHyperlinkParser:
    def __init__(self, htmlDoc):
        tok = Tokenizer()
        self.doc = self.parseDoc(tok.tokenize(htmlDoc))

    def extractThruToStr(self, chars, tokens):
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

    def parseDoc(self, chars):
        if chars.popleft() == '<':
            second = chars.popleft()
            if second == '?':
                self.extractThruToStr(chars, '?>')
                return self.parseDoc(chars)
            elif second == '!':
                self.extractThruToStr(chars, '>')
                return self.parseDoc(chars)
            else:
                chars.appendleft(second)
                return self.parseHTML(chars)
        else:
            return None

    def parseHTML(self, chars):
        node = HTMLNode(chars.popleft().lower())

        # parse attributes
        attributes = self.extractThruToStr(chars, '>')
        for a in attributes:
            node.attributes["foo"] = a

        # if not self-closing tag
        if len(attributes) < 2 or attributes[-2] != '/':
            tokens = self.extractThruToStr(chars, ['<', '/', node.name, '>'])
            # ignore script nodes
            if node.name == 'script' or node.name == 'style':
                return node
            
            while tokens.pop() != '<':
                pass
            
            while True:
                # skip text nodes
                self.extractThruToStr(tokens, '<')

                # skip comments
                if len(tokens) > 0:
                    tok = tokens.popleft()
                    if tok == '!':
                        self.extractThruToStr(tokens, '-->')
                    else:
                        tokens.appendleft(tok)
                
                if len(tokens) > 0:
                    node.appendChild(self.parseHTML(tokens))
                else:
                    break
        return node


