import urllib2
import re
from os.path import basename, exists, join
from urlparse import urlsplit
from threading import Thread
from framework.async import CancelToken


def download_async(callback=None):
    c = CancelToken()
    t = Thread(target=download, args=(callback, c))
    t.start()
    return c, t
    
def download(callback=None, canceltoken=None):
    b = "http://dominion.diehrstraits.com/scans/"
    s = ("base", "intrigue", "seaside", "alchemy",
         "prosperity", "cornucopia", "hinterlands", 
         "promo", "common")
    
    try:
        for url in [b + e for e in s]:
            urlContent = urllib2.urlopen(url).read()
            imgUrls = re.findall('A .*?HREF="(.*?jpg)"', urlContent, re.IGNORECASE)
            for imgUrl in imgUrls:
                if canceltoken and canceltoken.cancel:
                    return
                filename = basename(urlsplit(imgUrl)[2])
                print filename
                fullpath = join('res', 'cards_full', filename)
                if not exists(fullpath):
                    print fullpath
                    try:
                        with open(fullpath, 'wb') as f:
                            imgData = urllib2.urlopen(url + '/' + imgUrl).read()
                            f.write(imgData)
                        if callback:
                            callback(fullpath)
                    except e:
                        print e
    except:
        pass
    
if __name__ == "__main__":
    download()
