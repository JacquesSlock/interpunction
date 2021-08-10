import queue
from multiprocessing import Process, Queue
import threading
import time
from gtts import gTTS
import pyttsx3
from playsound import playsound
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import tkinter as tk

firstTimeRun = True;

class FacebookComments:
    def __init__(self, queue, browser):
        self.queue = queue
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        self.language = 'dutch'
        # to display voices
        # for voice in engine.getProperty('voices'):
        #     print(voice)
        self.change_voice(engine, self.language, "male")

        self.extract(browser, "https://www.facebook.com/hln.be",1)

    def change_voice(self, engine, language, gender):
        # for voice in engine.getProperty('voices'):
        #     print(voice)
        for voice in engine.getProperty('voices'):
            if self.language in voice.name and gender == voice.gender:
                engine.setProperty('voice', voice.id)
                return True

        raise RuntimeError("language '{}' for gender '{}' not found".format(language, gender))
    def find_comments(self, bs_data):
        with open('./bs.html',"w", encoding="utf-8") as file:
            file.write(str(bs_data.prettify()))
        k = bs_data.find_all(class_="kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql")
        postBigDict = list()
        k.pop(0)
        k.pop(0)
        for item in k:
            # print(item.text)
            text = item.text + " "
            if(not 'See more' in text and len(text) < 200):
                # engine.say(text)
                # engine.runAndWait()
                self.queue.put(text)
                self.speak(text)
                pass
    def speak(self, text):
        tts = gTTS(text, lang="nl")
        tts.save("comment.mp3")
        #
        # frame.add_text(text)
        playsound('comment.mp3')

    def _count_needed_scrolls(self, browser, numOfPost):
        lenOfPage = int(numOfPost / 8)
        print("Number Of Scrolls Needed " + str(lenOfPage))
        return lenOfPage


    def _scroll(self, browser, lenOfPage):
        lastCount = -1
        match = False

        while not match:
            lastCount += 1

            # wait for the browser to load, this time can be changed slightly ~3 seconds with no difference, but 5 seems
            # to be stable enough
            time.sleep(.1)

            browser.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return "
                    "lenOfPage;")

            if lastCount == lenOfPage:
                match = True

    def show_all_comments(self, browser):
        print("scrolling for all comments")
        rankDropdownsXPath = '//div[contains(@class, "bp9cbjyn j83agx80 kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x h3fqq6jp")]'
        rankDropdowns = browser.find_elements_by_xpath(rankDropdownsXPath)
        #print(rankDropdowns)
        rankXPath = '//div[contains(@class, "j83agx80 cbu4d94t ew0dbk1b irj2b8pg")]'
        # print(rankDropdowns)
        i = 0
        for rankDropdown in rankDropdowns:
            #click to open the filter modal
            action = webdriver.common.action_chains.ActionChains(browser)

            try:
                action.move_to_element_with_offset(rankDropdown, 5, 5)
                action.perform()
                rankDropdown.click()
                # time.sleep(.5)
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

    def load_more_comments(self, browser):
        print("Load more comments")
        self.queue.put("inladen commentaar")
        self.speak("inladen commentaar")
        moreCommentsXPath = '//div[contains(@class,"oajrlxb2 bp9cbjyn g5ia77u1 mtkw9kbi tlpljxtp qensuy8j ppp5ayq2 goun2846 ccm00jje s44p3ltw mk2mc5f4 rt8b4zig n8ej3o3l agehan2d sk4xxmp2 rq0escxv nhd2j8a9 pq6dq46d mg4g778l btwxx1t3 g5gj957u p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x tgvbjcpo hpfvmrgz jb3vyjys p8fzw8mz qt6c0cv9 a8nywdso l9j0dhe7 i1ao9s8h esuyzwwr f1sip0of du4w35lb lzcic4wl abiwlrkh gpro0wi8 m9osqain buofh1pr")]'
        moreComments = browser.find_elements_by_xpath(moreCommentsXPath)
        print("Scrolling through to click on more comments")
        # to this for max 1 minute
        t_end = time.time() + 60 * 1
        while len(moreComments) != 0 and time.time() < t_end:
            for moreComment in moreComments:
                action = webdriver.common.action_chains.ActionChains(browser)
                try:
                    # move to where the comment button is
                    action.move_to_element_with_offset(moreComment, 5, 5)
                    action.perform()
                    moreComment.click()
                    # time.sleep(.5)
                except:
                    # do nothing right here
                    pass
            moreComments = browser.find_elements_by_xpath(moreCommentsXPath)
            for link in moreComments[:]:
                try:
                    if(link.text=="" or "Hide" in link.text):
                        # print(link.text)
                        moreComments.remove(link)
                except:
                    pass
    def click_see_more(self, browser):
        print("Pressing see more")
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

    def extract(self, browser, page, numOfPost):
        self.queue.put("loading")
        self.speak("loading")
        browser.get(page)

        lenOfPage = self._count_needed_scrolls(browser, numOfPost)
        self._scroll(browser, lenOfPage)
        self.load_more_comments(browser)
        self.click_see_more(browser)
        self.click_see_more(browser)
        # Now that the page is fully scrolled, grab the source code.
        source_data = browser.page_source

        # Throw your source into BeautifulSoup and start parsing!
        bs_data = bs(source_data, 'html.parser')
        postBigDict = self.find_comments(bs_data)


