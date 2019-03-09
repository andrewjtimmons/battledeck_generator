import json
import re
import requests

import sys



def main():

    # get the serach term
    terms = sys.argv[1:]
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
            print 'oh noes two failures try again'
            continue

        page = r.text
        #remove all breaks for regex idk.
        page = page.replace('\r', '').replace('\n', '')
        search_pages.append(page) #todo can i skip this step?

        search_result_decks[terms[index]] = []

        search_result_text_blobs_that_hopefully_have_the_link = re.findall(r"(?<=title title-link antialiased j-slideshow-title).+?(?=\>)", page)
        for garbage_text in search_result_text_blobs_that_hopefully_have_the_link:

            # TODO maybe handle no match
            search_result_decks[terms[index]].append("https://www.slideshare.net/" + re.findall(r"(?<=href\=\").+?(?=\")", garbage_text)[0])

        # print search_result_text_blobs_that_hopefully_have_the_link
        # print len(search_result_text_blobs_that_hopefully_have_the_link)


    print search_result_decks
    # print search_urls
    # search_url = 'https://www.slideshare.net/search/slideshow?searchfrom=header&q='+term
    # search_page = requests.get(search_url)
    # print search_page.text



if __name__ == '__main__':
    main()