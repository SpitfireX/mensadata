import scrapy
import re
import datetime
import html


class WerksweltSpider(scrapy.Spider):
    name = 'werkswelt'
    allowed_domains = ['werkswelt.de']
    start_urls = ['http://werkswelt.de/?id=lmpl']

    def parse(self, response):
        site = response.url.split('?id=')[1]

        body = re.search(r'Speiseplan.+<h4>(.+)</h4>(.+)\n<form', response.text, re.DOTALL)
        assert body, 'Body regex did not yield a result'
        
        date, dishes = body.group(1, 2)

        assert date, 'No date string'

        date = datetime.datetime.strptime(date.split()[-1], '%d.%m.%Y')

        assert dishes, 'No dishes string'

        dishes = html.unescape(dishes)
        # normalize whitespace
        dishes = ' '.join(dishes.split())
        dishes = dishes.replace('</br>', '\n').strip()

        yield {
            'site': site,
            'date': date,
            'dishes': list(parse_dishes(dishes)),
            'raw': dishes,
        }

def parse_dishes(dishes):

    dishes = re.split(r'(Aktions)?[eE]ssen (\d+)', dishes)
    dishes = zip(dishes[1::3], dishes[2::3], dishes[3::3]) # group list elements into tuples, skip 0 because always empty/irrelevant
    
    for special, n, text in dishes:

        # split string on prices
        name, pstud, _, pemp, _, pguest, rest = re.split(r'(\d+,\d+) € \(.+?\)', text.strip())

        # addidional info badges
        badges = [m[1] for m in re.finditer(r'<img.+?infomax-food-icon (\w+).+?>', rest)]
        assert len(badges) > 0, "implausible dish without badges"

        # nutritional info
        nutrition = re.search(r'(Energie.+)\]', rest)[1].strip()

        # remove html markup from name
        name = ' '.join(re.sub(r'<.+?>', '', name).split())

        name, *sides = name.split('Wahlbeilagen:')

        # remove weird prefixes like "Aus dem WOK:"
        name = name.split(':')[-1]

        # remove phrases
        name = re.sub(r'verschieden garniert|-? ?in der Kühltheke', '', name)

        allergen_regex = re.compile(r'[[(](.+?)[])]')

        # canonical name without allergen info and empty phrases
        canonical_name = ' '.join(re.sub(allergen_regex, '', name).split())


        components = re.split(allergen_regex, name)
        components = zip(components[0::2], components[1::2])
        components = [
            {
                'name': name.strip(),
                'allergens': allergens.split(','),
                'optional': False,
            } for name, allergens in components]

        for n, c in enumerate(components):
            if n > 0:
                components[n]['name'] = re.sub(r'und|mit|auf|an', '', components[n]['name']).strip()
        
        if sides:
            s = re.split(allergen_regex, sides[0])

            for name, allergens in zip(s[0::2], s[1::2]):
                components.append(
                    {
                        'name': name.lstrip(',').strip(),
                        'allergens': allergens.split(','),
                        'optional': True,
                    }
                )

        yield {
            'n': n,
            'special': bool(special),
            'canonical': canonical_name,
            'components': components,
            'prices': {
                'student': priceformat(pstud),
                'employee': priceformat(pemp),
                'guest': priceformat(pguest),
            },
            'badges': badges,
            'nutrition': nutrition,
        }

def priceformat(price):
    return float(price.strip().replace(',', '.'))