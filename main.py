import sys
import os

from Crawler import Crawler

def printHelp():
    print("""web.cse.crawler - v1.and.only
    This thingy downloads all the files it can find at the supplied URL. It does
    not download things from other domains from the one specified. It does not
    download things from a path above the supplied one. All the downloaded files
    will be saved in a directory named with the domain name of the URL.
            
USEAGE: main.py URL [DIR] [OPTION]

URL: The URL to scrape
DIR: (Optional) place to save the downloaded files. Defaults to the current directory
OPTION:
    --clean     Start afresh, don't load saved url lists

For example:

    spider.py https://www.unicornsareamazing.com/red/green/blue

Will try to download everything in blue. It will download these:

    https://www.unicornsareamazing.com/red/green/blue/birds/hawk.html
    https://www.unicornsareamazing.com/red/green/blue/penguin.php

And save them in a folder named 'unicornsareamazing'. But it will NOT download these:

    https://www.unicornsareamazing.com/red/green/someOtherPage.html
    https://www.unicornsareamazing.com/images/someImageFromThePenguinPage.jpg
    https://www.google.com/search?q=stop+asking+us+questions
    http://someExternalSite.com/suffLinkedToFromTheUnicornSite.html
    https://www.microsoft.com/DoYouNeedHelp?look=overthere""")


def main():
    if len(sys.argv) > 1 and len(sys.argv) < 5:
        context = sys.argv[1]
        place = "./"
        clean = False

        if len(sys.argv) == 3:
            if sys.argv[2] == "--clean":
                clean = True
            else:
                place = sys.argv[2]
        elif len(sys.argv) == 4:
            place = sys.argv[2]
            if sys.argv[3] == "--clean":
                clean = True
            else:
                print("Unrecognized option '" + sys.argv[3] + "'")

        with Crawler(place, context) as spider:
            if not clean:
                if (os.path.exists(spider.listFileName) and
                        os.path.exists(spider.visitedFileName)):
                    spider.loadState(spider.listFileName, spider.visitedFileName)
                else:
                    print("Could not load one or more of the URL lists.")
            
            spider.recursivePull()
    else:
        printHelp()


if __name__ == "__main__":
    main()
