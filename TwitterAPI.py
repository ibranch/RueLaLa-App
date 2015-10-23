__author__ = 'branch.izaak@gmail.com'

import twitter
import simplejson
import oauth.oauth as oauth
import os
import oauthtwitter
import webbrowser
from requests_oauthlib import OAuth1Session

consumer_key = 'e4HQnSAldA79TXwDPhe5ZR6zh'
consumer_secret = 'TFKLd2nAbmEse20WOfiMTsjdYZAUHpsLGqey1ffzUYaV7YE14W'
api = twitter.Api(access_token_key="")

class TwitterAPI:

    def getAuthToken(self):
        """
        Generates an Access Token Key and Access Token Secret Key for a Twitter API object

        Note: the vast majority of code in getAuthToken() is copied from or remarkably close to
        the code in get_access_token.py included in the python-twitter package found at
        github.com/bear/python-twitter/blob/master/get_access_token.py

        :return: an authenticated twitter.API object
        """

        #These variables do not need to be globally accessible, so they are moved here
        REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
        ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
        AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'

        oauth_client =  OAuth1Session(consumer_key, client_secret=consumer_secret)

        print 'Requesting temp token from Twitter'

        try:
            response = oauth_client.fetch_request_token(REQUEST_TOKEN_URL)
        except ValueError, e:
            print 'Invalid response from Twitter when requesting temp token: %s' % e
            return
        url = oauth_client.authorization_url(AUTHORIZATION_URL)

        print '\nI will attempt to automatically start a browser to access authentication page.' \
              '\nIf a browser does not open, please navigate to the following URL and sign in' \
              '\nto Twitter to retrieve the PIN you will need for the next step.\n'
        print url

        webbrowser.open(url)
        print ''
        pin = raw_input("Please enter the PIN you received: ")

        print '\nGenerating and signing request for an access token \n'

        oauth_client = OAuth1Session(consumer_key,
                                     client_secret=consumer_secret,
                                     resource_owner_key=response.get('oauth_token'),
                                     resource_owner_secret=response.get('oauth_token_secret'),
                                     verifier=pin)

        try:
            response = oauth_client.fetch_access_token(ACCESS_TOKEN_URL)
        except ValueError, e:
            print 'Invalid response from Twitter requesting token: %s' % e
            return

        access_token = response.get('oauth_token')
        access_secret = response.get('oauth_token_secret')

        #no need to have access token and access secret accessible outside of this function,
        #just pass them directly to an API builder, and the created API will be global.
        api = self.makeAPI(access_token, access_secret)

        return api

    def makeAPI(self, access_token, access_secret):
        """
        Generates a Twitter API object.

        :param access_token: An Access Token received from Twitter using OAuth
        :param access_secret: A Secret AccessToken received from Twitter using OAuth
        :return: the newly constructed API
        """
        api = twitter.Api(consumer_key = consumer_key,
                      consumer_secret = consumer_secret,
                      access_token_key=access_token,
                      access_token_secret=access_secret)

        return api

    def sendTweet(self, message):
        """
        Sends a tweet from the Authenticated account, and prints that tweet.

        :return: None
        :except: UnicodeDecodeError if non-ASCII characters are used
        :except: AttributeError if the api object has an error
        """

        try:
            status = api.PostUpdates(message)
        except UnicodeDecodeError:
            print "Your message could not be encoded - please only use ASCII characters"
        except AttributeError, e:
            print "Message could not be sent - likely api is not initialized or authenticated: %s\n" % e
            print "Will attempt to authenticate and initialize api...\n\n"
            self.getAuthToken()

        print 'You just tweeted \"%s\"' % message

        return

    def searchTweets(self, term):
        """
        Searches all tweets for the given term

        Uses standard Twitter search function, so keywords such as OR and to: will work
        Prints all returned tweets in the form <Username>: <Tweet> before returning

        :param term: The term to search for
        :return: a list of up to 16 twitter.Status objects that match the given term
        """
        tweets = api.GetSearch(term, count=16)

        for tweet in tweets:
            try:
                print "%s: %s" % (tweet.GetUser().screen_name, tweet.GetText(),)
            except UnicodeEncodeError, e:
                print "A Tweet could not be decoded - likely uses characters unsupported by your charmap (like emojis): %s" % e

        return tweets

    def searchTermExact(self, term):
        """
        Searches all tweets for exactly the given term

        Appends quotes to the front and end of the given search term, then uses standard
        Twitter search function. Prints all returned tweets in the form
        <Username>: <Tweet> before returning

        :param term: the exact term to search for
        :return: a list of up to 16 twitter.Status objects that match the given term exactly
        """

        term = "\"" + term + "\""

        return self.searchTweets(term)

    def searchTweetsRange(term, endDate):
        """
        Searches all tweets for the given term before the given date

        Uses standard Twitter search function. Prints all returned tweets in the form
        <Username>: <Tweet> before returning

        NOTE: Apparently the python-twitter documentation for twitter.api.GetSearch is inaccurate.
        There is no option to pass in a startDate/since argument, therefore it has been omitted here.

        :param term: the term to search for
        :param endDate: the end date of the search, in YYYY-MM-DD format
        :return: a list of up to 16 twitter.Status objects that match the given term in the given date range
        """
        if endDate == "0":
            tweets = api.GetSearch(term, count=16)
        else:
            tweets = api.GetSearch(term, count=16, until=endDate)

        for tweet in tweets:
            try:
                print "%s: %s" % (tweet.GetUser().screen_name, tweet.GetText())
            except UnicodeEncodeError, e:
                print "A Tweet could not be decoded - likely uses characters unsupported by your charmap (like emojis): %s" % e

        return tweets

    def searchTweetsRangeExact(self, term, endDate):
        """
        Searches all tweets for the exact given term between the given dates

        Appends quotes to the front and end of the given search term, then uses standard
        Twitter search function. Prints all returned tweets in the form
        <Username>: <Tweet> before returning

        NOTE: Apparently the python-twitter documentation for twitter.api.GetSearch is inaccurate.
        There is no option to pass in a startDate/since argument, therefore it has been omitted here.

        :param term: the term to search for
        :param endDate: the end date of the search, in YYYY-MM-DD format
        :return: a list of up to 16 twitter.Status objects that match the given term in the given date range
        """
        term = "\"" + term + "\""

        return self.searchTweetsRange(term, endDate)

    def searchFrom(self, user, tweets = []):
        """
        Searches all tweets sent TO a given user or users.

        Appends the to: statement to the front of a given username, then uses standard
        Twitter search function. Prints all returned tweets in the form:
        <Username TO>: <Tweet>

        Will run recursively for multiple users

        :param user: the user or users to search
        :return: a list of up to (16 * number of users to search) twitter.Status objects
        """
        usrTemp = ""

        user = user.replace(" ","")#remove all whitespace

        if ( user.rfind(";") == len(user)-1 ): #case where the last char is a semicolon
            user = user[:len(user)-1] #remove said semicolon so array indices don't blow up
            self.searchFrom(user, tweets) #case where there are many trailing semicolons
        if (user.find(";") != -1):
            usrTemp = "from:" + user[:user.find(";")]
            user = user[user.find(";") + 1:]
            tweetTemp = api.GetSearch(usrTemp, count=16)

            tweets += tweetTemp
            self.searchFrom(user, tweets)

        #at this point, there is still the final name in the list (no more semicolons though)
        #so we need to perform a search on that single name

        user = "from:" + user
        tweets += api.GetSearch(user, count=16)


        for tweet in tweets:
            try:
                print "%s: %s" % (tweet.GetUser().screen_name, tweet.GetText())
            except UnicodeEncodeError, e:
                print "A Tweet could not be decoded - likely uses characters unsupported by your charmap (like emojis): %s" % e

        return tweets

    def searchTo(self, user, tweets = []):
        """
        Searches all tweets sent TO a given user or users.

        Appends the to: statement to the front of a given username, then uses standard
        Twitter search function. Prints all returned tweets in the form:
        <Username FROM>: <Tweet>

        Will run recursively for multiple users

        :param user: the user or users to search
        :return: a list of up to (16 * number of users to search) twitter.Status objects
        """
        usrTemp = ""
        tweetTemp = None

        user = user.replace(" ","")#remove all whitespace

        if ( user.rfind(";") == len(user)-1 ): #case where the last char is a semicolon
            user = user[:len(user)-1] #remove said semicolon so array indices don't blow up
            self.searchTo(user, tweets) #in case there are many trailing semicolons
        if (user.find(";") != -1):
            usrTemp = "to:" + user[:user.find(";")]
            user = user[user.find(";") + 1:]
            tweetTemp = api.GetSearch(usrTemp, count=16)

            tweets += tweetTemp
            self.searchTo(user, tweets)

        #at this point, there is still the final name in the list (no more semicolons though)
        #so we need to perform a search on that single name

        user = "to:" + user
        tweets += api.GetSearch(user, count=16)


        for tweet in tweets:
            try:
                print "%s: %s" % (tweet.GetUser().screen_name, tweet.GetText(),)
            except UnicodeEncodeError, e:
                print "A Tweet could not be decoded - likely uses characters unsupported by your charmap (like emojis): %s" % e


        return tweets

    def validateDate(date):
        """
        Verifies that a given string is of the form YYYY-MM-DD and is a reasonable date

        Basically, this is the input validation function used by searching functions with date arguments

        :param date: A String
        :return: date if it is a valid date as defined above, 0 otherwise
        """
        if date == 0: return 0 # base case, when date is not specified
        valid = True
        try:
            year = int (date[:4])
            month = int (date[5:7])
            day = int (date[9:])
        except ValueError, e:
            print "All numerical elements of a date string must be integers. Searching all dates..."
            return 0
        if date[4] != "-" or date[7] != "-" or len(date) > 10\
                or year > 2015 or month > 12 or day > 31:
            print "Not a valid date string, searching all dates..."
            return 0

        return date


