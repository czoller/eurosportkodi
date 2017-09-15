# -*- coding: utf-8 -*-
# Module: default
# Author: NaZo

import sys
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin
import urllib
import json
from datetime import datetime
import dateutil.parser


_HANDLE = int(sys.argv[1])
_EUROSPORT_MAIN_URL = 'https://de.eurosportplayer.com/schedule';
_EUROSPORT_AIRINGS_URL = 'https://search-api.svcs.eurosportplayer.com/svc/search/v2/graphql/persisted/query/eurosport/web/Airings/onAir?variables=%7B%22uiLang%22%3A%22de%22%2C%22mediaRights%22%3A%5B%22GeoMediaRight%22%5D%2C%22preferredLanguages%22%3A%5B%22de%22%2C%22en%22%5D%7D';
_EUROSPORT_EVENT_URL_PREFIX = 'https://de.eurosportplayer.com/event/contentId/';


class EurosportAiring(object):
    
    def __init__(self, json):
        
        self.live = json['liveBroadcast']
        self.title = json['titles'][0]['title']
        self.channel = json['channel']['callsign']
        self.description = json['titles'][0]['descriptionLong']
        thumbSize = 0
        self.thumb = ''
        fanartSize = 0
        self.fanart = ''
        for photo in json['photos']:
            width = int(photo['width']) 
            if width > fanartSize:
                fanartSize = width
                self.fanart = photo['uri']
            if abs(400 - width) < abs(400 - thumbSize):
                thumbSize = width
                self.thumb = photo['uri']
        self.start = dateutil.parser.parse(json['startDate'][:-1])
        self.end = dateutil.parser.parse(json['endDate'][:-1]);
        self.page = _EUROSPORT_EVENT_URL_PREFIX + json['contentId']
        
    def toListItem(self):
        listItem = xbmcgui.ListItem(label=self.title)
        listItem.setInfo('video', {'title': self.title, 'date': self.start.strftime('%d.%m.%Y'), 'tagline': self.description, 'plot': self.description, 'plotoutline': self.description})
        listItem.setProperty('IsPlayable', 'true')
        listItem.setArt({'thumb': self.thumb, 'icon': self.thumb, 'fanart': self.fanart})
        page = self.page
        url = 'plugin://plugin.program.chrome.launcher/?url=' + page + '&mode=showSite&stopPlayback=no'
        
        return (url, listItem, False)
    
def toListItem(skygoObject):
    return skygoObject.toListItem()

def loadVideoList():
    
    file = urllib.urlopen(_EUROSPORT_AIRINGS_URL)
    results = json.load(file)
    
    now = datetime.utcnow()
    listItems = []
    for item in results['data']['Airings']:
        airing = EurosportAiring(item)
        if airing.channel.endswith('GR') or airing.channel.startswith('LI'):
            listItems.append(airing)

    return listItems
    
def listVideos():
    
    listing = map(toListItem, loadVideoList())
    xbmcplugin.addDirectoryItems(_HANDLE, listing, len(listing))
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_DATEADDED)
    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(_HANDLE)


def showVideo(path):

    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=play_item)


def router(paramstring):

    params = dict(parse_qsl(paramstring))
    if params and params['show'] == 'play':
        showVideo(params['video'])
    else:
        listVideos()


if __name__ == '__main__':
    router(sys.argv[2][1:])
