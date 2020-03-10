# what next?
import googletrans
from googletrans import Translator
import sys
from nltk.tokenize import sent_tokenize
from selenium import webdriver
from time import sleep
from lxml.html import document_fromstring
from lxml import html
import codecs
from bs4 import BeautifulSoup
import re
import regex
from boilerpy3 import extractors


def read_file(file_name):
    with codecs.open(file_name,'r', "utf-8" ) as inp:
        read_file = inp.read()
    inp.close()
    return read_file

def login_in_fb(usr, pwd):
    driver.get("https://m.facebook.com/login.php?refsrc=https%3A%2F%2Fm.facebook.com%2F&refid=8")
    sleep(3)

    username_box = driver.find_element_by_id("m_login_email")
    username_box.send_keys(usr)
    sleep(3)

    password_box = driver.find_element_by_name('pass')
    password_box.send_keys(pwd)
    sleep(3)
    login_box = driver.find_element_by_name('login')
    login_box.click()
    sleep(5)

def find_img_alt_text(soup_tree):

    list_alt = []
    soup_tree = soup_tree.find("div", {"class": "_5pcr userContentWrapper"})

    for match in soup_tree("form", {"class": "commentable_item"}):
        match.decompose()

    alt_text = soup_tree.find_all("img")

    if alt_text:
        for x_alt_text in alt_text:
            find_alt_text = re.search("\w+", x_alt_text["alt"])
            if find_alt_text:
                what = x_alt_text["alt"]
                content = detect_lang_and_sent_to_translate(what)
                list_alt.append(content)
    if list_alt:
        img_description = '<p lang="rus">' + "Описаниие изображения:" + '</p>' + "\n".join(list_alt)
    else:
        img_description = ""
    return img_description

def chek_for_new_post(mobile_link):
    driver.get(mobile_link)
    sleep(5)

    html_source = driver.page_source
    sleep(5)
    
    soup = BeautifulSoup(html_source, 'html.parser')
    watch_els = []
    
    for a in soup.find_all('a', href=True, text='Full Story'):
        datax = a["href"]
        print(datax)
        print(str(a))
        datax = regex.search(r"(\d\d\d\d+)", datax)
        # datax = re.search(r"story_fbid.(\d+)", datax)
        post_id = int(datax.group(0))
        if post_id > last_post:
            watch_els.append(post_id)

        elif post_id <= last_post:
            return watch_els

    #pres see more and continue loop for check
    while watch_els[-1] > last_post:
        elem = driver.find_element_by_partial_link_text("See More Stories")
        elem.click()
        sleep(3)
        html_source = driver.page_source
        sleep(5)
        doc = html.fromstring(bytes(html_source, encoding='utf8'))
        a_xpath = doc.xpath("//a")
        for a in a_xpath:
            if a.text_content() == "Full Story":
                datax = a.get("href")
                datax = regex.search(r"(\d\d\d\d+)", datax)
                # datax = re.search(r"story_fbid.(\d+)", datax)
                post_id = int(datax.group(0))
                if post_id > last_post:
                    watch_els.append(post_id)
                elif post_id <= last_post:
                    return watch_els
                else:
                    return watch_els

def refresh_last_post_id():
    #scrabe post by link with commenst
    if watch_els:
        if int(watch_els[0]) > last_post:
            with codecs.open('last_post.txt','w', "utf-8" ) as out:
                out.write(str(watch_els[0]))
            out.close()

def translate_text(text_for_translate):
    translator = Translator()

    text_for_translate = text_for_translate.replace("\n", " ")
    text_for_translate = text_for_translate.replace("\r", " ")
    text_for_translate = text_for_translate.replace("  ", " ")
    text_for_translate = text_for_translate.replace("  ", " ")

    if int(sys.getsizeof(text_for_translate)) > 15000:
        text_one = sent_tokenize(text_for_translate)
        text_two = []
        while int(sys.getsizeof(' '.join(text_one))) > 15000:
            text_two[:0] = [text_one.pop()]

        for t in text_one, text_two:
            art_text = ' '.join(t)
            # translations = translator.translate(art_text, dest='ru', src=detect_text)
            translations = translator.translate(art_text, dest='ru')
            return translations.text

    else:
        # translations = translator.translate(text_for_translate, dest='ru', src=detect_text)
        translations = translator.translate(text_for_translate, dest='ru')
        return translations.text