def main():
    global api
    this = TwitterAPI()
    if api._access_token_key == "": #API has not been initialized with real values
        print "Welcome to Izaak Branch's RueLaLa Application!\n"
        api = this.getAuthToken()
        print "Thank you for signing in. ",
    op = None
    query = ""
    valid = False
    sel = 0
    while not valid:
        print "Please refer to the listed options:\n"
        print "1. Tweet a Message\n" \
              "2. Search Tweets using standard Twitter search\n" \
              "3. Search Tweets for an exact phrase\n" \
              "4. Search Tweets for a phrase before a given date\n" \
              "5. Search Tweets for an exact phrase before a given date\n" \
              "6. Search for Tweets FROM a person or people\n" \
              "7. Search for Tweets TO a person or people\n" \
              "8. Exit Application"
        sel = raw_input("Selection: ")

        if sel == "1":
            query = raw_input("Enter your Tweet: ")
            op = this.sendTweet(query)
            valid = True
        elif sel == "2":
            query = raw_input("Enter the term you would like to search for: ")
            this.searchTweets(query)
            valid = True
        elif sel == "3":
            query = raw_input("Enter the term you would like to exactly search for: ")
            this.searchTermExact(query)
            valid = True
        elif sel == "4":
            query = raw_input("Enter the term you would like to search for: ")
            endDate = raw_input("Enter the end date to search from in YYYY-MM-DD format: Enter 0 to not specify an end date:")
            endDate = this.validateDate(endDate)
            this.searchTweetsRange(query, endDate)
            valid = True
        elif sel == "5":
            query = raw_input("Enter the term you would like to exactly search for: ")
            endDate = raw_input("Enter the end date to search from in YYYY-MM-DD format: Enter 0 to not specify an end date:")
            endDate = this.validateDate(endDate)
            this.searchTweetsRangeExact(query, endDate)
            valid = True
        elif sel == "6":
            query = raw_input("Enter the username(s) to search tweets FROM, separated by semicolon (;) characters: ")
            this.searchFrom(query, [])
            valid = True
        elif sel == "7":
            query = raw_input("Enter the username(s) to search tweets TO, separated by semicolon (;) characters: ")
            this.searchFrom(query, [])
            valid = True
        elif sel == "8":
            print "Thank you for your consideration."
            valid = True
            exit(1)
        else:
            print "\n%s is not a valid option. Try again. " % sel,

    Again()

def Again():
    sel = raw_input("Would you like to perform another operation? [y/n]")
    if sel == 'y':
        print ''
        main()
    elif sel == 'n':
        print '\nThank you for your consideration.'
        exit(1)
    else:
        print "\nInvalid input. ",
        Again()

if __name__ == "__main__":
    main()
















