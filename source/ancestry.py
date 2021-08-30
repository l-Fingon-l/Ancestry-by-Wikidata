import requests

amount = 0
tablichka = set()


def search(qid, depth, sqid, year):
    if qid in tablichka:
        return False
    tablichka.add(qid)

    global amount
    amount += 1

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

    # date of birth check
    if 'P569' not in text['entities'][qid]['claims']:
        birth_year = 999999
    elif 'datavalue' not in text['entities'][qid]['claims']['P569'][0]['mainsnak']:
        birth_year = 999999
    else:
        birth_date = text['entities'][qid]['claims']['P569'][0]['mainsnak']['datavalue']['value']['time']
        birth_year = int(str(birth_date).split('-', 1)[0][1:])
    if birth_year < year:  # not a descendant for sure
        return False

    if qid == sqid:
        if 'en' in text['entities'][sqid]['labels']:
            search_name = text['entities'][sqid]['labels']['en']['value']
        else:
            search_name = sqid
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('\n    ' + search_name)
        return True

    if 'P22' in text['entities'][qid]['claims']:  # father
        father = text['entities'][qid]['claims']['P22'][0]['mainsnak']['datavalue']['value']['id']
        if search(father, depth, sqid, year):
            print('              ||          ')
            print('              \\/         ')
            print('    ' + name)
            return True
    if 'P25' in text['entities'][qid]['claims']:  # mother
        mother = text['entities'][qid]['claims']['P25'][0]['mainsnak']['datavalue']['value']['id']
        if search(mother, depth, sqid, year):
            print('              ||          ')
            print('              \\/         ')
            print('    ' + name)
            return True

    return False


def ancestry(qid, sqid):
    url = 'https://www.wikidata.org/wiki/Special:EntityData/' + sqid + '.json'
    res = requests.get(url)
    text = res.json()

    P569 = text['entities'][sqid]['claims']
    if 'P569' not in P569:
        year = 0
    else:
        date = P569['P569'][0]['mainsnak']['datavalue']['value']['time']
        year = int(str(date).split('-', 1)[0][1:])

    en = text['entities'][sqid]['labels']
    if 'en' in en:
        search_name = en['en']['value']
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
    if not search(qid, -1, sqid, year):
        print('\n' + name + ' is not a descendant of ' + search_name)
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print(str(amount) + ' royals were examined.')
