import requests
import re

amount = 0
tablichka = set()

#########################
#   helper functions
#########################


def find_name(qid, text):
    text = text['entities'][qid]
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
    if article[0] == 'Q':
        qid = article
    else:
        split = article.split('.', 2)
        if len(split) == 3 and split[1] == 'wikipedia':
            article_name = article.rsplit('/', 1)[1]
        else:
            article_name = article
        url = 'https://en.wikipedia.org/w/api.php'
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


def ancestry(article1, article2):
    qid = get_qid(article1)
    sqid = get_qid(article2)

    if not qid[0] == 'Q':
        print(f'Fix a descendant link: "{article1}" , please!')
        return
    if not sqid[0] == 'Q':
        print(f'Fix an ancestor link: "{article2}", please!')
        return

    text = request(sqid, 'labels|claims')
    year = get_year('P569', text['entities'][sqid]['claims'])
    search_name = find_name(sqid, text)

    text = request(qid, 'labels')
    name = find_name(qid, text)

    print('\n    ' + name + '      <=>      ' + search_name)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
    if not search(qid, -1, sqid, year) == 'found':
        print('\n' + name + ' is not a descendant of ' + search_name)
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(str(amount) + ' royals were examined.')


#########################
#     main function
#########################


def search(qid, depth, sqid, year):
    if qid in tablichka:
        return 'checked already'
    else:
        tablichka.add(qid)

    depth += 1
    text = request(qid, 'labels|claims|descriptions')

    # search name
    name = find_name(qid, text)
    space = '|   ' * depth
    print(space + '=>' + name)

    global amount
    amount += 1

    if qid == sqid:
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('\n    ' + name)
        return 'found'

    # in this section we're gonna found out if the person is a valid descendant by his lifetime dates
    if year is not None:
        birth_age = 5  # damn it en.wikipedia.org/wiki/Lina_Medina
        lifetime = 95  # if one of the parents is 100 years older than search then drop the other

        # date of birth check
        birth_year = get_year('P569', text['entities'][qid]['claims'])

        # date of death check
        death_year = get_year('P570', text['entities'][qid]['claims'])

        # first try (if it works then we wouldn't have to compute the regexp)
        if birth_year is not None:
            if birth_year + lifetime < year:  # a spouse is not a descendant for sure
                return 'return'
            elif birth_year < year + birth_age:  # not a descendant for sure
                return 'not a descendant'
        if death_year is not None:
            if death_year < year + birth_age:  # a spouse is not a descendant for sure as well
                return 'return'

        # if not found yet, search by description
        if birth_year is None or death_year is None:
            years_found = search_description(text['entities'][qid]['descriptions'])
            if birth_year is None:
                birth_year = years_found['birth_year']
                if birth_year is not None:
                    if birth_year + lifetime < year:  # a spouse is not a descendant for sure
                        return 'return'
                    elif birth_year < year + birth_age:  # not a descendant for sure
                        return 'not a descendant'
            if death_year is None:
                death_year = years_found['death_year']
                if death_year is not None:
                    if death_year < year + birth_age:  # a spouse is not a descendant for sure as well
                        return 'return'

    # now we know this person is a valid descendant so we continue to search up the tree
    if 'P22' in text['entities'][qid]['claims']:  # father
        father = text['entities'][qid]['claims']['P22'][0]['mainsnak']['datavalue']['value']['id']
        result = search(father, depth, sqid, year)
        if result == 'found':
            print('              ||          ')
            print('              \\/         ')
            print('    ' + name)
            return 'found'
        elif result == 'return':
            return 'not found'

    if 'P25' in text['entities'][qid]['claims']:  # mother
        mother = text['entities'][qid]['claims']['P25'][0]['mainsnak']['datavalue']['value']['id']
        result = search(mother, depth, sqid, year)
        if result == 'found':
            print('              ||          ')
            print('              \\/         ')
            print('    ' + name)
            return 'found'

    return 'not found'