class ThreadedClient:
    """ Launch the main part of the GUI and the worker thread.
        periodic_call() and end_application() could reside in the GUI part, but
        putting them here keeps all the thread controls in a single place.
    """
    def __init__(self, master):
        # start browser
        self.browser = self.start_up()


        self.master = master
        self.queue = queue.Queue()

        # Set up the GUI part.
        self.gui = ShowText(master, self.queue, self.end_application)

        # Set up the background processing thread.
        self.running = True
        self.thread = threading.Thread(target=self.workerthread)
        self.thread.start()

        # Start periodic checking of the queue.
        self.periodic_call(200)

    def _login(self, browser, email, password):
        browser.get("http://facebook.com")
        try:
            browser.find_element_by_xpath('//button[@data-testid="cookie-policy-dialog-accept-button"]').click()
            time.sleep(.5)
        except Exception as e:
            pass
        try:
            browser.find_element_by_xpath('//button[@data-testid="cookie-policy-dialog-accept-button"]').click()
            time.sleep(.5)
        except Exception as e:
            pass
        browser.find_element_by_name("email").send_keys(email)
        try:
            browser.find_element_by_xpath('//button[@data-testid="cookie-policy-dialog-accept-button"]').click()
            time.sleep(.5)
        except Exception as e:
            pass
        browser.find_element_by_name("pass").send_keys(password)
        try:
            browser.find_element_by_xpath('//button[@data-testid="cookie-policy-dialog-accept-button"]').click()
            time.sleep(.5)
        except Exception as e:
            pass
        browser.find_element_by_xpath('//button').click()
        browser.maximize_window()

    def start_up(self):
        with open('facebook_credentials.txt') as file:
            self.EMAIL = file.readline().split('"')[1]
            self.PASSWORD = file.readline().split('"')[1]
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
        self._login(browser, self.EMAIL, self.PASSWORD)
        return browser

    def periodic_call(self, delay):
        """ Every delay ms process everything new in the queue. """
        self.gui.process_incoming()
        if not self.running:
            sys.exit(1)
        self.master.after(delay, self.periodic_call, delay)
    # Runs in separate thread - NO tkinter calls allowed.
    def workerthread(self):
        while self.running:
            # try:
            FacebookComments(self.queue, self.browser)
            # except Exception as e:
            #     print("Error in fbcomments")


    def end_application(self):
        self.running = False  # Stop queue checking.
        self.master.quit()

class ShowText(tk.Frame):
    def __init__(self, master, queue, end_command):
        self.queue = queue
        self.master = master
        master.text = tk.Text(master, height=6, width=40, highlightthickness = 0, borderwidth=0)
        master.text.tag_configure("centerText", justify='center')
        master.text['background']='black'
        master.text['foreground']='white'
        # master.text.config(anchor=tk.CENTER)
        master.text.pack(side="top", fill="both", expand=True, padx= "25",pady= "150")
    def clearToTextInput(self):
        self.master.text.delete("1.0","end")
    def add_text(self, text):
        self.clearToTextInput()
        try:
        # some code
            self.typeit(self.master.text, "1.0", text)
            # self.master.text.insert("end", text)
            pass
        except KeyboardInterrupt:
            print ('All done')
            # If you actually want the program to exit
            raise
    def typeit(self, widget, index, string):
       if len(string) > 0:
          widget.insert("end", string[0])
          widget.tag_add("centerText", "1.0", "end")
          if len(string) > 1:
             # compute index of next char
             index = widget.index("%s + 1 char" % index)
             self.master.text.see("end")
             # type the next character in half a second
             widget.after(70, self.typeit, widget, index, string[1:])

    def process_incoming(self):
        """ Handle all messages currently in the queue. """
        while self.queue.qsize():
            try:
                text = self.queue.get_nowait()
                self.add_text(text)
            except queue.Empty:  # Shouldn't happen.
                pass

if __name__ == "__main__":
    root = tk.Tk()

    root['bg'] = 'black'
    root.attributes('-fullscreen', True)
    root.option_add('*Font', 'Arial 72')
    client = ThreadedClient(root)
    root.mainloop()
