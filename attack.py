#!/usr/bin/env python
from database import *
from hkgolden import *
from proxy import *
from multiprocessing import Pool
from selenium import webdriver
from time import sleep
import sys

def getUnrepliedPostList(centID):
    postIDLowerLimit = int(getSetting("postIDLowerLimit"))
    unrepliedPostList = []
    print("Attempting to get what {} posted recently...".format(centID))
    profileHtml = getProfilePage(centID)
    if not profileHtml:
        print("Failed to get {}'s profile page!".format(centID))
        return False
    username = getUsername(profileHtml)
    msg = getWeapon(centID).format(username)
    print("Username: {} (ID: {})".format(username, centID))
    for postID in getPostList(profileHtml):
        if postID > postIDLowerLimit and (not isThisPostReplyed(centID, postID)):
            print("Will reply in {}'s post {}!".format(username, postID))
            unrepliedPostList.append(postID)
        elif postID <= postIDLowerLimit:
            print("It seems that {}'s post {} is too old (<={}).".format(username, postID, postIDLowerLimit))
        else:
            print("It seems that {}'s post {} is already replied.".format(username, postID))
    return {centID: [unrepliedPostList, msg]}

def main():
    print("Initializing...")
    if not areTablesExist():
        print("Creating databases...")
        if (not createTables()) or (not createProxyTables()):
            raise Exception("Cannot create databases!")
        elif "import" not in sys.argv:
            result = importProxies(scriptPath + "/proxies.txt")
            if result and result > 0:
                print("{0} proxies imported!".format(result))
            else:
                print("No proxy is imported.")

    postedSleepTime, workerSleepTime = int(getSetting("postedSleepTime")), int(getSetting("workerSleepTime"))
    settings = "email, password, postedSleepTime, postIDLowerLimit, workerSleepTime, generalTimeout, databaseThreads"

    if len(sys.argv) >= 2:
        if (sys.argv[1] == "start"):
            browser = webdriver.PhantomJS()
            login(browser, getSetting("email"), getSetting("password"))
            while 1:
                centsList = getCentsList()
                if centsList:
                    postsDict = {}
                    with Pool(processes = int(getSetting("databaseThreads"))) as pool:
                        result = pool.map(getUnrepliedPostList, centsList)
                    for dict in result:
                        for key, list in dict.items():
                            postsDict[key] = list
                    for centID, unrepliedPosts in postsDict.items():
                        msg = unrepliedPosts[1]
                        for postID in unrepliedPosts[0]:
                            print("Replying '{}...' in {}'s post {}!".format(msg[:20], centID, postID))
                            if (reply(browser, postID, msg)):
                                saveReplyedPost(centID, postID)
                                print(bcolors["OKBLUE"] + "Successfully replied!" + bcolors["ENDC"] + " Waiting for {0}s...".format(postedSleepTime))
                                time.sleep(postedSleepTime)
                            else:
                                print(bcolors["FAIL"] + "ERROR in replying {}'s post {}! Can't reach server, or posted too fast, or thread is locked?".format(centID, postID) + bcolors["ENDC"])
                    print(bcolors["OKBLUE"] + "Finished this process! Sleeping for {0}s...".format(workerSleepTime) + bcolors["ENDC"])
                    time.sleep(workerSleepTime)
                else:
                    print("Please add at least an userID")
                    print("Usage: attack.py add <userID> <message>")
                    break
        elif (sys.argv[1] == "add" or sys.argv[1] == "new"):
            try:
                success = newCent(int(sys.argv[2]), sys.argv[3])
                if not success:
                    print("userID {} already exists in database".format(int(sys.argv[2])))
                else:
                    print("Added userID: {}".format(int(sys.argv[2])))
            except IndexError:
                print("Usage: attack.py add <userID> <message>")
            except ValueError:
                print("userID must be integer")
        elif (sys.argv[1] == "del" or sys.argv[1] == "delete" or sys.argv[1] == "remove"):
            try:
                success = delCent(int(sys.argv[2]))
                if not success:
                    print("userID {} does not exists in database".format(int(sys.argv[2])))
                else:
                    print("Deleted userID {} from database".format(int(sys.argv[2])))
            except IndexError:
                print("Usage: attack.py del <userID>")
            except ValueError:
                print("userID must be integer")
        elif (sys.argv[1] == "message" or sys.argv[1] == "msg"):
            try:
                if len(sys.argv) == 4:
                    success = changeWeapon(int(sys.argv[2]), sys.argv[3])
                    if not success:
                        print("userID {} does not exists in database".format(int(sys.argv[2])))
                    else:
                        print("Message of userID {} changed".format(int(sys.argv[2])))
                else:
                    result = getWeapon(int(sys.argv[2]))
                    if not result:
                        print("userID {} does not exists in database".format(int(sys.argv[2])))
                    else:
                        print(result)
            except IndexError:
                print("Usage: attack.py msg <userID> (<new msg>)")
            except ValueError:
                print("userID must be integer")
        elif (sys.argv[1] == "list"):
            print(getCentsList())
        elif (sys.argv[1] == "setting" or sys.argv[1] == "settings"):
            if len(sys.argv) == 4:
                success = changeSetting(sys.argv[2], sys.argv[3])
                if not success:
                    print("No such a setting!")
                else:
                    print("Successfully changed {}".format(sys.argv[2]))
            elif len(sys.argv) == 3:
                result = getSetting(sys.argv[2])
                if result:
                    print(result)
                else:
                    print("No such a setting!")
            else:
                print("Usage: attack.py setting <setting> (<new value>) *() = optional")
                print("Settings list: " + settings)
        elif (sys.argv[1] == "sql"):
            if len(sys.argv) >= 3:
                conn = getConn()
                cur = conn.cursor()
                cur.execute(sys.argv[2])
                for row in cur.fetchall():
                    print(row)
                cur.close()
                conn.close()
                conn = None
            else:
                print("Usage: attack.py sql <custom SQL statement>")
        elif (sys.argv[1] == "import"):
            if len(sys.argv) >= 3:
                result = False
                try:
                    result = importProxies(sys.argv[2])
                except:
                    try:
                        result = importProxies(scriptPath + "/" + sys.argv[2])
                    except:
                        print("Proxy file not found!")
                if result and result > 0:
                    print("{0} proxies imported!".format(result))
                else:
                    print("No proxy is imported.")
            else:
                print("Usage: attack.py import <path to proxy file>")
        elif (sys.argv[1] == "help"):
            if len(sys.argv) >= 3:
                if (sys.argv[2] == "start"):
                    print("Starts the attack. You must have at least 1 50cent user ID specified.")
                    print("Usage: attack.py start")
                elif (sys.argv[2] == "add"):
                    print("Add an user to 50cents list so that it will be sniped. <message> is what you will reply on the same thread if that 50cent has replied on a thread.")
                    print("Usage: attack.py add <userID> <message>")
                elif (sys.argv[2] == "del"):
                    print("Removes an user from 50cents list so that he will be no longer sniped.")
                    print("Usage: attack.py del <userID>")
                elif (sys.argv[2] == "msg"):
                    print("Sees what you will reply on the same thread if a 50cent has replied on a thread.")
                    print("You are able to change the message.")
                    print("Usage: attack.py msg <userID> (<new msg>) *() = optional")
                elif (sys.argv[2] == "list"):
                    print("Prints the list of 50cent member stored in SQL")
                    print("Usage: attack.py list")
                elif (sys.argv[2] == "import"):
                    print("Parses and imports proxy file into database. Default import proxies.txt. \nFormat: <ip>:<port>:<type(3|4|5)>\\n")
                    print("Usage: attack.py import <path to proxy file>")
                elif (sys.argv[2] == "setting"):
                    if len(sys.argv) >= 4:
                        if (sys.argv[3] == "email"):
                            print("Your HKGolden login email.")
                        elif (sys.argv[3] == "password"):
                            print("Your HKGolden login password. Please beware that your password is stored in plain text in database.")
                        elif (sys.argv[3] == "postedSleepTime"):
                            print("How long will you wait after you have successfully replied to a thread. This is used to avoid the flood check. Default is 20")
                        elif (sys.argv[3] == "workerSleepTime"):
                            print("How long this program will sleep after an attack process. Default is 60.")
                        elif (sys.argv[3] == "postIDLowerLimit"):
                            print("You don't really want to reply to old thread, right? So post ID lesser or equal to postIDLowerLimit will be ignored. Default is 5000000")
                        elif (sys.argv[3] == "generalTimeout"):
                            print("The general time out. Default is 30")
                        elif (sys.argv[3] == "databaseThreads"):
                            print("Database threads. Default is 16")
                        else: 
                            print("Settings list: " + settings)
                            print("To get help of each setting: attack.py help setting <setting>")
                    else:
                        print("Get the setting value or change a setting.")
                        print("Settings list: " + settings)
                        print("Usage: attack.py setting <setting> (<new value>) *() = optional")
                        print("To get help of each setting: attack.py help setting <setting>")
                elif (sys.argv[2] == "sql"):
                    print("Executes custom SQL statement, for advanced users only.")
                    print("Usage: attack.py sql <custom SQL statement>")
                elif (sys.argv[2] == "help"):
                    print("Displays this message.")
                    print("Usage: attack.py sql help <command>")
                else: 
                    print("Invalid command")
                    print("Commands list: start, add, del, msg, list, setting, sql, help, import")
                    print("To get help: attack.py help <command>")
            else:
                print("attack.py v0.0.3")
                print("Author: Saren (HKGID: 199152)")
                print("This tool is used to attack on99 50cents on HKGolden.")
                print("For example, if a 50cent has replied on a thread, or it posted a thread on HKGolden,")
                print("this tool will find that thread and reply a message on that thread automatically,")
                print("letting everyone know that 50cent is a 50cent.\n")
                print("Commands list: start, add, del, msg, list, setting, sql, help, import")
                print("To get help: attack.py help <command>")
        else:
            print("Invalid action")
            print("To get help: attack.py help")
    else:
        print("You didn't input any arguments.")
        print("To get help: attack.py help")
        
if __name__ == "__main__":
    main()