# from selenium.webdriver import Chrome
import json
import time
from configparser import ConfigParser

from selenium import webdriver


try:
    from types import SimpleNamespace as Namespace
except ImportError:
    # Python 2.x fallback
    from argparse import Namespace


groups_tlv_fname = "../groups_tlv"
posts_tlv_fname = "../posts_tlv"
posts_json_file = "../posts_tlv_json"

class Post:
    def __init__(self, text, img):
        self.text = text
        self.img = img


def get_credentials_from_file():
    file_name = '../config.ini'
    config = ConfigParser()
    config.read(file_name)

    account_section_name = config.sections()[0] #the name of the section can be any name
    account_list = list(config[account_section_name])

    user = config[account_section_name][account_list[0]]
    password = config[account_section_name][account_list[1]]

    return user, password


def post_to_groups(driver, groups_tlv, posts_tlv):
    j = 0
    while j < len(posts_tlv):
        for i in range(len(groups_tlv)):
            driver.get(groups_tlv[i])
            time.sleep(6)
            # driver.find_element_by_xpath("//div[@data-pagelet=\"GroupInlineComposer\"]//div[@role=\"button\"]").click()
            # time.sleep(6)
            # driver.find_element_by_xpath("//div[@aria-label=\"Photo/Video\"][@role=\"button\"]").click()
            driver.find_element_by_xpath("//div[@data-pagelet=\"GroupInlineComposer\"]//input")\
                .send_keys(posts_tlv[j].img)
            print("file name: ", posts_tlv[j])
            time.sleep(3)
            driver.find_element_by_xpath("//form[@method=\"POST\"]//div[@role=\"presentation\"]//span").send_keys(posts_tlv[j].text)

            time.sleep(3)
            driver.find_element_by_xpath("//div[@aria-label=\"Post\"]").click()
            if i == len(groups_tlv)-1:
                j = j+1
            time.sleep(10)


def post():
    user, pwd = get_credentials_from_file()

    options = define_chrome_options()
    driver = webdriver.Chrome("../chromedriver.exe", options=options)

    with driver:
        driver.maximize_window()
        driver.get("http://www.facebook.com")
        time.sleep(3)

        login(driver, pwd, user)
        groups_tlv = read_groups_from_file(groups_tlv_fname)
        # posts_tlv = read_groups_from_file(posts_tlv_fname)

        posts_tlv = posts_json()
        post_to_groups(driver, groups_tlv, posts_tlv)
        driver.close()


def read_groups_from_file(filename):
    # line_list = list()
    with open(filename) as file:
        line_list = [line.rstrip('\n') for line in file]

    return line_list


def define_chrome_options():
    options = webdriver.ChromeOptions()
    options.headless = False
    prefs = {"profile.default_content_setting_values.notifications": 2}  # disable notifications
    options.add_experimental_option("prefs", prefs)
    return options


def login(driver, pwd, user):
    driver.find_element_by_id("email").send_keys(user)
    driver.find_element_by_id("pass").send_keys(pwd)
    driver.find_element_by_name("login").click()

    time.sleep(10)


def post_decoder(obj):
    print("post decoder")
    return Post(obj['text'], obj['path'])


def posts_json():
    with open(posts_json_file, "r", encoding="utf8") as f:
        post_obj = json.load(f, object_hook=post_decoder)
        print(post_obj)
        return post_obj


if __name__ == "__main__":
    post()