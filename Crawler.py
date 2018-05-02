import itertools    
import os
import re
import time

from collections import deque
from typing import ByteString

# 3rd party lib
import requests

from NodeExtractor import extractNamedNodes
from URLHelper import URLHelper


# The crawling class

class Crawler:
    def __init__(self, local_save: str, url: str):
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
        self.protocolPattern = re.compile("((f|ht)tps?://)")
        self.invalidPathChars = re.compile("[<>:\"\\|\\?\\*]")


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.saveState(self.listFileName, self.visitedFileName)


    # returns None if the url is from a different domain
    # or if the url is in a directory above the one the Crawler was
    # initialized to.
    def parseLink(self, context: str, link: str) -> str:
        url = URLHelper.addSlash(link)
        url = URLHelper.removeBookmark(url)
        root = context[:context.find(self.context) + len(self.context)]
        result = None
        
        if self.protocolPattern.match(url) == None:
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

    
    def save(self, path: str, data: ByteString):
        # replace invalid windows path characters
        filteredPath = self.invalidPathChars.sub("_", path)
        if filteredPath[-1] == '/':
            Crawler._recursiveMkdir(filteredPath)
        else:
            last_slash = filteredPath.rfind('/')
            directory = filteredPath[:last_slash]
            Crawler._recursiveMkdir(directory)
        
        with open(filteredPath, "wb") as out:
            out.write(data)

    # Downloads the file that {@code starting_url} points to
    # and adds all valid urls to {@code self.places2go} that are
    # not already in there.
    # 
    # @updates self.places2go
    #
    def get(self, starting_url: str):
        response = requests.get(starting_url)

        if not response.ok:
            msg = ("Error: " + str(response.status_code)
                    + " - " + response.reason + " - " + starting_url)
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
        
        # Don't need to look for links if the file is binary,
        # and not going to bother looking through non-html
        # responses for possible URLs
        if "text/html" == response.headers["content-type"]:
            raw_links = set()
            for n in extractNamedNodes(response.text, ["a", "img", "script", "link"]):
                if 'href' in n.attributes:
                    raw_links.add(n.attributes['href'])
                elif 'src' in n.attributes:
                    raw_links.add(n.attributes['src'])
            
            while 0 < len(raw_links):
                parsed = self.parseLink(url_obj.fullPath, raw_links.pop())
                if (parsed is not None and parsed not in self.places2go
                        and parsed not in self.visited):
                    self.places2go.append(parsed)
                    self.newURLCount += 1
                    print("adding url: " + parsed)
    

    # replaces self.places2go
    # replaces self.visited
    # clears self.newURLCount
    # clears self.usedURLCount
    def loadState(self, list_file_name: str, visited_file_name: str):
        loadedList = frozenset(Crawler._loadLines(list_file_name))
        loadedVisted = Crawler._loadLines(visited_file_name)
        self.places2go = deque()
        self.places2go.extend(loadedList.difference(loadedVisted))
        self.visited = loadedVisted
        self.newURLCount = 0
        self.usedURLCount = 0


    # clears self.usedURLCount
    # clears self.newURLCount
    def saveState(self, list_file_name: str, visited_file_name: str):
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
            # _coolSleep(60 * 12)

    # @param nap_length
    #                   the time to sleep in seconds
    @staticmethod
    def _coolSleep(nap_length: int):
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

    @staticmethod
    def _recursiveMkdir(path):
        if not os.path.exists(path):
            pair = os.path.split(path)
            Crawler._recursiveMkdir(pair[0])
            os.mkdir(path)

    @staticmethod
    def _loadLines(file_name: str) -> list:
        result = []
        with open(file_name, "r") as f:
            result = f.read().splitlines()
            print("loaded '" + file_name + "'")
        return result