def detect_lang_and_sent_to_translate(what):
    translator = Translator()
    dict_lang_code_change = {
        "ru" : "rus",
        "pl" : "pol"
        }
    rege = regex.compile('[^\.\?\!,\)\(;:\w\s]')
    # rege = regex.compile('[^\p{posix_punct}\w\s]')
    what = rege.sub('', what)
    
    # what = what_detect

    chek_what = re.search('\w\w\w\w', what)
    chek_for_detect = what

    if chek_what:
        if int(sys.getsizeof(what)) > 500:
            chek_for_detect = re.search('\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+', what)
            chek_for_detect = chek_for_detect.group()

        detect_text = translator.detect(chek_for_detect)
        detect_text = detect_text.lang
        # sleep(5)

        if detect_text == "ru" or detect_text == "uk" or detect_text == "pl":
            for item in dict_lang_code_change.keys():
                detect_text = re.sub(item, dict_lang_code_change[item], detect_text, re.S)
            taged_text = '<p lang="' + detect_text + '">' + what + '</p>' + '\r\n'
        else:
            what = translate_text(what)
            taged_text = '<p lang="' + 'rus' + '">' + what + '</p>' + '\r\n'

    else:
            taged_text = '<p>' + what + '</p>' + '\r\n'
    return taged_text

def expand_comments():
    while True:
        try:
            elem = driver.find_element_by_partial_link_text("replied")
            elem.click()
            sleep(3)
        except:
            break
    while True:
        try:
            elem = driver.find_element_by_partial_link_text("See More")
            elem.click()
            sleep(3)
        except:
            break

def chek_for_autor(where, name='Myroslava'):

        autor = where.find("div", {"class": "_5pcr userContentWrapper"})

        for match in autor("form", {"class": "commentable_item"}):
            match.decompose()
        for match in autor("span", {"class": "timestampContent"}):
            match.decompose()
        for match in autor("div", {"rel": "theater"}):
            match.decompose()
        for match in autor("div", {"class": "lfloat _ohe"}):
            match.decompose()
        for match in autor("button"):
            match.decompose()
        chek_autor = str(autor.get_text())
        if chek_autor.startswith(name, 0, 10) == True:
            return True
        else:
            return False

def get_article_text(data):
    soup_tree = BeautifulSoup(data, 'html.parser')
    chek_out_link = soup_tree.find("div", {"class": "_5pcr userContentWrapper"})
    for match in chek_out_link("form", {"class": "commentable_item"}):
        match.decompose()
    chek_out_link = chek_out_link.find("div", {"class": "lfloat _ohe"})
    if chek_out_link:
        chek_out_link = chek_out_link.find("a")["href"]
        if chek_out_link:
            find_video = re.search("youtube", chek_out_link)
            if not find_video:
                get_link = chek_out_link
                driver.get(get_link)
                sleep(5)
                article_html = driver.page_source


                extractor = extractors.ArticleExtractor()
                what = extractor.get_content(article_html)
                sleep(5)
                content = detect_lang_and_sent_to_translate(what)
                sleep(5)
                content = '<p lang="' + 'rus' + '">' + "Ссылка на материал: " + '</p> ' + content
                return content
    content = ""
    return content


def scrabe_fb_comments(data):
    soup_tree = BeautifulSoup(data, 'html.parser')
    comments = soup_tree.find_all("div", {"data-testid": "UFI2Comment/body"})

    if comments:
        com_list = []
        for coment in comments:
            coment = coment.get_text()
            who = re.match('\w+ +\w+', coment)
            what = re.sub('^\w+ +\w+', '', coment)
            
            what = detect_lang_and_sent_to_translate(what)
            coment = '<p lang="' + 'rus' + '">' + who.group() + '</p>' + what
            com_list.append(coment)
        comments = "\r\n" + '<p lang="rus">' + "Далее коментари:" + '</p>' + "\r\n" + "\n".join(com_list) + "\r\n"
    else:
        comments = ""
    return comments

def take_data_time_post(take_data_time_post_data):
    translat_month = {
        "10" : "октября",
        "11" : "ноября",
        "12" : "декабря",
        "1" : "января",
        "2" : "февраля",
        "3" : "Марта",
        "4" : "апреля",
        "5" : "мая",
        "6" : "июня",
        "7" : "июля",
        "8" : "августа",
        "9" : "сентября"
        }
    doc = document_fromstring(take_data_time_post_data)
    abbr_xpath = doc.xpath("//abbr[@title][@data-utime][@data-shorten][@class]")
    # abbr_xpath = doc.xpath("//abbr[@title]")
    time_post = abbr_xpath[0].get("title")
    time_post = re.search(r"(\d+)/(\d+)/(\d+), (\d+):\d+ (\w+)", time_post)
    day = time_post.group(2)
    month = str(time_post.group(1))
    if time_post.group(5) == "AM":
        evning = " дня "
    if time_post.group(5) == "PM":
        evning = " вечера "

    for item in translat_month.keys():
        change = "\b" + translat_month[item] + "\b"
        month = re.sub(item, change, month, re.S)
    time_post = "\r\n\r\n"+ '<p lang="rus">' + "Пост написано в " + str(time_post.group(4)) + evning + str(day) + " " + str(month) + " 20" + str(time_post.group(3)) + " года. " + '</p>'
    return time_post

