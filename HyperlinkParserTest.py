
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
    
    print(printTabs(indent) + '<' + node.name + '>')
    for n in node.childList:
        printNodes(n, indent + 1)
    print(printTabs(indent) + '</' + node.name + '>')


def main():
    # tests:
    #   http://localhost/php-manual-en/function.filter-input.html
    #   http://localhost/
    #   "<html><body><div><div></div></div></body></html>"
    #
    # Also, compare number of matches with regex split

    response2 = requests.get("http://localhost/")
    
    print("Parsing...")
    
    parser = HTMLHyperlinkParser(response2.text)
    #parser = HTMLHyperlinkParser("<html><body><div><div></div></div></body></html>")
    printNodes(parser.doc, 0)

if __name__ == "__main__":
    main()