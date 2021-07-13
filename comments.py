import argparse
import time
import json
import csv
from gtts import gTTS
from playsound import playsound
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs


with open('facebook_credentials.txt') as file:
    EMAIL = file.readline().split('"')[1]
    PASSWORD = file.readline().split('"')[1]



def _extract_html(bs_data):
    #Add to check
    with open('./bs.html',"w", encoding="utf-8") as file:
        file.write(str(bs_data.prettify()))

    k = bs_data.find_all(class_="kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql")
    postBigDict = list()

    for item in k:
        print(item.text)
        if(len(item.text)>100):
            language = 'nl'

            # Passing the text and language to the engine,
            # here we have marked slow=False. Which tells
            # the module that the converted audio should
            # have a high speed
            tts = gTTS(text=item.text, lang=language)

            tts.save("comment.mp3")
            #
            playsound('comment.mp3')
        #print(item.find_elements_by_xpath(".//*").text)
        #postDict = dict()
        #postDict['Comments'] = _extract_comments(item)

        #Add to check
        #postBigDict.append(postDict)
        #with open('./postBigDict.json','w', encoding='utf-8') as file:
        #    file.write(json.dumps(postBigDict, ensure_ascii=False).encode('utf-8').decode())

    return postBigDict


def _login(browser, email, password):
    browser.get("http://facebook.com")
    browser.maximize_window()
    browser.find_element_by_name("email").send_keys(email)
    browser.find_element_by_name("pass").send_keys(password)
    browser.find_element_by_id('u_0_d').click()
    time.sleep(5)


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
        time.sleep(5)

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
        rankDropdownsXPath = '//div[contains(@class, "h3fqq6jp hcukyx3x oygrvhab cxmmr5t8 kvgmc6g5 j83agx80 bp9cbjyn")]'
        rankDropdowns = browser.find_elements_by_xpath(rankDropdownsXPath)
        #print(rankDropdowns)
        rankXPath = '//div[contains(@class, "bp9cbjyn j83agx80 btwxx1t3 buofh1pr i1fnvgqd hpfvmrgz")]'
        for rankDropdown in rankDropdowns:
            #click to open the filter modal
            action = webdriver.common.action_chains.ActionChains(browser)

            try:
                action.move_to_element_with_offset(rankDropdown, 5, 5)
                action.perform()
                rankDropdown.click()
            except:
                pass

            # if modal is opened filter comments
            ranked_unfiltered = browser.find_elements_by_xpath(rankXPath) # RANKED_UNFILTERED => (All Comments)
            try:
                action.move_to_element_with_offset(ranked_unfiltered, 5, 5)
                action.perform()
                ranked_unfiltered.click()
            except:
                pass

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
        seeMoreXPath = '//div[contains(@class,"oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8 lrazzd5p") and text()="See more"]'
        seeMores = browser.find_elements_by_xpath(seeMoreXPath)
        print(seeMores)
        for seeMore in seeMores:
            #click to open the filter modal
            action = webdriver.common.action_chains.ActionChains(browser)

            try:
                action.move_to_element_with_offset(seeMore, 5, 5)
                action.perform()
                seeMore.click()
            except:
                pass
        #first uncollapse collapsed comments
        # IDEA: search for parent,o
        # #unCollapseCommentsButtonsXPath = '//div[contains(@class,"oajrlxb2 g5ia77u1 rq0escxv nhd2j8a9 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gpro0wi8")]'
        # unCollapseCommentsButtonsXPath = '//div[contains(@class,"oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl oo9gr5id gpro0wi8 lrazzd5p")]'
        # unCollapseCommentsButtons = browser.find_elements_by_xpath(unCollapseCommentsButtonsXPath)
        # print(unCollapseCommentsButtons)
        # while len(unCollapseCommentsButtons) > 2:
        #     for unCollapseComment in unCollapseCommentsButtons:
        #         action = webdriver.common.action_chains.ActionChains(browser)
        #         try:
        #             # move to where the un collapse on is
        #             action.move_to_element_with_offset(unCollapseComment, 5, 5)
        #             action.perform()
        #             unCollapseComment.click()
        #         except:
        #             # do nothing right here
        #             pass
        #     unCollapseCommentsButtons = browser.find_elements_by_xpath(unCollapseCommentsButtonsXPath)
        #     for seeMore in unCollapseCommentsButtons[:]:
        #         if("less" in seeMore.text):
        #             print(link.text)
        #             unCollapseCommentsButtons.remove(seeMore)
        #         pass

    # Now that the page is fully scrolled, grab the source code.
    source_data = browser.page_source

    # Throw your source into BeautifulSoup and start parsing!
    bs_data = bs(source_data, 'html.parser')

    postBigDict = _extract_html(bs_data)
    #browser.close()

    return postBigDict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Page Scraper")
    required_parser = parser.add_argument_group("required arguments")
    required_parser.add_argument('-page', '-p', help="The Facebook Public Page you want to scrape", required=True)
    required_parser.add_argument('-len', '-l', help="Number of Posts you want to scrape", type=int, required=True)
    optional_parser = parser.add_argument_group("optional arguments")
    optional_parser.add_argument('-infinite', '-i',
                                 help="Scroll until the end of the page (1 = infinite) (Default is 0)", type=int,
                                 default=0)
    optional_parser.add_argument('-usage', '-u', help="What to do with the data: "
                                                      "Print on Screen (PS), "
                                                      "Write to Text File (WT) (Default is WT)", default="CSV")

    # optional_parser.add_argument('-comments', '-c', help="Scrape ALL Comments of Posts (y/n) (Default is n). When "
    #                                                      "enabled for pages where there are a lot of comments it can "
    #                                                      "take a while", default="No")
    args = parser.parse_args()

    infinite = False
    if args.infinite == 1:
        infinite = True

    # scrape_comment = False
    # if args.comments == 'y':
    scrape_comment = True

    postBigDict = extract(page=args.page, numOfPost=args.len, infinite_scroll=infinite, scrape_comment=scrape_comment)


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
