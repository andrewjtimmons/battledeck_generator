import json
import re
import requests
from random import randint
import sys
import os
import time
import urllib

def main():

    # get the serach term
    num_slides = int(sys.argv[1])
    terms = sys.argv[2:]
    print terms
    search_urls = []
    search_pages = []
    search_result_decks = {}
    for index in range(0,len(terms)):
        terms[index] = terms[index].replace(" ", "+")
        search_urls.append('https://www.slideshare.net/search/slideshow?searchfrom=header&q='+terms[index])

        r = requests.get(search_urls[index])
        if r.status_code != 200:
            #try again if it fails give up lol
            r = requests.get(search_urls[index])
        if r.status_code != 200:
            print 'oh noes two search failures moving on'
            continue

        page = r.text
        #remove all breaks for regex idk.
        page = page.replace('\r', '').replace('\n', '')
        search_pages.append(page) #todo can i skip this step?

        search_result_decks[terms[index]] = []
        search_result_text_blobs_that_hopefully_have_the_link = re.findall(r"(?<=title title-link antialiased j-slideshow-title).+?(?=\>)", page)
        if len(search_result_text_blobs_that_hopefully_have_the_link) >= 2:
            search_result_text_blobs_that_hopefully_have_the_link = search_result_text_blobs_that_hopefully_have_the_link[0:2]
        for garbage_text in search_result_text_blobs_that_hopefully_have_the_link:

            # TODO maybe handle no match
            deck_link = "https://www.slideshare.net/" + re.findall(r"(?<=href\=\").+?(?=\")", garbage_text)[0]
            print deck_link
            r = requests.get(deck_link)
            if r.status_code != 200:
                #try again if it fails give up lol
                r = requests.get(search_urls[index])
            if r.status_code != 200:
                print 'oh noes two getting the deck failures moving on'
                continue

            # duplicate this code as much as possible
            page = r.text
            page = page.replace('\r', '').replace('\n', '')
            # put the page with its siblings
            search_result_decks[terms[index]].append(page)

    slide_links = []
    #get the first slide
    slide_links.append(extract_slide_link_from_page(search_result_decks[terms[0]][0], 1))

    #extract random links
    for x in xrange(0, num_slides):
        random_term_index = randint(0, len(terms)-1)
        random_deck_index = randint(0, len(search_result_decks[terms[random_term_index]])-1)
        slide_links.append(extract_slide_link_from_page(search_result_decks[terms[random_term_index]][random_deck_index]))


    # Path to be created
    path = str(int(time.time()))

    os.mkdir(path, 0755);

    for index in range(0, len(slide_links)):
        print slide_links[index]
        try:
            urllib.urlretrieve(slide_links[index], path + "/" + str(index) + ".jpg")
        except:
            #we must never fail
            continue

    print slide_links


def extract_slide_link_from_page(page, page_to_extract = None):

    if page_to_extract == None:
        try:
            num_pages = re.findall(r"(?<=j-total-slides\"\>).+?(?=\<)", page)[0]
        except IndexError:
            return None
        page_to_extract = randint(0, int(num_pages))

    try:
        bad_pattern = r"(?<=data-index=\"{0}\")".format(page_to_extract) + r".+?(?=section)"
        slide_blob = re.findall(bad_pattern, page)[0]
    except IndexError:
        return None

    try:
        anti_pattern = r"(?<=data-full\=\").+?(?=\")"
        lol_its_my_link = re.findall(anti_pattern, slide_blob)[0]
    except IndexError:
        return None

    return lol_its_my_link


if __name__ == '__main__':
    main()