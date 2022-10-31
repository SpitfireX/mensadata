.PHONY: install scrape

OUTFILE := "output.json"

install:
	pipenv install

scrape:
	cd werksscraper && pipenv run scrapy crawl werkswelt -o $(OUTFILE)
