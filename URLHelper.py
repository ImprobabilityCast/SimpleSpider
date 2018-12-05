import os

# A not so helpful helper class
class URLHelper:
    def __init__(self, url: str):
        index = url.find("://") + 3
        self.protocol = url[:index]
        first_slash = url[index:].find("/")
        if first_slash == -1:
            self.domain = url[index:]
            self.path = "/"
            self.fileName = "index.html"
            self.fullPath = url + "/"
            self.currentDirectory = url[index:] + "/"
        else:
            first_slash += index
            self.domain = url[index:first_slash]
            last_slash = url[first_slash:].rfind("/") + first_slash + 1
            if last_slash == len(url):
                self.fileName = "index.html"
            else:
                self.fileName = url[last_slash:]
            self.path = url[first_slash:]
            self.fullPath = url[:last_slash]
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
    
    def __str__(self):
        return self.fullPath + self.fileName

    def __repr__(self):
        return ("{\n"
            "\tprotocol:\t\t" + self.protocol + ",\n"
            "\tdomain:\t\t\t" + self.domain + ",\n"
            "\tfileName:\t\t" + self.fileName + ",\n"
            "\tpath:\t\t\t" + self.path + ",\n"
            "\tfullPath:\t\t" + self.fullPath + ",\n"
            "\tcurrentDirectory:\t" + self.currentDirectory  + "\n}"
        )
