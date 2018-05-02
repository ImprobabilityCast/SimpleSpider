import os

# A not so helpful helper class
class URLHelper:
    def __init__(self, url: str):
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

    @staticmethod
    def removeBookmark(url: str) -> str:
        index = url.rfind('#')
        if index != -1:
            result = url[:index]
        else:
            result = url
        return result

    @staticmethod
    def addSlash(url: str) -> str:
        index = url.rfind("/")
        if index != -1 and index != len(url) - 1 and "." not in url[index:]:
            result = url + "/"
        else:
            result = url
        return result
