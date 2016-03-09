#!/usr/bin/python

################################################################################
#
# ThousandEyesApi class. Do not edit. Scroll down to the bottom to make changes
#
################################################################################

import sys
import urllib, urllib2
import json
import datetime



#
# ThousandEyesApi class includes methods to interact with the ThousandEyes API
#
class ThousandEyesApi:


    apiUri = 'https://api.thousandeyes.com/'


    def __init__(self, email, authToken, accountId=None):

        self.email = email
        self.authToken = authToken
        self.accountId = accountId

    #
    # Performs GET HTTP request to desired API endpoint and returns JSON data
    #
    def makeGetRequest(self, uri):

        passwordManager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passwordManager.add_password(None, self.apiUri, self.email, self.authToken)
        handler = urllib2.HTTPBasicAuthHandler(passwordManager)

        director = urllib2.build_opener(handler)

        req = urllib2.Request(uri)

        try:
            result = director.open(req)
        except urllib2.HTTPError, e:
            print('HTTPError = ' + str(e.code))
        except urllib2.URLError, e:
            print('URLError = ' + str(e.reason))
        except httplib.HTTPException, e:
            print('HTTPException')
        # result.read() will contain the data
        # result.info() will contain the HTTP headers

        #response = requests.get(uri)
        return json.loads(result.read())


    #
    # Performs POST HTTP request to desired API endpoint and returns JSON data
    #
    def makePostRequest(self, uri, properties):

        passwordManager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passwordManager.add_password(None, self.apiUri, self.email, self.authToken)
        handler = urllib2.HTTPBasicAuthHandler(passwordManager)

        director = urllib2.build_opener(handler)

        headers = { 'Content-Type': 'application/json'}
        data = json.dumps(properties)

        req = urllib2.Request(uri, data, headers)

        try:
            result = director.open(req)
        except urllib2.HTTPError, e:
            print('HTTPError = ' + str(e.code))
        except urllib2.URLError, e:
            print('URLError = ' + str(e.reason))
        except httplib.HTTPException, e:
            print('HTTPException')

        return json.loads(result.read())


    #
    # Queries /agents endpoint.
    # http://developer.thousandeyes.com/agents/
    #
    def getAgents(self):

        uri = self.apiUri + 'agents.json'
        return self.makeGetRequest(uri)


    #
    # Queries /tests/{testType}/new endpoint.
    # http://developer.thousandeyes.com/tests/
    #
    def createTest(self, testType, properties):

        uri = self.apiUri + 'tests/' + testType + '/new.json'
        return self.makePostRequest(uri, properties)






################################################################################
#
# Showcase script that utilizes the ThousandEyesApi class. Modify to achieve
# your desired results.
#
################################################################################

# ThousandEyes API requires username and API token. These should be provided as
# parameters from the CLI. User can optionally provide a number of a sample to
# be ran. Defaults to sample #1.
if len(sys.argv) != 3 and len(sys.argv) != 4:
    sys.exit('Use: ' + sys.argv[0] + ' <email> <apiToken> [sampleNumber]')

username = sys.argv[1]
apiToken = sys.argv[2]
if len(sys.argv) == 4:
    sampleNo = int(sys.argv[3])
else:
    sampleNo = 1



#
# Sample #1
#
# Print IP addresses of all Cloud Agents available to your account
#
if sampleNo == 1:

    # Establish connection with the API, use your email and API token
    api = ThousandEyesApi(username, apiToken)

    # Get all agent data from the /agents API endpoint
    data = api.getAgents()

    # Loop through all the agents
    for agent in data['agents']:
        # We are only interested in Cloud agents, not in Enterprise agents
        if agent['agentType'] == 'Cloud':
            if agent['ipAddresses']:
                # Each Cloud agent has multiple IP addresses, loop through all
                for ipAddress in agent['ipAddresses']:
                    print(ipAddress)



#
# Sample #2
#
# Create a new HTTP server test and add it to all Enterprise agents that are
# currently Online.
#
if sampleNo == 2:

    # Establish connection with the API, use your email and API token
    api = ThousandEyesApi(username, apiToken)

    # Get all agent data from the /agents API endpoint
    data = api.getAgents()

    # Put all Enterprise agent IDs in a single list
    enterpriseAgentIds = []
    # Loop through all the agents
    for agent in data['agents']:
        # We are only interested in Enterprise agents that are currently online
        if agent['agentType'] == 'Enterprise' and agent['agentState'] == 'Online':
            enterpriseAgentIds.append(agent['agentId'])

    # Test type is HTTP Server
    testType = 'http-server'

    # Configure new test properties
    # http://developer.thousandeyes.com/tests/#/test_metadata
    properties = {}
    # Test will be called 'API test <date time>'
    properties['testName'] = 'API test ' + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    # Run once every hour
    properties['interval'] = 3600
    # Query the www.thousandeyes.com website
    properties['url'] = 'http://www.thousandeyes.com'
    # Disable alerts
    properties['alertsEnabled'] = 0
    # Run the test on the Enterprise agents that are currently online
    properties['agents'] = []
    for agentId in enterpriseAgentIds:
        properties['agents'].append({"agentId": agentId})

    # Create the test
    result = api.createTest(testType, properties)

    # Print out the results of the new test call
    print ('Test ' + result['test'][0]['testName'] + ' created.')
    print ('Currently running on agents:')
    for agent in result['test'][0]['agents']:
        print ('- ' + agent['agentName'])
