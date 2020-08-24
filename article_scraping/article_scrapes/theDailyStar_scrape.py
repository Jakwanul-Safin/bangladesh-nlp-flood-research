from unidecode import unidecode

def theDailyStarScrape(soup, meta):
    headline = soup.find('h1', itemprop='headline')
    if headline: headline = headline.text
    authors = soup.find('div', itemprop='author')
    if authors:
        authors2 = authors.find('span', itemprop='name')
        if authors2:
            authors3 = authors.find_all('a')
            if authors3:
                authors = [a.text for a in authors3]
            else:
                authors = authors.text
    text = soup.find('article', role='article')
    if text:
        textp = text.find_all('p')
        if textp: text = ' '.join([p.text for p in textp])

    if headline: headline = unidecode(headline)
    if authors: authors = unidecode(authors)
    if text: text = unidecode(text)

    return {
        'headline': headline,
        'authors': authors,
        'text': 'Date Published:{}      \n'.format(meta['datePublished']) + text
    }