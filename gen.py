# use:
# python gen.py 12 "finance" "machine learning" "veternarian" "sales" "marketing" "death" "cyber security" "manufacturing"
# the first arg is how many slides you want (it also grabs the start and end slide of a presentation so you have that) and the rest are search terms

import json
import re
import requests
from random import randint
import sys
import os
import time
import urllib

def main():

    num_slides = int(sys.argv[1])
    terms = sys.argv[2:]

    search_urls = []
    search_result_decks = {}

    for index in range(0,len(terms)):
        terms[index] = terms[index].replace(" ", "+")
        search_urls.append('https://www.slideshare.net/search/slideshow?searchfrom=header&q='+terms[index])

        # this could be more robust but shurg
        r = requests.get(search_urls[index])
        if r.status_code != 200:
            #try again if it fails give up lol
            r = requests.get(search_urls[index])
        if r.status_code != 200:
            print 'oh noes two search failures moving on'
            continue

        print 'extracting presentations for ' + terms[index]
        page = r.text
        #remove all breaks for regex so it can find our elements. .json() didnt work oh well.
        page = page.replace('\r', '').replace('\n', '')

        search_result_decks[terms[index]] = []
        search_result_text_blobs_that_hopefully_have_the_link = re.findall(r"(?<=title title-link antialiased j-slideshow-title).+?(?=\>)", page)
        if len(search_result_text_blobs_that_hopefully_have_the_link) >= 2:
            search_result_text_blobs_that_hopefully_have_the_link = search_result_text_blobs_that_hopefully_have_the_link[0:2]
        for garbage_text in search_result_text_blobs_that_hopefully_have_the_link:

            # TODO maybe handle no match
            deck_link = "https://www.slideshare.net/" + re.findall(r"(?<=href\=\").+?(?=\")", garbage_text)[0]
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
    # get the first slide.  TODO make this grab a random deck from the decks for the first and last slide instead of the same search term.
    slide_links.append(extract_slide_link_from_page(search_result_decks[terms[0]][0], 1))

    #extract random links
    for x in xrange(0, num_slides):
        random_term_index = randint(0, len(terms)-1)
        random_deck_index = randint(0, len(search_result_decks[terms[random_term_index]])-1)
        slide_links.append(extract_slide_link_from_page(search_result_decks[terms[random_term_index]][random_deck_index]))

    #get the last slide. TODO make this use the same deck as the first slide but random choice.
    slide_links.append(extract_slide_link_from_page(search_result_decks[terms[0]][0], -1))

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

    print 'done'

def extract_slide_link_from_page(page, page_to_extract = None):

    if page_to_extract == None:
        try:
            num_pages = int(re.findall(r"(?<=j-total-slides\"\>).+?(?=\<)", page)[0])
            if num_pages > 5:
                # if we have more than a couple slides lets aim for the middle so we dont get multiple conclusion slides
                min_page = num_pages/10
                max_page = num_pages-min_page
                page_to_extract = randint(min_page, max_page)
            else:
                page_to_extract = randint(0, int(num_pages))
        except IndexError:
            return None

    if page_to_extract == -1:
        try:
            num_pages = re.findall(r"(?<=j-total-slides\"\>).+?(?=\<)", page)[0]
            page_to_extract = num_pages
        except IndexError:
            return None
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