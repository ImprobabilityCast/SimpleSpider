
# 3rd party lib
import requests

from HTMLHyperlinkParser import HTMLHyperlinkParser

def printTabs(num):
    s = ""
    while num > 0:
        s += '  '
        num -= 1
    return s

def printNodes(node, indent):
    
    print(printTabs(indent) + node.name)
    for n in node.childList:
        printNodes(n, indent + 1)


def main():
    # tests:
    #   http://localhost/php-manual-en/function.filter-input.html
    #   http:/localhost/
    #
    # Also, compare number of matches with regex split

    response = requests.get("http://localhost/php-manual-en/function.filter-input.html")
    
    parser = HTMLHyperlinkParser(response.text)
    printNodes(parser.doc, 0)

if __name__ == "__main__":
    main()