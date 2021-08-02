import argparse
import time
import json
import csv
from gtts import gTTS
import pyttsx3
from playsound import playsound
from io import BytesIO
import time
import threading
try:
    # python 2.x
    import Tkinter as tk
except ImportError:
    # python 3.x
    import tkinter as tk

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs


# engine = pyttsx3.init()
# voices = engine.getProperty("voices")
# for voice in voices:
#     print(voice, voice.id)
#
# engine.setProperty('voice', 'dutch')
# engine.say("hello everyone")
# engine.runAndWait()
with open('facebook_credentials.txt') as file:
    EMAIL = file.readline().split('"')[1]
    PASSWORD = file.readline().split('"')[1]




def _extract_html(bs_data):
    #Add to check
    with open('./bs.html',"w", encoding="utf-8") as file:
        file.write(str(bs_data.prettify()))

    k = bs_data.find_all(class_="kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql")
    postBigDict = list()
    k.pop(0)
    k.pop(0)
    for item in k:
        # print(item.text)
        text = item.text
        if(len(text)>100):
            tts = gTTS(text, lang=language)

            tts.save("comment.mp3")
            #
            frame.add_text(text)
            playsound('comment.mp3')
            pass
            # words = item.text.split()
            # # easier to show words
            # for word in words:
            #     tts = gTTS(word, lang=language)
            #     tts.save("comment.mp3")
            #     playsound('comment.mp3')
            #     pass
    return postBigDict


def _login(browser, email, password):
    browser.get("http://facebook.com")
    browser.maximize_window()
    browser.find_element_by_xpath('//button[@data-testid="cookie-policy-dialog-accept-button"]').click()
    browser.find_element_by_name("email").send_keys(email)
    browser.find_element_by_name("pass").send_keys(password)
    # browser.find_element_by_id('u_0_d_jk').click()
    browser.find_element_by_xpath('//button').click()
    time.sleep(1)


def _count_needed_scrolls(browser, infinite_scroll, numOfPost):
    if infinite_scroll:
        lenOfPage = browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;"
        )
    else:
        # roughly 8 post per scroll kindaOf
        lenOfPage = int(numOfPost / 8)
    print("Number Of Scrolls Needed " + str(lenOfPage))
    return lenOfPage


def _scroll(browser, infinite_scroll, lenOfPage):
    lastCount = -1
    match = False

    while not match:
        if infinite_scroll:
            lastCount = lenOfPage
        else:
            lastCount += 1

        # wait for the browser to load, this time can be changed slightly ~3 seconds with no difference, but 5 seems
        # to be stable enough
        time.sleep(1)

        if infinite_scroll:
            lenOfPage = browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")
        else:
            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                "lenOfPage;")

        if lastCount == lenOfPage:
            match = True


