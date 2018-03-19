#import xml.etree.ElementTree as ElementTree
#from xml.etree.ElementTree import XMLParser
import os
import re
import time
from collections import deque
import itertools

# 3rd party lib
import requests

# Dear self, This is terribly organized. Best, me

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

# Helper methods

def recursiveMkdir(path):
    if not os.path.exists(path):
        pair = os.path.split(path)
        recursiveMkdir(pair[0])
        os.mkdir(path)


def loadLines(file_name):
    result = []
    with open(file_name, "r") as f:
        result = f.read().splitlines()
        print("loaded '" + file_name + "'")
    return result


def removeBookmark(url):
    index = url.rfind('#')
    if index != -1:
        result = url[:index]
    else:
        result = url
    return result


def addSlash(url):
    index = url.rfind("/")
    if index != -1 and index != len(url) - 1 and "." not in url[index:]:
        result = url + "/"
    else:
        result = url
    return result


# The crawling class

class Crawler:
    def __init__(self, local_save, url):
        self.place = local_save
        if local_save[-1] != "/" and local_save[-1] != "\\":
            self.place = self.place + "/"
        url_obj = URLHelper(url)
        # prevent the spider from crawling above it's station
        self.context = url_obj.currentDirectory
        self.domain = url_obj.domain
        self.listFileName = self.domain + "_list.txt"
        self.visitedFileName = self.domain + "_visited.txt"
        # keep track of the places we've been
        self.places2go = deque()
        self.places2go.append(url)
        self.visited = []
        self.newURLCount = 1
        self.usedURLCount = 0
        # precompile the regexes to use later
        self.pattern = re.compile("(href|src)=\\\\?(\"|')")
        self.invalidPathChars = re.compile("[<>:\"\\|\\?\\*]")


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.saveState(self.listFileName, self.visitedFileName)


    # returns None if the url is from a different domain
    # or if the url is in a directory above the one the Crawler was
    # initialized to.
    def parseLink (self, context, data):
        # this will not return None unless the html is REALLY crappy
        end = re.search("'|\"", data).start(0)
        url = data[:end]

        url = addSlash(url)
        url = removeBookmark(url)
        
        root = context[:context.find(self.context) + len(self.context)]
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
            if (url.find(self.context, idx) == 0
                    or url.find("www." + self.context, idx) == 0):
                result = url

        return result

    
    def save(self, path, data):
        # replace invalid windows path characters
        filteredPath = self.invalidPathChars.sub("_", path)
        if filteredPath[-1] == '/':
            recursiveMkdir(filteredPath)
        else:
            last_slash = filteredPath.rfind('/')
            directory = filteredPath[:last_slash]
            recursiveMkdir(directory)
        
        out = open(filteredPath, "wb")
        out.write(data)
        out.close()
    

    # Downloads the file that {@code starting_url} points to
    # and adds all valid urls to {@code self.places2go} that are
    # not already in there.
    # 
    # @updates self.places2go
    #
    def get(self, starting_url):
        response = requests.get(starting_url)

        if not response.ok:
            msg = (starting_url + " - Error: " + str(response.status_code)
                    + " - " + response.reason)
            print(msg)
            with open("error.log", "a") as f:
                f.write(msg + "\n")
            return

        url_obj = URLHelper(starting_url)
        file_path = self.place + url_obj.currentDirectory

        # assume the root file name is 'index.html'
        if starting_url[-1] == '/':
            file_path += "index.html"
        else:
            file_path += url_obj.fileName
        
        self.save(file_path, response.content)
        
        # Don't need to look for liks if the file is binary
        if "text" in response.headers["content-type"]:
            raw_links = self.pattern.split(response.text)
        else:
            raw_links = []

        # Skip over every 3 elements 'cause the regex subpattern matches are kept.
        idx = 3
        while idx < len(raw_links):
            parsed = self.parseLink(url_obj.fullPath, raw_links[idx])
            if (parsed is not None and parsed not in self.places2go
                    and parsed not in self.visited):
                self.places2go.append(parsed)
                self.newURLCount += 1
                print("adding url: " + parsed)
            idx += 3


    # replaces self.places2go
    # replaces self.visited
    # clears self.newURLCount
    # clears self.usedURLCount
    def loadState(self, list_file_name, visited_file_name):
        loadedList = frozenset(loadLines(list_file_name))
        loadedVisted = loadLines(visited_file_name)
        self.places2go = deque()
        self.places2go.append(loadedList.difference(loadedVisted))
        self.visited = loadedVisted
        self.newURLCount = 0
        self.usedURLCount = 0

    # clears self.usedURLCount
    # clears self.newURLCount
    def saveState(self, list_file_name, visited_file_name):
        with open(list_file_name, "a") as list_file:
            diff = len(self.places2go) - self.newURLCount
            if diff < 0:
                newURLs = self.visited[diff:]
                newURLs.extend(self.places2go)
            else:
                newURLs = list(itertools.islice(self.places2go, diff, None))

            for url in newURLs:
                list_file.write(url + "\n")
    
        with open(visited_file_name, "a") as visited_file:
            newVisits = self.visited[len(self.visited) - self.usedURLCount:]
            for url in newVisits:
                visited_file.write(url + "\n")
        
        self.usedURLCount = 0
        self.newURLCount = 0


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
            self.visited.append(url)
            self.usedURLCount += 1
            # self.get may update the length of self.places2go
            print("\nDownloading: " + url)
            self.get(url)
            if self.usedURLCount == 12:
                print("Saving current state...")
                self.saveState(self.listFileName, self.visitedFileName)
            print("list size: " + str(len(self.places2go)))

            # be nice to webservers, sleep for 600s (12min)
            # self.coolSleep(60 * 12)


