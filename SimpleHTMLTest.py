
# 3rd party lib
import requests

from simpleHTML import parse

def printTabs(num):
    s = ""
    while num > 0:
        s += '  '
        num -= 1
    return s

def printNodes(node, indent):
    
    print(printTabs(indent) + '<' + node.name + ' ' + str(node.attributes) + '>')
    for n in node.childList:
        printNodes(n, indent + 1)
    print(printTabs(indent) + '</' + node.name + '>')

def printLinks(node):
    nodes = node.getElementsByTagNames("a")
    toPrint = []
    for n in nodes:
       # if 'href' in n.attributes and n.attributes['href'] not in toPrint:
        toPrint.append(n.attributes['href'])
        #    print(n.attributes['href'])
    print(len(toPrint))
    

def main():
    # tests:
    #   http://localhost/php-manual-en/function.filter-input.html
    #   http://localhost/
    #   "<html><body><div><div></div></div></body></html>"
    #   "<html><body><div content pigs='null' turkey='' knife='egg\\'bacon'><p></p></div></body></html>"
    #
    # these make it parse slow:
    #   http://localhost/php-manual-en/indexes.examples.html
    #   http://localhost/php-manual-en/indexes.functions.html
    #

    response2 = requests.get("http://localhost/php-manual-en/indexes.examples.html")
    
    print("Parsing...")
    
    doc = parse(response2.text)
    printNodes(doc, 0)
    printLinks(doc)

if __name__ == "__main__":
    main()