def extract(page, numOfPost, infinite_scroll=False, scrape_comment=False):
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    option.add_argument("--disable-extensions")

    # Pass the argument 1 to allow and 2 to block
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    # chromedriver should be in the same folder as file
    browser = webdriver.Chrome(executable_path="./chromedriver", options=option)
    _login(browser, EMAIL, PASSWORD)
    browser.get(page)
    lenOfPage = _count_needed_scrolls(browser, infinite_scroll, numOfPost)
    _scroll(browser, infinite_scroll, lenOfPage)

    # click on all the comments to scrape them all!
    # TODO: need to add more support for additional second level comments
    # TODO: ie. comment of a comment

    if scrape_comment:
        #second set comment ranking to show all comments
        #rankDropdowns = browser.find_elements_by_class_name('h3fqq6jp hcukyx3x oygrvhab cxmmr5t8 kvgmc6g5 j83agx80 bp9cbjyn') #select boxes who have rank dropdowns
        rankDropdownsXPath = '//div[contains(@class, "bp9cbjyn j83agx80 kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x h3fqq6jp")]'
        rankDropdowns = browser.find_elements_by_xpath(rankDropdownsXPath)
        #print(rankDropdowns)
        rankXPath = '//div[contains(@class, "j83agx80 cbu4d94t ew0dbk1b irj2b8pg")]'
        print(rankDropdowns)
        i = 0
        for rankDropdown in rankDropdowns:

            #click to open the filter modal
            action = webdriver.common.action_chains.ActionChains(browser)

            try:
                action.move_to_element_with_offset(rankDropdown, 5, 5)
                action.perform()
                rankDropdown.click()
                time.sleep(.5)
                try:
                    action.move_by_offset(0, -20)    # 10px to the right, 20px to bottom
                    action.click()
                    action.perform()
                    # ranked_unfiltered = browser.find_elements_by_xpath(rankXPath) # RANKED_UNFILTERED => (All Comments)
                    # action.move_to_element_with_offset(ranked_unfiltered[i], 0, 0)
                    # action.perform()
                    # ranked_unfiltered[i].click()
                    # i = i + 1
                except Exception as e:
                    print(e)
                    print("niet gevonden")
                    # pass
            except Exception as e:
                print(e)
                print("oeps")
                # pass

            # if modal is opened filter comments


        time.sleep(10)
        moreCommentsXPath = '//div[contains(@class,"oajrlxb2 bp9cbjyn g5ia77u1 mtkw9kbi tlpljxtp qensuy8j ppp5ayq2 goun2846 ccm00jje s44p3ltw mk2mc5f4 rt8b4zig n8ej3o3l agehan2d sk4xxmp2 rq0escxv nhd2j8a9 pq6dq46d mg4g778l btwxx1t3 g5gj957u p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x tgvbjcpo hpfvmrgz jb3vyjys p8fzw8mz qt6c0cv9 a8nywdso l9j0dhe7 i1ao9s8h esuyzwwr f1sip0of du4w35lb lzcic4wl abiwlrkh gpro0wi8 m9osqain buofh1pr")]'
        moreComments = browser.find_elements_by_xpath(moreCommentsXPath)
        print("Scrolling through to click on more comments")
        while len(moreComments) != 0:
            for moreComment in moreComments:
                action = webdriver.common.action_chains.ActionChains(browser)
                try:
                    # move to where the comment button is
                    action.move_to_element_with_offset(moreComment, 5, 5)
                    action.perform()
                    moreComment.click()
                except:
                    # do nothing right here
                    pass
            moreComments = browser.find_elements_by_xpath(moreCommentsXPath)
            for link in moreComments[:]:
                try:
                    if(link.text=="" or "Hide" in link.text):
                        print(link.text)
                        moreComments.remove(link)
                except:
                    pass
        seeMoreXPath = '//div[text()="See more"]'
        seeMores = browser.find_elements_by_xpath(seeMoreXPath)
        # print(seeMores)
        for seeMore in seeMores:
            #click to open the filter modal
            action = webdriver.common.action_chains.ActionChains(browser)

            try:
                action.move_to_element_with_offset(seeMore, 5, 5)
                action.perform()
                seeMore.click()
            except:
                pass

    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source

    # Throw your source into BeautifulSoup and start parsing!
    bs_data = bs(source_data, 'html.parser')

    postBigDict = _extract_html(bs_data)
    #browser.close()

    return postBigDict


class ShowText(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        self.text = tk.Text(self, height=6, width=40)
        self.text['background']='black'
        self.text['foreground']='white'
        # self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        # self.text.configure(yscrollcommand=self.vsb.set)
        # self.vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
    def add_text(self, text):
        # self.after(100,self.add_timestamp)
        try:
        # some code

            text =  text
            self.text.insert("end", text)
            self.text.see("end")
        except KeyboardInterrupt:
            print ('All done')
            # If you actually want the program to exit
            raise



if __name__ == "__main__":
    # setup of window
    root =tk.Tk()
    root.attributes('-fullscreen', True)
    root.option_add('*Font', 'Arial 26')
    frame = ShowText(root)
    language = 'nl'
    parser = argparse.ArgumentParser(description="Facebook Page Scraper")
    optional_parser = parser.add_argument_group("optional arguments")
    optional_parser.add_argument('-infinite', '-i',
                                 help="Scroll until the end of the page (1 = infinite) (Default is 0)", type=int,
                                 default=0)
    optional_parser.add_argument('-usage', '-u', help="What to do with the data: "
                                                  "Print on Screen (PS), "
                                                  "Write to Text File (WT) (Default is WT)", default="CSV")

    args = parser.parse_args()

    infinite = False
    if args.infinite == 1:
        infinite = True

    # scrape_comment = False
    # if args.comments == 'y':
    scrape_comment = True

    # hardcoded page and number of posts
    # postBigDict = extract(page=args.page, numOfPost=args.len, infinite_scroll=infinite, scrape_comment=scrape_comment)
    postBigDict = extract(page="https://www.facebook.com/hln.be", numOfPost=1, infinite_scroll=infinite, scrape_comment=scrape_comment)

    # loop for showing text
    frame = ShowText(root)
    frame.pack(fill="both", expand=True)
    # root.mainloop()
    #TODO: rewrite parser
    if args.usage == "WT":
        with open('output.txt', 'w') as file:
            for post in postBigDict:
                file.write(json.dumps(post))  # use json load to recover

    elif args.usage == "CSV":
        with open('data.csv', 'w',) as csvfile:
           writer = csv.writer(csvfile)
           #writer.writerow(['Post', 'Link', 'Image', 'Comments', 'Reaction'])
           writer.writerow(['Post', 'Link', 'Image', 'Comments', 'Shares'])

           for post in postBigDict:
              writer.writerow([post['Post'], post['Link'],post['Image'], post['Comments'], post['Shares']])
              #writer.writerow([post['Post'], post['Link'],post['Image'], post['Comments'], post['Reaction']])

    else:
        for post in postBigDict:
            print(post)
    # while True:
    #     pass
    print("Finished")
