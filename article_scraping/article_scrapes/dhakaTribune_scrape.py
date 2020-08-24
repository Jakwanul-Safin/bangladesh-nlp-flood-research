from unidecode import unidecode

def dhakaTribuneScrape(soup, meta):
    main_div = soup.find('div', class_='report-mainhead')

    headline = main_div.find('h1')
    if headline: headline = headline.text.strip()
    authors = main_div.find('div', class_='author-bg')
    if authors: authors = authors.text.strip()
    text = main_div.find('div', class_='report-content')
    if text:
        textp = text.find_all('p')
        if textp: text = ' '.join([p.text for p in textp])
    if not text: text = main_div.text
    if type(text)!=str: text=''

    if headline: headline = unidecode(headline)
    if authors: authors = unidecode(authors)
    if text: text = unidecode(text)

    return {
        'headline': headline,
        'authors': authors,
        'text': 'Date Published:{}      \n'.format(meta['datePublished'])+text
    }
