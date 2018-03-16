import re


def main():
    testReg = re.compile("((f|ht)tps?://)")

    test = "s"
    if testReg.search(test) == None:
        print("Passed: " + test)
    else:
        print("Failed: " + test)

    test = "http"
    if testReg.search(test) == None:
        print("Passed: " + test)
    else:
        print("Failed: " + test)
        
    test = "ftp"
    if testReg.search(test) == None:
        print("Passed: " + test)
    else:
        print("Failed: " + test)
        
    test = "https"
    if testReg.search(test) == None:
        print("Passed: " + test)
    else:
        print("Failed: " + test)
        
    test = "://"
    if testReg.search(test) == None:
        print("Passed: " + test)
    else:
        print("Failed: " + test)

    test = ":"
    if testReg.search(test) == None:
        print("Passed: " + test)
    else:
        print("Failed: " + test)
        
    test = "http:/"
    if testReg.search(test) == None:
        print("Passed: " + test)
    else:
        print("Failed: " + test)

    test = "http://"
    if testReg.search(test) != None:
        print("Passed: " + test)
    else:
        print("Failed: " + test)
    
    test = "https://"
    if testReg.search(test) != None:
        print("Passed: " + test)
    else:
        print("Failed: " + test)
    
    test = "www"
    if testReg.search(test) == None:
        print("Passed: " + test)
    else:
        print("Failed: " + test)

    test = "www."
    if testReg.search(test) == None:
        print("Passed: " + test)
    else:
        print("Failed: " + test)

    test = "http://www"
    if testReg.search(test) != None:
        print("Passed: " + test)
    else:
        print("Failed: " + test)

    test = "http://www."
    if testReg.search(test) != None:
        print("Passed: " + test)
    else:
        print("Failed: " + test)
    
    test = "."
    if testReg.search(test) == None:
        print("Passed: " + test)
    else:
        print("Failed: " + test)


if __name__ == "__main__":
    main()
