# from selenium.webdriver import Chrome
import json
import time
from configparser import ConfigParser

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


try:
    from types import SimpleNamespace as Namespace
except ImportError:
    # Python 2.x fallback
    from argparse import Namespace


test_fname = "../test_groups"
test_fname2 = "../test_groups2"
# posts_tlv_fname = "../posts_tlv"
tlv_posts_json_file = "../posts_tlv_json"
jrs_posts_json_file = "../posts_jrs_json"

tlv_groups_file = "../tlv_groups"
jrs_groups_file = "../jrs_groups"
general_groups_file = "../general_groups"

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


def wait(driver, xpath, sec=10):
    try:
        print("wait: ", xpath)
        WebDriverWait(driver, sec)\
            .until(lambda d: d.find_element_by_xpath(xpath))
    except NoSuchElementException:
        print("exception in wait")
        raise NoSuchElementException
    except Exception as e:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print(message)


def post_to_groups(driver, groups_tlv, posts_tlv):
    j = 0
    while j < len(posts_tlv):
        for i in range(len(groups_tlv)):
            driver.get(groups_tlv[i])
            print("group: ", groups_tlv[i])
            try:
                upload_img_for_post(driver, posts_tlv[j].img)
                # time.sleep(1)

                write_post_text(driver, posts_tlv[j].text)
                wait(driver, "//div[@aria-label=\"Remove post attachment\"]")
                time.sleep(2)
                driver.find_element_by_xpath("//div[@aria-label=\"Post\"]").click()
                time.sleep(5)
                # ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                # time.sleep(3)

            except NoSuchElementException:
                print("No such element exception")
                b = driver.find_element_by_xpath("//form[@method=\"POST\"]//div[@aria-label=\"Got It\"]")
                if b:
                    b.click()
                    print("after clicking got it")
                    write_post_text(driver, posts_tlv[j].text)
                    time.sleep(3)
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(3)
            finally:
                print("finally")
                if i == len(groups_tlv)-1:
                    j = j+1


def write_post_text(driver, text):
    # wait(driver, "//form[@method=\"POST\"]//div[@aria-label=\"Got It\"")
    wait(driver, "//form[@method=\"POST\"]//div[@role=\"presentation\"]//div[@role=\"textbox\"]")
    driver.find_element_by_xpath(
        "//form[@method=\"POST\"]//div[@role=\"presentation\"]//div[@role=\"textbox\"]"
    ).send_keys(text)
    # driver.find_element_by_xpath("//form[@method=\"POST\"]//div[@role=\"presentation\"]//span") \
    #     .send_keys(posts_tlv[j].text)


def upload_img_for_post(driver, img):
    wait(driver, "//div[@data-pagelet=\"GroupInlineComposer\"]//input")
    driver.find_element_by_xpath("//div[@data-pagelet=\"GroupInlineComposer\"]//input") \
        .send_keys(img)
    print("file name: ", img)


def post():
    user, pwd = get_credentials_from_file()

    options = define_chrome_options()
    driver = webdriver.Chrome("../chromedriver.exe", options=options)

    with driver:
        driver.maximize_window()
        driver.get("http://www.facebook.com")
        # time.sleep(3)

        login(driver, pwd, user)
        # groups_tlv = read_groups_from_file(tlv_groups_file)
        groups_jrs = read_groups_from_file(jrs_groups_file)
        general_groups = read_groups_from_file(general_groups_file)

        # groups_tlv.extend(general_groups)
        # print("tlv groups = \\n", groups_tlv)
        groups_jrs.extend(general_groups)
        print("jrs groups = \\n", groups_jrs)

        posts_tlv = posts_json("../current_post")
        post_to_groups(driver, groups_jrs, posts_tlv)

        # posts_jrs = posts_json(jrs_posts_json_file)
        # post_to_groups(driver, groups_jrs, posts_jrs)
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
    # el = WebDriverWait(driver, 10).until(lambda d: d.find_element_by_id("email"))

    driver.find_element_by_id("email").send_keys(user)
    driver.find_element_by_id("pass").send_keys(pwd)
    driver.find_element_by_name("login").click()

    time.sleep(10)


def post_decoder(obj):
    return Post(obj['text'], obj['path'])


def posts_json(filename):
    with open(filename, "r", encoding="utf8") as file:
        post_obj = json.load(file, object_hook=post_decoder)
        return post_obj


if __name__ == "__main__":
    post()