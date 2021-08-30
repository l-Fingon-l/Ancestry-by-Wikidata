import requests
import re

amount = 0
tablichka = set()


def search(qid, depth, sqid, year):
    if qid in tablichka:
        return 'checked already'
    else:
        tablichka.add(qid)

    depth += 1
    url = 'https://www.wikidata.org/wiki/Special:EntityData/' + qid + '.json'
    res = requests.get(url)
    text = res.json()

    if 'en' in text['entities'][qid]['labels']:
        name = text['entities'][qid]['labels']['en']['value']
    else:
        name = qid
    space = '|   ' * depth
    print(space + '=>' + name)

    global amount
    amount += 1

    if qid == sqid:
        if 'en' in text['entities'][sqid]['labels']:
            search_name = text['entities'][sqid]['labels']['en']['value']
        else:
            search_name = sqid
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('\n    ' + search_name)
        return 'found'

    # in this section we're gonna found out if the person is a valid descendant by his lifetime dates
    birth_age = 5  # damn it https://en.wikipedia.org/wiki/Lina_Medina
    lifetime = 95  # if one of the parents is 100 years older than search then drop the other
    birth_year = None
    death_year = None

    # date of birth check
    if 'P569' in text['entities'][qid]['claims']:
        if 'datavalue' in text['entities'][qid]['claims']['P569'][0]['mainsnak']:
            birth_date = text['entities'][qid]['claims']['P569'][0]['mainsnak']['datavalue']['value']['time']
            birth_year = int(str(birth_date).split('-', 1)[0][1:])

    # date of death check
    if 'P570' in text['entities'][qid]['claims']:
        if 'datavalue' in text['entities'][qid]['claims']['P570'][0]['mainsnak']:
            death_date = text['entities'][qid]['claims']['P570'][0]['mainsnak']['datavalue']['value']['time']
            death_year = int(str(death_date).split('-', 1)[0][1:])

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


def ancestry(qid, sqid):
    url = 'https://www.wikidata.org/wiki/Special:EntityData/' + sqid + '.json'
    res = requests.get(url)
    text = res.json()

    if 'P569' not in text['entities'][sqid]['claims']:
        year = 0
    else:
        date = text['entities'][sqid]['claims']['P569'][0]['mainsnak']['datavalue']['value']['time']
        year = int(str(date).split('-', 1)[0][1:])

    if 'en' in text['entities'][sqid]['labels']:
        search_name = text['entities'][sqid]['labels']['en']['value']
    else:
        search_name = sqid

    url = 'https://www.wikidata.org/wiki/Special:EntityData/' + qid + '.json'
    res = requests.get(url)
    text = res.json()

    if 'en' in text['entities'][qid]['labels']:
        name = text['entities'][qid]['labels']['en']['value']
    else:
        name = qid

    print('\n    ' + name + '      <=>      ' + search_name)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
    if not search(qid, -1, sqid, year) == 'found':
        print('\n' + name + ' is not a descendant of ' + search_name)
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(str(amount) + ' royals were examined.')
