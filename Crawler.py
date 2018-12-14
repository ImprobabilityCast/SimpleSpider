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

        self.lastSaveTime = 0


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.saveState(self.listFileName, self.visitedFileName)


    # returns None if the url is from a different domain
    # or if the url is in a directory above the one the Crawler was
    # initialized to.
    def parseLink(self, context: URLHelper, link: str) -> str:
        url = URLHelper.addSlash(link)
        url = URLHelper.removeBookmark(url)
        result = None
        
        if self.protocolPattern.match(url) == None:
            url_len = len(url)
            if url_len > 1 and url[0] == ".":
                if url[1] == "/":
                    result = context.fullPath + url[2:]
                elif url[1] == ".":
                    idx = context.currentDirectory[:-1].rfind("/")
                    if idx != -1:
                        # add 1 to keep slash at the end of the parent directory
                        idx += len(context.protocol) + 1
                        result = context.fullPath[:idx] + url[3:]
                else:
                    result = context.fullPath + url
            
            elif url_len == 1 and url[0] == "/":
                result = context.protocol + context.domain
            # filter out  empty urls and urls like mailto:me@me.com
            elif url_len != 0 and ":" not in url:
                if url[0] == "/":
                    result = context.protocol + context.domain + url
                else:
                    result = context.fullPath + url
        else:
            # check if URL is from same domain & subdomain
            idx = url.find("://") + 3
            if (url.find(self.context, idx) == idx
                    or url.find("www." + self.context, idx) == idx):
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
    # Returns the provided starting_url or the URL it redirects to
    # 
    # updates self.places2go
    #
    def get(self, starting_url: str):
        response = requests.get(starting_url, allow_redirects=False, headers={"User-Agent": "SimpleSpider"})

        if not response.ok:
            msg = ("Error: " + str(response.status_code)
                    + " - " + response.reason + " - " + starting_url)
            print(msg)
            with open("error.log", "a") as f:
                f.write(msg + "\n")
            return starting_url
        
        if response.is_redirect:
            return self.get(response.headers['Location'])

        url_obj = URLHelper(starting_url)
        file_path = self.place + url_obj.currentDirectory + url_obj.fileName
        self.save(file_path, response.content)
        
        # Don't need to look for links if the file is binary,
        # and not going to bother looking through non-html
        # responses for possible URLs
        if "text/html" in response.headers["Content-Type"]:
            raw_links = set()
            for n in extractNamedNodes(response.text, ["a", "img", "script", "link"]):
                if 'href' in n.attributes:
                    raw_links.add(n.attributes['href'])
                elif 'src' in n.attributes:
                    raw_links.add(n.attributes['src'])
            
            while 0 < len(raw_links):
                parsed = self.parseLink(url_obj, raw_links.pop())
                if (parsed is not None and parsed not in self.places2go
                        and parsed not in self.visited):
                    self.places2go.append(parsed)
                    self.newURLCount += 1
                    print("adding url: " + parsed)
        
        return starting_url


    # updates self.places2go
    # updates self.visited
    # replaces self.listFileName
    # replaces self.visitedFileName
    # clears self.newURLCount
    # clears self.usedURLCount
    def loadState(self, list_file_name: str, visited_file_name: str):
        loadedList = frozenset(Crawler._loadLines(list_file_name))
        loadedVisted = Crawler._loadLines(visited_file_name)
        newList = loadedList.difference(loadedVisted)
        self.places2go = deque(frozenset(self.places2go).union(newList))
        self.visited = list(frozenset(self.visited).union(loadedVisted))
        self.newURLCount = 0
        self.usedURLCount = 0
        self.listFileName = list_file_name
        self.visitedFileName = visited_file_name


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


    # clears self.places2go
    # clears self.visited
    # clears self.usedURLCount
    # clears self.newURLCount
    def clearLists(self):
        self.places2go.clear()
        self.visited.clear()
        self.newURLCount = 0
        self.usedURLCount = 0


    def recursivePull(self):
        while 0 != len(self.places2go):
            url = self.places2go.popleft()
            self.visited.append(url)
            self.usedURLCount += 1
            # self.get may update the length of self.places2go
            print("\nDownloading: " + url)

            # check for redirects
            newURL = self.get(url)
            if newURL != url:
                self.visited.append(newURL)
            
            # save current state if it's been 5min or if we've used 12 URLs
            t = time.time()
            if t - self.lastSaveTime > 60 * 5 or self.usedURLCount == 12:
                print("Saving current state...")
                self.saveState(self.listFileName, self.visitedFileName)
                self.lastSaveTime = t
            print("list size: " + str(len(self.places2go)))

            # be nice to webservers, sleep for 12min
            #Crawler._coolSleep(60 * 12)


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