def scrabe_text_of_post(data):
    soup_tree = BeautifulSoup(data, 'html.parser')
    titles = soup_tree.find("div", {"class": "mts"})
    if titles:
        titles = titles.find("div", {"data-testid": "post_message"})
        if titles:
            titles = '<p lang="' + 'rus' + '">' + "Перепост:" + '</p> '
        else:
            titles = None
    else:
        titles = None
    posts = soup_tree.find_all("div", {"data-testid": "post_message"})

    if posts:
        posts_list = []
        for post in posts:
            what = post.get_text()
            what =  re.sub("https://\S+", "", what)
            if what == "":
                post = ""
                continue
            post = detect_lang_and_sent_to_translate(what)

            posts_list.append(post)
        if titles:
            if len(posts_list) == 1:
                post = titles + "".join(posts_list) + "\r\n"
            elif len(posts_list) > 1:
                post = titles.join(posts_list) + "\r\n"
        else:
            post = "\r\n".join(posts_list) + "\r\n"
    else:
        post = ""
    return post

def scrabe_posts(link):
    posts_together = []
    print(str(watch_els))
    for x in watch_els:
        link_post = link + "/posts/" + str(x)
        driver.get(link_post)
        sleep(5)

        expand_comments()

        data = (driver.page_source)
        take_data_time_post_data = data
        soup_tree = (BeautifulSoup(data, 'html.parser'))
        chek_a = chek_for_autor(soup_tree, name_of_need_autor)

        if chek_a == True:
            pass
        else:
            continue

        post = scrabe_text_of_post(data)

        article_text = get_article_text(data)

        alt_text = (find_img_alt_text(soup_tree))

        chek_for_empty_post = re.search("\S", post)

        if not chek_for_empty_post:
            post = ""
        # if post == "":
        if post == "" and article_text == "" and alt_text == "":
            continue
        else:
            pass

        comments = scrabe_fb_comments(data)

        time_post = take_data_time_post(take_data_time_post_data)

        posts_together.append(time_post)

        posts_together.append(post)

        posts_together.append(alt_text)

        posts_together.append(article_text)

        posts_together.append(comments)

    return posts_together

def write_to_file(what, out_file_name = 'out.txt'):
    with codecs.open(out_file_name, 'w',"utf-8") as out:
        for element in what:
            out.write(element)
    out.close()


if __name__ == '__main__':
    # private = read_file("Private_data.txt")
    print("In your fb need  be english interface.")
    your_login_fb = str(input("type your login for fb:  \n"))
    your_password_to_fb = str(input("type your fb password: \n"))
    last_post = int(input("Type last seened POST ID. For example look to link of date time of post that you want stop searche: https://www.facebook.com/your_friends_page_id/posts/ID_OF_POST_THAT_YOU_NEED_TYPE: \n"))
    friend_fb_id = str(input("type your friends id. For example open web page of your friend: https://www.facebook.com/YOUR_FRIENDS_PAGE_ID_THAT_YOU_NEED_TYPE/: \n"))
    name_of_need_autor = str(input("type your friends first name in fb \n"))
    options = webdriver.FirefoxOptions()
    profile = webdriver.FirefoxProfile()
    
    # run browser inviseble
    # options.headless = True
    
    #witout notification
    options.set_preference("dom.push.enabled", False)
    
    #witout image
    profile.set_preference("permissions.default.image", 2)

    driver = webdriver.Firefox(firefox_options=options, firefox_profile=profile)
    
    link = "https://www.facebook.com/" + friend_fb_id
    mobile_link = "https://m.facebook.com/" + friend_fb_id

    login_in_fb(your_login_fb, your_password_to_fb)
    watch_els = chek_for_new_post(mobile_link)

    if watch_els:
        post_from_autor = scrabe_posts(link)
        refresh_last_post_id()
        if post_from_autor:
            write_to_file(post_from_autor)
            post_from_autor = read_file('out.txt')
            print ("+++++++Sended+++++++++")
        else:
            print ("-------------Not new posts---------------")
    else:
        print ("-------------Not new posts---------------")
    driver.quit()
    pres_enter = input("Pres Enter to exit")
