"""The Crawler Module, One of Three Main Components for
 the IRC Post-Processing Software, It Can Download Different IRC That are
 Logged in Different Structures"""

__author__ = 'Ahmed Abouzeid'

import os
import sys
import shutil
import argparse
import logging
import requests
from bs4 import BeautifulSoup

sys.setrecursionlimit(10000)
logging.basicConfig(filename='crawler.log', filemode='w', level=logging.INFO)

###################################################################################################
# The Crawler mission is to be configured by initialising it with a list of urls to go through    #
# and loop inside all the links inside the main url and repeat its task according to the          #
# configuration by the other parameters during the initialisation, the initialised configuration  #
# is given as a set of parameters to the initialised Crawler object. List of parameters           #
# which their values should be determined according to how logs are located in the site and how   #
# the Crawler should look and download the logs. there is urls                                    #
# list parameter which is given as a text file with a url in a separated line The parameters are  #
# as below:                                                                                       #
# 1- crawl : if yes, the software will run the crawling task                                      #
# 2- search : if yes, the software will run only a search for all sub-links inside a given link   #
# 3- link_to_search : a given link must be passed as an argument in case of using -search param   #
# 4- urls_file : the path of the file with list of websites or root urls that the spider will     #
# iterate recursively through each                                                                #
# 5- file_spider: indicates if the spider should look only for files and download them. That      #
# parameter needs the target_format parameter                                                     #
# 6- The target_format: indicates which file formats the spider is to fetch its text when it is   #
# configured to be a file_spider                                                                  #
# 7- ignored_links: indicates the list of links to avoid processing and recursively loop through  #
# them.                                                                                           #
# 8- allow_clean_url: indicates if the Crawler should call the cleanUrl function which solve url  #
# formats occurred sometimes in some IRC sites.                                                   #
# while Crawling. Can be useful in debugging also.                                                #
# 9- time_out: by default = 60 seconds which is the maximum time allowed to try download a log    #
# or download contents of a log page, if time exceeds that parameter value, the Crawler proceeds  #
# with next iteration ignoring the current problematic link.                                      #
# 10- work_path:to configure where to download the logs. By default it will be on the local folder#
# 11- max_recursion_depth: indicates how many iteration levels allowed to go, that is to avoid    #
# iterating on links that are not part of the IRC site but they are links mentioned in the        #
# conversations of the downloaded logs, which is not part of the software target. So simply you   #
# loop till you find a log and do no more iteration inside any more links in the fetched contents,#
# so, you pass the maximum number of iterations or sub-links starting from the root url, so the   #
# IRC stops there when it reaches that maximum. If = 0, it means no depth maximum is configured   #
# 12- one_bite: indicates if the Crawler should only downloads the page of the given root url     #
# without any further recursions inside links in the page contents                                #
# 13- white_list_path : in case of a file crawler, only file names in that passed path will be    #
# downloaded                                                                                      #
###################################################################################################


