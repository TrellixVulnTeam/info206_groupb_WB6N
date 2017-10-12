import urllib.request
import xml.etree.ElementTree as ET
#https://docs.python.org/3.0/library/urllib.request.html
#https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.XMLPullParser

class NextBusAPI(object):
    """
    Inputs:
        Stop (mandatory), e.g. "MacArthur Blvd & 66th Av"
        Route (optional), e.g. "57"
        Direction (optional), e.g. "Emeryville"

    Outputs:
    List of soon to depart buses, with:
        Route title
        Direction
        Departure Time Estimate


    Methods should accept BARTQueryIntent and return a BARTRoutesResponse.

    BusQueryIntent (a subclass of Intent)
		Represents a user’s intent to query for bus schedules
		Attributes:
            origin (string): The origin bus station
            Route (string): The AC Transit bus route in question, for example “6”, “51B”
            direction (string, optional): The direction in question, for example, “Northbound”
            destination (string, optional): The destination bus station

    BusRoutesResponse
		Represents a response containing bus route schedules
		Attributes:
            departures (list of  DateTime): The schedule of departures from that specific route.
    """

    def __init__(self):
        """
        Initiate with values for AC transit.
        """
        #from Agency List
        self.agencyTag = 'actransit'
        self.agencyTitle = 'AC Transit'
        self.regionTitle = 'California-Northern'

    def getAgencyList(self):
        """
        Obtain a list of available transit agencies.
        """
        #Agency information
        #Import agency list feed and parse it into an Element Tree.
        self.agencyListFeed = urllib.request.urlopen('http://webservices.nextbus.com/service/publicXMLFeed?command=agencyList')
        self.agencyList = ET.parse(self.agencyListFeed)


    def getRouteList(self, agency):
        """
        http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=<agency_tag>
        Obtain a list of routes for a given agency.
        The agency is specified by the "a" parameter in the query string.
        The tag for the agency is obtained from the agencyList command.
        """
        self.routeListFeed = urllib.request.urlopen('http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=%s' %self.agencyTag)
        self.routeList = ET.parse(self.routeListFeed)

        print("getRouteList url request: ", 'http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&a=%s' %self.agencyTag)

        #Get dictionary of route tag: route title
        self.routeListRoot = self.routeList.getroot()
        self.routeDictionary = {}
        for child in self.routeListRoot:
            self.routeDictionary.update({child.get('title'):child.get('tag')})

    def getRouteConfig(self, agency, route):
        """
        http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=<agency_tag>&r=<route tag>
        Obtain a list of routes for a given agency. The route is optionally specified by the "r" parameter.
        The tag for the route is obtained using the routeList command.
        If the "r" parameter is not specified, all routes for the agency are returned, limited to 100 routes per request.
        """
        self.routeConfigFeed = urllib.request.urlopen('http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=%s&r=%s' %(self.agencyTag, self.routeTag))
        self.routeConfig = ET.parse(self.routeConfigFeed)

        print("getRouteConfig url request:", 'http://webservices.nextbus.com/service/publicXMLFeed?command=routeConfig&a=%s&r=%s' %(self.agencyTag, self.routeTag))

        #Creates a dictionary for the given route w/ stop titles as keys and stop tags as values
        #Need to be able to find all stop tags associated with a certain stop title.
        """
        self.stopsDictionary = {}
        self.routeConfigRoot = self.routeConfig.getroot()
        for child in self.routeConfigRoot:
            for stop in child:
                self.stopsDictionary.update({stop.get('title'):stop.get('tag')})
        print('Stops dictionary: ', self.stopsDictionary)
        """
        self.routeConfigRoot = self.routeConfig.getroot()
        self.stopsDictionaryByTag = {}
        for route in self.routeConfigRoot:
            for stop in route:
                self.stopsDictionaryByTag.update({stop.get('tag'):stop.get('title')})

        #print('Stops Dictionary by Tag:', self.stopsDictionaryByTag)


    def getPredictionRequest(self, agency, route, stop):
        """
        http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=<agency_tag>&r=<route tag>&s=<stop tag>
        Obtain predictions associated with a particular stop. There are two ways to specify the stop: 1) using a stopId or 2) by specifying the route and stop tags.​
        Returns a list of bus departure times, with the first item being the route direction.
        """
        print('getPredictionRequest url: ', 'http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=%s&r=%s&s=%s' %(agency, route, stop))
        self.predictionRequestFeed = urllib.request.urlopen('http://webservices.nextbus.com/service/publicXMLFeed?command=predictions&a=%s&r=%s&s=%s' %(agency, route, stop))
        self.predictionRequest = ET.parse(self.predictionRequestFeed)

        busDepartureTimes = {}
        self.predictionRequestRoot = self.predictionRequest.getroot()
        for predictions in self.predictionRequestRoot:
            for direction in predictions:
                timeList = []
                for prediction in direction:
                    #print(prediction.items())
                    timeList.append(prediction.get('minutes'))
                busDepartureTimes[direction.get('title')]= timeList

        return busDepartureTimes


    def BartRoutesResponse(self, routeInput, stopInput, directionInput = None):
        """Takes stop, route, and optionally direction as input.
        Returns a dictionary with all keys of stop titles and elements of list of estimated upcoming departure times in minutes.
        If direction is specified, returns a dictionary with only the specified direction and its estimated upcoming departure times."""
        self.routeInput = routeInput
        self.stopInput = stopInput
        self.directionInput = directionInput
        #self.agencyTag = 'actransit' already, from initiation

        #From route title, find route tag
        self.getRouteList(self.agencyTag)
        #route dictionary will be defined, with title:tag
        self.routeTag = self.routeDictionary[self.routeInput]
        print('Route Input:', self.routeInput, 'Route Tag:', self.routeTag)

        #From stop title, find stop tags
        self.getRouteConfig(self.agencyTag, self.routeTag)

        #Check stopsDictionaryByTag for all instances of the stop title, and fetch the associated tags
        self.stopTags = []
        for tag in self.stopsDictionaryByTag:
            if self.stopsDictionaryByTag[tag] == self.stopInput:
                self.stopTags.append(tag)

        print('Stop Input:', self.stopInput, 'Stop Tags:', self.stopTags)

        allDepartureTimes = {}
        #Make prediction request
        for tag in self.stopTags:
            allDepartureTimes.update(self.getPredictionRequest(self.agencyTag, self.routeTag, tag))


        if directionInput:
            filteredDepartureTimes = {self.directionInput:allDepartureTimes[self.directionInput]}
            print(filteredDepartureTimes)
            return filteredDepartureTimes

        print(allDepartureTimes)
        return(allDepartureTimes)




