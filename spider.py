#import xml.etree.ElementTree as ElementTree
#from xml.etree.ElementTree import XMLParser
#import http.client
import os
import re
import requests
import sys
import time
from collections import deque

class URLHelper:
    def __init__(self, url):
        index = url.find("://") + 3
        self.protocol = url[:index]
        first_slash = url[index:].find("/") + index
        self.domain = url[index:first_slash]
        last_slash = url[first_slash:].rfind("/") + first_slash + 1
        self.fileName = url[last_slash:]
        self.path = url[index:]
        self.fullPath = url[:last_slash]
        self.rawURL = url
        self.currentDirectory = url[index:last_slash]


class Crawler:
    def __init__(self, local_save, url):
        self.place = local_save
        self.domain = URLHelper(url).domain
        self.name_len = len(self.domain)
        # keep track of the places we've been
        self.places2go = deque()
        self.places2go.append(url)
        self.visited = set()
        self.crawlCount = 0
        self.pattern = re.compile("(href|src)=\\\\?(\"|')")


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.saveState()


    def recursiveMkdir(self, path):
        if not os.path.exists(path):
            pair = os.path.split(path)
            print(pair[0])
            self.recursiveMkdir(pair[0])
            os.mkdir(path)


    def removeBookmark(self, url):
        index = url.rfind('#')
        if index != -1:
            result = url[:index]
        else:
            result = url
        return result


    def addSlash(self, url):
        index = url.rfind("/")
        if index != -1 and index != len(url) - 1 and "." not in url[index:]:
            result = url + "/"
        else:
            result = url
        return result


    # requires data to begin with the url
    # returns None if the url is from a different doamin
    def parseLink (self, context, data):
        # this will not return None unless the html is REALLY crappy
        end = re.search("'|\"", data).start(0)
        url = data[:end]

        url = self.addSlash(url)
        url = self.removeBookmark(url)
        
        root = context[:context.find(self.domain) + self.name_len]
        reg = re.compile("((f|ht)tps?://)")
        result = None
        
        if reg.match(url) == None:
            url_len = len(url)
            if url_len > 1 and url[0:2] == "./":
                result = context + url[2:]
            elif url_len == 1 and url[0] == "/":
                result = root + "/"
            # filter out  empty urls and urls like mailto:me@me.com
            elif url_len != 0 and ":" not in url:
                result = context + url
        else:
            idx = url.find("://") + 3
            if (url.find(self.domain, idx) == 0
                    or url.find("www." + self.domain, idx) == 0):
                result = url

        return result

    
    def save(self, path, data):
        if path[-1] == '/':
            self.recursiveMkdir(path)
        else:
            last_slash = path.rfind('/')
            directory = path[:last_slash]
            self.recursiveMkdir(directory)
        
        file = open(path, "wb")
        file.write(data)
        file.close()
    

    # Downloads the file that {@code starting_url} points to
    # and adds all valid urls to {@code self.places2go} that are
    # not already in there.
    # 
    # @updates self.places2go
    # @updates self.visited
    # @updates self.crawlCount
    #
    def get(self, starting_url):
        self.visited.add(starting_url)
        self.crawlCount += 1
        response = requests.get(starting_url)

        if not response.ok:
            print(starting_url + " - Error: " + str(response.status_code)
                + " - " + response.reason)
            return

        url_obj = URLHelper(starting_url)
        file_path = self.place + url_obj.currentDirectory

        if starting_url[-1] == '/':
            file_path += "index.html"
        else:
            file_path += url_obj.fileName
        
        self.save(file_path, response.content)
        
        # Note: There will be no href in the first split
        raw_links = self.pattern.split(response.text)

        # Skip over every 3 elements 'cause the regex subpattern matches are kept.
        idx = 3
        while idx < len(raw_links):
            parsed = self.parseLink(url_obj.fullPath, raw_links[idx])
            if (parsed is not None and parsed not in self.places2go
                    and parsed not in self.visited):
                self.places2go.append(parsed)
                print("adding url: " + parsed)
            idx += 3


    def loadLines(self, file_name):
        result = []
        if os.path.exists(file_name):
            with open(file_name, "r") as f:
                result = f.read().splitlines()
                print("loaded '" + file_name + "'")
        else:
            print("'" + file_name + "' does not exist")
        return result


    def loadState(self):
        list_file_name = self.domain + "_list.txt"
        visited_file_name = self.domain + "_visited.txt"
        saved_places = self.loadLines(list_file_name)
        self.places2go.extend(saved_places)
        saved_visited = self.loadLines(visited_file_name)
        self.visited = self.visited.union(saved_visited)


    def saveState(self):
        with open(self.domain + "_list.txt", "w") as list_file:
            for place in self.places2go:
                list_file.write(place)
                list_file.write("\n")
        with open(self.domain + "_visited.txt", "w") as visited_file:
            for place in self.visited:
                visited_file.write(place)
                visited_file.write("\n")

    # @param nap_length
    #                   the time to sleep in seconds
    def coolSleep(self, nap_length):
        while nap_length > 0:
            minutes = str(nap_length // 60)
            if len(minutes) == 1:
                minutes = "0" + minutes
            seconds = str(nap_length % 60)
            if len(seconds) == 1:
                seconds = "0" + seconds
            print("sleeping...    " + minutes + ":" + seconds, end="\r")
            time.sleep(1)
            nap_length -= 1


    def recursivePull(self):
        while 0 != len(self.places2go):
            url = self.places2go.popleft()
            # self.get may update the length of self.places2go
            print("\nDownloading: " + url)
            self.get(url)
            if self.crawlCount % 3:
                self.saveState()
            print("list size: " + str(len(self.places2go)))
            print("Pages crawled this session: " + str(self.crawlCount))

            # sleep for longer (7-15min) when running 4 real.
            self.coolSleep(1)


def printHelp():
    print("""web.cse crawler - v1.and.only

            USEAGE:
                
            """)


def main():
    # this location has ~13,000 files in it. Good place to test.
    context = "http://localhost/php-manual-en/"
    place = "./data/"
    
    with Crawler(place, context) as spider:
        if len(sys.argv) < 2 or sys.argv[1] != "clean":
            spider.loadState()

        spider.recursivePull()
    


if __name__ == "__main__":
    main()