class Crawler(object):
    """defines the crawler class"""

    def __init__(self, urls_file_, file_spider_='no', target_format_='', ignored_links_file_='',
                 allow_clean_url_='no', time_out_=60, work_path_='./',
                 max_recursion_depth_=0, one_bite_='no', white_list_path_=""):
        """This is the initializer method, defines the default values and passed argument values"""
        self.__urls = Crawler.__read_file(urls_file_)
        self.__file_spider = file_spider_
        self.__target_format = target_format_
        self.__allow_clean_url = allow_clean_url_
        self.__one_bite = one_bite_
        self.__white_list_path = white_list_path_
        self.__white_list = []

        # loads white list in beginning in case an argument was passed for it
        if self.__file_spider == 'yes' and self.__white_list_path != '':
            self.__white_list = Crawler.__read_white_list(self.__white_list_path)

        # link titles that should be ignored during recursions
        self.__ignored_links = Crawler.__read_file(ignored_links_file_)

        self.__time_out = time_out_
        self.__work_path = os.path.join(work_path_.rstrip('/')+'/', 'DATA')
        self.__recursion_max_depth = max_recursion_depth_
        self.__extensions = ['txt', 'html', 'csv', 'tsv', 'tar', 'raw']

        logging.info('''Crawler Has been Initialized With The Below Configurations:
-------------------------------------------------------------------
-urls: %s
-file_spider: %s
-target_format: %s
-ignored_links_file: %s
-allow_clean_url: %s
-time_out: %s
-work_path: %s
-max_recursion_depth: %s
-one_bite: %s
-white_list_path: %s
''', self.__urls, self.__file_spider, self.__target_format, self.__ignored_links,
                     self.__allow_clean_url, self.__time_out, self.__work_path,
                     self.__recursion_max_depth, self.__one_bite, self.__white_list_path)

    def crawl(self):
        """main method that iterates through all passed urls from the urls.txt file
        , it invokes start_recursion which iterates through sub-links inside urls.txt urls"""
        if os.path.exists(self.__work_path):
            shutil.rmtree(self.__work_path)
            print '\nOld Data Was Found And Removed.\n'

        initial_first_run = True
        initial_recursion_depth = 0
        initial_prev_link_size = 0
        for url in self.__urls:
            self.__start_recursion(url, initial_first_run,
                                   initial_recursion_depth, initial_prev_link_size)

        Crawler.mission_report(self.__work_path)

    def __start_recursion(self, url, first_run_p, recursion_depth_p, prev_link_size_p):
        """iterates through all passed urls frm the urls.txt file"""
        links_titles = []
        print 'Crawling Link: {}'.format(url)
        # storing current link length to count recursion depth.
        recursion_settings = Crawler.__count_recursion_depth(len(str(url).rstrip('/').split('/'))
                                                             , recursion_depth_p,
                                                             prev_link_size_p,
                                                             first_run_p)

        try:
            source_code = requests.get(url, timeout=self.__time_out)
            plain_text = source_code.text
        except requests.RequestException as excep:
            logging.error('Error In URL %s, Reason: %s', url, excep.message)

        # if true: means that only one bite crawling was asked (no recursion)
        if Crawler.__handle_one_bite(self.__one_bite, BeautifulSoup(plain_text),
                                     url, self.__work_path):
            return

        iteration_result = Crawler.__iterate_link(BeautifulSoup(plain_text).find_all('a')
                                                  , url, self.__ignored_links,
                                                  links_titles, self.__extensions)

        # empty original given root urls to fill them with the sub links for next recursion
        if self.__allow_clean_url == 'yes':
            links_titles = Crawler.__clean_url(links_titles)

        # in case the crawling found ftp folders (means there should be more iteration)
        sub_urls = Crawler.__setup_recursion(iteration_result[0], iteration_result[1])

        # downloads data and configure current crawling status like recursion settings
        crawling_status = Crawler.__fetch_data(self.__file_spider, links_titles,
                                               self.__white_list, self.__target_format,
                                               self.__time_out, self.__work_path,
                                               recursion_settings[0],
                                               self.__recursion_max_depth,
                                               recursion_settings[1], recursion_settings[2])

        if self.__recursion_max_depth != 0:
            # if true: stop iterating and start from next element of the previous
            # recursion urls
            if crawling_status[0] == self.__recursion_max_depth:
                return

        for url in sub_urls:
            self.__start_recursion(url, crawling_status[2], crawling_status[0], crawling_status[1])

    @staticmethod
    def mission_report(path):
        """report results"""
        if os.path.exists(path):
            print '\n-----------------------------------------------------------------------'
            print 'Crawler Has Finished Crawling. Please Check The Path "{}"' \
                  ' For The Downloaded IRC Logs.'.format(path)
            print '-----------------------------------------------------------------------\n'
        else:
            print '\nNOTHING TO REPORT!\n'

    @staticmethod
    def __handle_one_bite(one_bite, parsed_html, url, path):
        """in case of only the main page of a url is to be downloaded
         and no more recursion is required"""
        if one_bite == 'yes':
            print 'Downloading Contents Of Page {}'.format(url)
            log_bite = parsed_html
            try:
                Crawler.__write_file(path, url, log_bite)
            except IOError as excep:
                logging.error('Error In URL %s, Reason: %s', url, excep.message)
            return True
        return False

    @staticmethod
    def __fetch_data(file_spider, links_titles, white_list, target_format, time_out, path,
                     recursion_depth, recursion_max_depth, prev_link_size, first_run):
        """"invokes methods(check_target_link, count_recursion_depth and download_link_contents)
         and it responsible for the real downloading of data with configuring the current
          crawling status like how many recursion depth remains and so on"""
        if file_spider == 'yes':
            Crawler.__check_target_link(links_titles, white_list, target_format,
                                        time_out, path)
            return [recursion_depth, prev_link_size, first_run]

        else:
            url_size = len(str(links_titles[0]).rstrip('/').split('/'))
            recursion_settings = Crawler.__count_recursion_depth(url_size, recursion_depth,
                                                                 prev_link_size, first_run)
            recursion_depth = recursion_settings[0]
            prev_link_size = recursion_settings[1]
            first_run = recursion_settings[2]

            if recursion_depth > recursion_max_depth and recursion_depth != 0:
                return [recursion_depth, prev_link_size, first_run]
            else:
                Crawler.__download_link_contents(links_titles, time_out, path)
                return [recursion_depth, prev_link_size, first_run]

    @staticmethod
    def __setup_recursion(folder_found, links_titles):
        """prepare the new list of parent url sub-links to iterate through"""
        urls = []
        if folder_found:
            for element_x, _, element_z in links_titles:
                if element_z == 'folder':
                    # fill urls with sub-links to recursively call crawl function on them
                    urls.append(element_x)
        return urls

    @staticmethod
    def __check_target_link(links_titles_p, white_list, target_format, time_out, path):
        """check links if to download or they should be ignored if not in white_list.txt"""
        for link_item, _, _ in links_titles_p:
            if str(link_item).split("/")[-1] not in white_list and white_list:
                continue
            if str(link_item).endswith(target_format):
                try:
                    my_file = requests.get(link_item, timeout=time_out)
                except requests.RequestException as excep:
                    logging.error('Error In URL %s, Reason: %s', link_item, excep.message)
                try:
                    if my_file.encoding != 'utf-8':
                        Crawler.__write_file(path, link_item, str(my_file.content)
                                             .decode(my_file.encoding))
                    else:
                        Crawler.__write_file(path, link_item, my_file.content)
                except IOError as io_exp:
                    logging.error('Error In URL %s, Reason: %s', link_item, io_exp.message)
                except UnicodeDecodeError as unicod_exp:
                    logging.error('Error In URL %s, Reason: %s', link_item, unicod_exp.message)

    @staticmethod
    def __download_link_contents(links_titles_p, time_out_p, path_p):
        """download links contents"""
        for link_item, _, _ in links_titles_p:
            try:
                print 'Downloading Contents Of Page {}'.format(link_item)
                source_code = requests.get(link_item, timeout=time_out_p)
            except requests.RequestException as req_exp:
                logging.error('Error In URL %s, Reason: %s', link_item, req_exp.message)
            parsed_html = BeautifulSoup(source_code.text)
            text = parsed_html.getText()
            try:
                Crawler.__write_file(path_p, link_item, text)
            except IOError as io_exp:
                logging.error('Error In URL %s, Reason: %s', link_item, io_exp.message)

    @staticmethod
    def __is_file(extension_p, all_extensions_p):
        """checks a given extension if exists in the class predefined extensions
         so it will be recognized as a file"""
        return extension_p in all_extensions_p

    @staticmethod
    def __iterate_link(links_p, current_url, ignored_links, links_titles, extensions):
        """iterating inside each link found on a crawled url"""
        folder_found = False
        # iterating inside each link found on a crawled url
        for link_element in links_p:
            if (link_element.string not in ignored_links and
                    link_element.get('href') != '/') and\
                    link_element.string:
                if not current_url.endswith('/'):
                    # if the link is a file
                    if Crawler.__is_file(link_element.string.split('.')[-1], extensions):
                        links_titles.append(
                            (current_url + '/' + link_element.get('href').lstrip('/'),
                             link_element.string, 'file'))
                    else:
                        folder_found = True
                        links_titles.append(
                            (current_url + '/' + link_element.get('href').lstrip('/'),
                             link_element.string, 'folder'))
                else:
                    if Crawler.__is_file(link_element.string.split('.')[-1], extensions):
                        links_titles.append((current_url +
                                             link_element.get('href').lstrip('/'),
                                             link_element.string, 'file'))
                    else:
                        folder_found = True
                        links_titles.append((current_url +
                                             link_element.get('href').lstrip('/'),
                                             link_element.string, 'folder'))

        return [folder_found, links_titles]

    @staticmethod
    def __write_file(path, link_name, context):
        """write link context to a file"""
        file_name = ''
        for strng in ['/', 'http:']:
            if not file_name:
                file_name = link_name.replace(strng, '')
            else:
                file_name = file_name.replace(strng, '')

        full_path = os.path.join(path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        open(full_path + '/' + file_name, 'w').write(context.encode('utf-8'))
        logging.info('File: %s Created', full_path + '/' + file_name)

    @staticmethod
    def find_link_title(link_para):
        """this function is used separately not invoked in the crawl function.
        it is to give information about links
        in the url to be crawled to know which links to ignore"""
        urls = []
        source_code = requests.get(link_para)
        plain_text = source_code.text
        parsed_html = BeautifulSoup(plain_text)
        for sub_link in parsed_html.find_all('a'):
            urls.append(sub_link.string)
        print urls

    @staticmethod
    def __clean_url(links_titles):
        """this function is called when we need to remove some words
   from url in order to make it callable from internet. EX.https://irclog.perlgeek.de/perl6/ is OK
   but https://irclog.perlgeek.de/perl6/perl6 is not a correct one.
   Sometimes such duplicates can be caused because of how some IRC sites source code is written
   and how the software is processing the."""
        clean_urls = []
        for url, title, flag in links_titles:
            duplicates_words = []
            unique_words = []
            for word in str(url).rstrip('/').split('/'):
                if word not in unique_words:
                    unique_words.append(word)
                else:
                    if word not in duplicates_words:
                        duplicates_words.append(word)
                        url = str(url).replace(word+'/', '', 1)
            clean_urls.append((url, title, flag))
        return clean_urls

    @staticmethod
    def __count_recursion_depth(link_size, recursion_depth, prev_link_size, first_run):
        """keep tracking the recursion depth to determine when to stop iterating into a link"""
        if not first_run:
            if link_size == prev_link_size + 1:
                recursion_depth += 1
                prev_link_size = link_size
            for i in range(1, 20):
                if link_size == prev_link_size - i:
                    recursion_depth -= i
                    prev_link_size = link_size
        else:
            prev_link_size = link_size
            first_run = False

        return [recursion_depth, prev_link_size, first_run]

    @staticmethod
    def __read_file(file_path):
        """read urls from the urls file"""
        assert os.path.exists(file_path), 'FILE "{}" NOT FOUND,' \
                                          ' PLEASE GIVE THE CORRECT FILE PATH.'.format(file_path)
        url_list = []
        if file_path == '':
            return url_list
        else:
            my_file = open(file_path, 'r')
            for line in my_file.readlines():
                url_list.append(''.join(line.split('\n')))
            return url_list

    @staticmethod
    def __read_white_list(file_path):
        """read file names from the white_list_path to decide what to crawl"""
        assert os.path.exists(file_path), 'FILE "{}" NOT FOUND,' \
                                          ' PLEASE GIVE THE CORRECT FILE PATH'.format(file_path)
        white_list = []
        my_file = open(file_path, 'r')
        for line in my_file.readlines():
            white_list.append(''.join(line.split('\n')))
        return white_list

# running from command line related part
if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('-crawl', help='this command in case of Crawling tasks. '
                                       '(yes) indicates to crawl, default value is no',
                        nargs='?', const='no', type=str, default='no')

    PARSER.add_argument('-search', help="""(yes) indicates searching
             for sub-links titles  inside a link to be crawled (useful to
              detect which sub-links to ignore), default value is no.
               You must pass the -link_to_search argument
               with that one""", nargs='?', const='no', type=str, default='no')

    PARSER.add_argument('-urls_file', help='path to file contains url(s) to be crawled. '
                                           'that argument is mandatory'
                                           ' in case of using "-crawl"',
                        type=str)

    PARSER.add_argument('-file_spider', help="""(yes)indicates if spider should
             look only for files and download them. that parameter needs the target_format
              parameter, default value is no""", nargs='?', const='no', type=str, default='no')

    PARSER.add_argument('-target_format', help="""indicates which file
             formats the spider to fetch its text when it is configured to be a file_spider,
              default value is empty string. that argument is mandatory in case of using
               '-crawl'""", type=str, nargs='?', const='', default='')

    PARSER.add_argument('-ignored_links_file', help='indicates a path to a file with list of'
                                                    ' links to avoid processing and recursively'
                                                    ' loop through them, default value is'
                                                    ' empty string', type=str, nargs='?',
                        const='', default='')

    PARSER.add_argument('-allow_clean_url', help='(yes)indicates if the Crawler'
                                                 ' should call the cleanUrl function'
                                                 ' which solve url format'
                                                 ' if needed in some IRC sites,'
                                                 ' default value is no', nargs='?',
                        const='no', type=str, default='no')

    PARSER.add_argument('-time_out', help='by default = 60 seconds which is maximum time'
                                          ' allowed to try download a log or download'
                                          ' contents of a log page,if time exceeds that'
                                          ' parameter value, Crawler proceeds with next'
                                          ' iteration ignoring current problematic link'
                        , type=int, nargs='?', const=60, default=60)

    PARSER.add_argument('-work_path', help='to configure where to download the logs.'
                                           ' by default it will be on the local folder',
                        nargs='?', const='./', type=str, default='./')

    PARSER.add_argument('-max_recursion_depth', help='indicates how many iteration allowed'
                                                     ' to go, that is to avoid iterating on'
                                                     ' links that are not part of the IRC '
                                                     'site but they are links  mentioned in'
                                                     ' the conversations, by default is 0.'
                                                     ' that argument is '
                                                     'mandatory when using -crawl',
                        type=int, nargs='?', const=0, default=0)

    PARSER.add_argument('-one_bite', help='(yes)indicates if Crawler should only downloads page'
                                          ' of given root url without any further'
                                          ' recursions inside links in'
                                          ' the page contents, by default it is no', nargs='?',
                        const='no', type=str, default='no')

    PARSER.add_argument('-white_list_path', help='in case of file crawler, only file names'
                                                 ' in that passed file path will be'
                                                 ' downloaded, by default it is empty string',
                        type=str, nargs='?', const='', default='')

    PARSER.add_argument('-link_to_search', help='pass here a link to report its sub-links,'
                                                ' useful before running crawling tasks'
                                                ' to see first which sub-links to'
                                                ' ignore. that argument is mandatory with'
                                                ' -search command', type=str)

    ARGM = PARSER.parse_args()

    if ARGM.crawl.lower() == 'yes':

        assert ARGM.search.lower() == 'no', 'YOU CANNOT SPECIFY -search ARGUMENT WHILE' \
                                            ' USING -Crawl. RUN "Crawl.py -h" FOR HELP'
        assert ARGM.urls_file, 'ARGUMENT "-urls_file" IS' \
                               ' REQUIRED WHEN USING "-crawl".'

        CRAWLER = Crawler(urls_file_=ARGM.urls_file,
                          file_spider_=ARGM.file_spider.lower(),
                          target_format_=ARGM.target_format,
                          ignored_links_file_=ARGM.ignored_links_file,
                          allow_clean_url_=ARGM.allow_clean_url.lower(),
                          time_out_=ARGM.time_out,
                          work_path_=ARGM.work_path,
                          max_recursion_depth_=ARGM.max_recursion_depth,
                          one_bite_=ARGM.one_bite.lower(),
                          white_list_path_=ARGM.white_list_path)
        CRAWLER.crawl()

    elif ARGM.search.lower() == 'yes' and ARGM.link_to_search is not None:
        Crawler.find_link_title(ARGM.link_to_search)
    elif ARGM.search.lower() == 'yes' and ARGM.link_to_search is None:
        print 'YOU HAVE TO SPECIFY "-link_to_search" ARGUMENT WITH "-search" ARGUMENT.'
    else:
        print 'YOU HAVE TO SPECIFY A TASK, EITHER CRAWLING or SEARCH.' \
               ' RUN "Crawl.py -h" FOR HELP'