if __name__ == '__main__':
    NextBus = NextBusAPI()

    """
    #Test: Print agency list
    #NextBus.getAgency()
    agencyListRoot = NextBus.agencyList.getroot()
    agencies = []
    for child in agencyListRoot:
       agencies.append(child.get('title'))
    print('\n'.join(agencies))
    """
    """
    #Test: print route feed
    NextBus.getRouteList(NextBus.agencyTag)
    print(NextBus.routeDictionary)
    # routeListRoot = NextBus.routeList.getroot()
    # for child in routeListRoot:
    #     print(child.get('title'))
    """
    """
    #Test: print route config
    NextBus.routeTag = '57'
    NextBus.getRouteConfig(NextBus.agencyTag, NextBus.routeTag)
    print(NextBus.stopsDictionary)
    """
    """
    #Test: print prediction request
    NextBus.routeTag = '57'
    NextBus.stopTag = '1002650'
    NextBus.getPredictionRequest(NextBus.agencyTag, NextBus.routeTag, NextBus.stopTag)
    predictionRequestRoot = NextBus.predictionRequest.getroot()
    for child in predictionRequestRoot:
        print('Prediction request:', child.items())
        for item in child:
            print(item.items())
    """

    #Test: BARTRoutesResponse
    NextBus.BartRoutesResponse(stopInput = "40th St & Telegraph Av", routeInput = "57", directionInput = "Foothill Square" )
    # pass
