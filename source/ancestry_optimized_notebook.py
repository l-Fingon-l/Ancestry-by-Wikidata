import requests
import re
from collections import deque
import time
from urllib.parse import unquote

amount = 0
tablichka = dict()
found = None


#########################
#   helper functions
#########################


def find_name(qid, text):
    if 'labels' in text:
        labels = text['labels']

        if 'en' in labels:
            name = labels['en']['value']
        elif 'fr' in labels:
            name = labels['fr']['value']
        elif 'de' in labels:
            name = labels['de']['value']
        else:
            name = list(labels.values())[0]['value']
    else:
        name = qid

    return name


def get_qid(article):  # a logic for obtaining the QID by varying input (article name / qid / url)
    article = unquote(article)  # safely convert the utf8 of browser url
    if article[0] == 'Q':
        qid = article
    else:
        split = article.split('.', 2)
        if len(split) == 3 and split[1] == 'wikipedia':
            article_name = article.rsplit('/', 1)[1]
            wiki = split[0]
            if split[0][:8] != 'https://':
                wiki = 'https://' + split[0]
        else:
            article_name = article
            wiki = 'https://en'
        url = wiki + '.wikipedia.org/w/api.php'
        params = {
            'action': 'query',
            'prop': 'pageprops',
            'ppprop': 'wikibase_item',
            'redirects': 1,
            'titles': article_name,
            'format': 'json'
        }
        res = requests.get(url, params=params)
        text = res.json()
        [key, page] = list(text['query']['pages'].items())[0]
        if key == '-1':  # the entry is missing from wikidata
            qid = '-1'
        else:
            qid = page['pageprops']['wikibase_item']

    return qid


def request(qid, props):
    url = 'https://www.wikidata.org/w/api.php'
    params = {
        'action': 'wbgetentities',
        'ids': qid,
        'props': props,
        'format': 'json'
    }
    res = requests.get(url, params=params)

    return res.json()


def get_year(claim, text):
    year = None
    if claim in text:
        if 'datavalue' in text[claim][0]['mainsnak']:
            date = text[claim][0]['mainsnak']['datavalue']['value']['time']
            year = int(str(date).split('-', 1)[0][1:])

    return year


def search_description(description):
    result = {'birth_year': None, 'death_year': None}
    for lang in description.values():
        m = re.fullmatch(r"(?:(?:.*\W)?([1-9]?\d{3})(?:\W.*)?)?-(?:(?:.*\W)?([1-9]?\d{3})(?:\W.*)?)?|(?:.*\W)?(["
                         r"1-9]?\d{3})(?:\W.*)?", lang['value'], flags=re.MULTILINE)
        if m:
            if m[3]:
                result['birth_year'] = int(m[3])
                continue
            if m[1]:
                result['birth_year'] = int(m[1])
            if m[2]:
                result['death_year'] = int(m[2])
                if result['birth_year'] is not None and result['death_year'] is not None:
                    break

    return result


#########################
#       interface
#########################


def ancestry_optimized(article1, article2):
    global amount, tablichka, found  # init
    amount = 0
    tablichka = dict()
    found = None

    started_at = time.monotonic()

    qid = get_qid(article1)
    if qid == '-1':
        print(f'Fix a descendant link: "{article1}" , please!')
        return

    sqid = get_qid(article2)
    if sqid == '-1':
        print(f'Fix an ancestor link: "{article2}", please!')
        return

    text = request(sqid, 'labels|claims')
    year = get_year('P569', text['entities'][sqid]['claims'])
    search_name = find_name(sqid, text['entities'][sqid])

    text = request(qid, 'labels')
    name = find_name(qid, text['entities'][qid])

    print('\n    ' + name + '      <=>      ' + search_name)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')

    search_optimized(qid, sqid, year, name, search_name)
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(str(amount) + ' royals were examined.')

    time_spent = time.monotonic() - started_at
    print(str(round(time_spent, 2)) + 's spent at total.')

    return time_spent


#########################
#     main functions
#########################


def search_optimized(qid, sqid, year, name, search_name):
    global found
    tablichka[qid] = [None, None]
    buffer = deque([qid])

    while len(buffer) != 0:  # BFS
        if found is not None:
            break
        started_at = time.monotonic()
        # compose the request QID list
        request_list = deque()
        while len(request_list) < 50 and len(buffer) != 0:  # check whether the buffer is exhausted
            i = buffer.popleft()  # pop the first key in buffer (aka queue)
            request_list.append(i)  # and add to request list (queue)

        # run the actual query for a whole list of QIDs (up to 50 at once)
        ids = '|'.join(request_list)
        texts = request(ids, 'labels|claims|descriptions')['entities']

        for qid in texts:
            text = texts[qid]
            if found is not None:
                break

            global amount
            amount += 1

            # in this section we're gonna found out if the person is a valid descendant by his lifetime dates
            if year is not None:
                birth_age = 5  # damn it en.wikipedia.org/wiki/Lina_Medina
                lifetime = 95  # if one of the parents is 100 years older than search then drop the other

                # date of birth & date of death check
                birth_year = get_year('P569', text['claims'])
                death_year = get_year('P570', text['claims'])

                # first try (if it works then we wouldn't have to compute the regexp)
                if (birth_year is not None and (birth_year + lifetime < year or birth_year < year + birth_age)) \
                        or (death_year is not None and death_year < year + birth_age):  # not a descendant for sure
                    continue

                # if not found yet, search by description
                if birth_year is None or death_year is None:
                    years_found = search_description(text['descriptions'])
                    if birth_year is None:
                        birth_year = years_found['birth_year']
                        if birth_year is not None:
                            if birth_year + lifetime < year or birth_year < year + birth_age:  # not a descendant for sure
                                continue
                    if death_year is None:
                        death_year = years_found['death_year']
                        if death_year is not None:
                            if death_year < year + birth_age:  # a spouse is not a descendant for sure as well
                                continue

            # now we know this person is a valid descendant so we continue to search up the tree

            # add the name to database
            temp_name = find_name(qid, text)
            tablichka[qid][1] = temp_name

            if 'P22' in text['claims']:  # father
                father = text['claims']['P22'][0]['mainsnak']['datavalue']['value']['id']
                if father in tablichka:
                    continue
                elif father == sqid:
                    found = father
                    tablichka[father] = [qid, None]
                    break
                else:
                    tablichka[father] = [qid, None]
                    buffer.append(father)

            if 'P25' in text['claims']:  # mother
                mother = text['claims']['P25'][0]['mainsnak']['datavalue']['value']['id']
                if mother in tablichka:
                    continue
                elif mother == sqid:
                    found = mother
                    tablichka[mother] = [qid, None]
                    break
                else:
                    tablichka[mother] = [qid, None]
                    buffer.append(mother)

        time_spent = str(round(time.monotonic() - started_at, 2))
        print(time_spent + 's spent for this query. ' + str(len(request_list)) + ' QIDs requested at once.')

    if found is not None:
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('\n    ' + search_name)
        found = tablichka[found][0]
        while found is not None:
            temp_name = tablichka[found][1]
            print('              ||          ')
            print('              \\/         ')
            print('    ' + temp_name)
            found = tablichka[found][0]
    else:
        print('\n' + name + ' is not a descendant of ' + search_name)
