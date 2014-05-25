#!/usr/bin/env python
from random import randint, choice, random
from pyquery import PyQuery as pq
from database import *
from proxy import *
from browserconn import *
import globalvar
import re
import time

generalTimeout = int(getSetting("generalTimeout"))

def login(browser, email, password):
    print("Going to login page...")
    browser.set_page_load_timeout(generalTimeout)
    server = choice([i for i in range(1,4)])
    browser.get("http://m{0}.hkgolden.com/login.aspx".format(server))
    emailField = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_txt_email']")
    passwordField = browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_txt_pass']")
    emailField.send_keys(email)
    passwordField.send_keys(password)
    print("Submitting login info...")
    browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_linkb_login']").click()
    if "login.aspx" in browser.current_url:
        raise Exception("Not logged in! Wrong email/password, server error or banned?")
        
def reply(browser, postID, msg):
    try:
        browser.set_page_load_timeout(generalTimeout)
        server = choice([i for i in range(1,4)])
        url = "http://m{0}.hkgolden.com/post.aspx?mt=Y&id={1}".format(server, postID)
        browser.get(url)
        textField = browser.find_element_by_xpath("//textarea[@id='ctl00_ContentPlaceHolder1_messagetext']")
        textField.send_keys(msg)
        browser.find_element_by_xpath("//input[@id='ctl00_ContentPlaceHolder1_btn_Submit']").click()
        elem = browser.find_element_by_xpath("//*")
        html = elem.get_attribute("outerHTML")
        replySuccess = pq(html)(".ViewTitle")
        if replySuccess:
            return True
        else:
            error = re.findall("Error #(\d+): (.+)", html)
            if not len(error):
                print(bcolors["WARNING"] + "Unknown error!" + bcolors["ENDC"])
                return False
            if error[0][0] == "27" or error[0][0] == "29":
                print(bcolors["WARNING"] + "It seems thread is locked." + bcolors["ENDC"])
                return True
            print(bcolors["WARNING"] + "Error {0}: {1}".format(error[0][0], error[0][1]) + bcolors["ENDC"])
            return False
    except Exception as e:
        print(bcolors["WARNING"] + "Reply time out!", end=bcolors["ENDC"])
        print(repr(e)[:50])
        return False
    
def waitForElement(browser, path, timeOut):
    timeLimit = time.time() + int(timeOut)
    while time.time() < timeLimit:
        try:
            browser.find_element_by_xpath(path)
            return True
        except:
            time.sleep(0.5)
    return False

def getProfilePage(userID):
    servers = [i for i in range(1,16) if i < 10 or i > 13]
    checkPath = "//tr[@style='background-color: #FFFFFF']"
    time.sleep(random()*3)
    while 1:
        try:
            proxy = getProxy()

            if proxy[3] == 3:
                service_args = ['--proxy={0}:{1}'.format(proxy[1], proxy[2]), '--proxy-type={0}'.format("http")]
            elif proxy[3] == 4:
                service_args = ['--proxy={0}:{1}'.format(proxy[1], proxy[2]), '--proxy-type={0}'.format("socks4")]
            elif proxy[3] == 5:
                service_args = ['--proxy={0}:{1}'.format(proxy[1], proxy[2]), '--proxy-type={0}'.format("socks5")]

            url = "http://forum{0}.hkgolden.com/ProfilePage.aspx?userid={1}".format(choice(servers), userID)
            
            print("Proxy {0}(r={1}): Getting {2}'s page...".format(proxy[1], round(proxy[4], 3), userID))

            browser = getBrowser(service_args)
            browser.set_page_load_timeout(generalTimeout)
            browser.get(url)

            print("Proxy {0}: Page loaded! ".format(proxy[1]), end="")
            multiplyRating(proxy[0], 0.9)
            browser.find_element_by_xpath("//select[@name='ctl00$ContentPlaceHolder1$mainTab$mainTab1$filter_type']/option[@value='all']").click()
            print("Proxy {0}: Waiting for element... ".format(proxy[1]), end="")
            multiplyRating(proxy[0], 0.75)
            if waitForElement(browser, checkPath, generalTimeout):
                elem = browser.find_element_by_xpath("//*")
                html = elem.get_attribute("outerHTML")
                browser.quit()
                if getUsername(html):
                    print(bcolors["OKGREEN"] + "Proxy {0}: Success! ".format(proxy[1]), end=bcolors["ENDC"])
                    multiplyRating(proxy[0], 0.6)
                    return html
                else:
                    return False
            else:
                raise Exception("Time out")
        except Exception as e:
            print(bcolors["WARNING"] + "Proxy {0}: Error! Trying another proxy. ".format(proxy[1]), end=bcolors["ENDC"])
            print(repr(e)[:50], end="...")
            multiplyRating(proxy[0], 2)
            browser.quit()

def getUsername(html):
    return pq(html)("#ctl00_ContentPlaceHolder1_tc_Profile_tb0_lb_nickname").html()

def getPostList(html):
    return [int(id) for id in list(set(re.findall("view.aspx\?message=([0-9]+)", html)))]
