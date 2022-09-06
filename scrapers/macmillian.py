from bs4 import BeautifulSoup as Soup
import lxml
import cchardet

from utils import split_list
from scraper import Scraper
from models import (
    ExampleGroup,
    WordDefinition,
    DictEntry,
    Phonetics,
    Keywords,
    ErrorList
)


class MacMillianDictScraper(Scraper):
    search_url = 'https://www.macmillandictionary.com/us/search/{dial}/direct/?q={word}'
    slug_url   = 'https://www.macmillandictionary.com/dictionary/{dial}/{slug}'
    dial_options = ('american', 'british')


    def __init__(self, word=None, slug=None, dial=None, recursive=True):
        self.dial      = 'american' if dial not in self.dial_options else dial
        self.word      = '' if word is None else word
        self.slug      = '' if slug is None else slug
        self.recursive = recursive

        if slug:
            final_url = self.slug_url.format(dial=self.dial, slug=self.slug)
        else:
            final_url = self.search_url.format(dial=self.dial, word=self.word)
        super().__init__(final_url)


    def extract(self):
        self.load()
        self.source_page = Soup(self.raw().text, 'lxml')

        if self.is_error_page():
            return self.parse_error_page()
        return self.parse_word_page()


    def is_error_page(self) -> bool:
        return bool(self.source_page.select('#search-results'))


    def parse_word_page(self) -> list[DictEntry]:
        sanitized_entries = []

        # get main page entry
        sanitized_main_entry = self.scrape_word_page(self.source_page)
        sanitized_entries.append(sanitized_main_entry)

        # get related pages
        text_title = sanitized_main_entry.word
        list_elm_related_links = self.source_page.select("#innerleftcol .related-entries-item a")
        if self.recursive:
            for elm_related_links in list_elm_related_links:
                elm_related_word = elm_related_links.select('.BASE')

                if elm_related_word:
                    text_related_word = elm_related_word[0].get_text()

                    if text_title == text_related_word:
                        # get the page
                        slug = elm_related_links.attrs['href'].split('/')[-1]
                        sanitized_data = MacMillianDictScraper(
                            slug=slug, dial=self.dial, recursive=False
                        ).extract()
                        sanitized_entries.append(sanitized_data)

        return sanitized_entries


    def scrape_word_page(self, source_page: Soup) -> DictEntry:
        """
        Receives a dict entry from MacMillian dictioanary
        Returns a DictEntry object
        """
        # get word of the page
        sanitized_word = source_page.select('.big-title > .BASE')[0].get_text()

        # get word phonetic pronunciation, if any
        list_scraped_phonetics = source_page.select('div.PRONS')
        list_sanitized_phonetics = []
        for scraped_phonetics in list_scraped_phonetics:
            # GET IPA SPELLING AND DIALECT (e.g. US, UK) [always true]
            scraped_spelling = scraped_phonetics.select('.PRON')
            scraped_dialect = scraped_phonetics.select('.pron_resource')
            if scraped_spelling:
                sanitized_phonetics_spelling = scraped_spelling[0].get_text().strip()
                sanitized_phonetics_dialect = scraped_dialect[0].get_text()

            # CREATE PHONETICS OBJECT
            sanitized_phonetics = Phonetics(
                spelling=sanitized_phonetics_spelling,
                dialect=sanitized_phonetics_dialect,
            )
            list_sanitized_phonetics.append(sanitized_phonetics)

            # GET QUALIFIER (e.g. STRONG, WEAK, US, UK) [only sometimes]
            scraped_qualifier = scraped_phonetics.select('.QUALIFIER')
            if scraped_qualifier:
                 sanitized_phonetics_qualifier= scraped_qualifier[0].get_text()
                 sanitized_phonetics.qualifier = sanitized_phonetics_qualifier


        # get word part of speech, if any
        scraped_pos = source_page.select('.entry-labels > .PART-OF-SPEECH')
        list_sanitized_pos = []
        if scraped_pos:
            self._remove_zero_space(scraped_pos[0])
            list_sanitized_pos = scraped_pos[0].get_text().split(', ')

        # get word keywrods (e.g. TRANSITIVE, COUNTABLE, PLURAL ...)
        elm_entry_labels = source_page.find(True, class_='entry-labels')
        list_scraped_keywords = elm_entry_labels.find_all(True, class_=[
            'SYNTAX-CODING',
            'RESTRICTION-CLASS',
            'STYLE-LEVEL',
            'GRAMMAR-TEXT',
            'DIALECT'
        ], recursive=False)
        sanitized_keywords = self.scrape_keywords(list_scraped_keywords)

        # get frequency info (red stars)
        list_red_stars = source_page.select('.entry-red-star')
        text_frequency = ''
        if list_red_stars:
            text_num_stars = len(list_red_stars)
            text_frequency = '\u2605' * text_num_stars
        

        # get dict entries
        list_scraped_defns = source_page.select('.SENSE-BODY, .SUB-SENSE-BODY')
        list_sanitized_defns = self.scrape_defns(list_scraped_defns)
        
        return DictEntry(
           word=sanitized_word,
           pos=list_sanitized_pos,
           phonetics=list_sanitized_phonetics,
           keywords=sanitized_keywords,
           defns=list_sanitized_defns,
           freq=text_frequency,
           source='MacMillian Dicionary'
        )


    def scrape_keywords(self, list_scraped_tags) -> Keywords:
        keywords_grammar     = []
        keywords_style       = []
        keywords_dialect     = []
        keywords_restriction = []
        for scraped_keyword in list_scraped_tags:
            self._remove_zero_space(scraped_keyword)
            sanitized_keyword = scraped_keyword.get_text().strip()

            class_list = scraped_keyword['class'][0]
            if class_list == 'SYNTAX-CODING':
                keywords_grammar.append(sanitized_keyword)
            elif class_list == 'STYLE-LEVEL':
                keywords_style.append(sanitized_keyword)
            elif class_list == 'DIALECT':
                keywords_dialect.append(sanitized_keyword)
            elif class_list == 'RESTRICTION-CLASS':
                keywords_restriction.append(sanitized_keyword)
        return Keywords(
            grammar=keywords_grammar,
            style=keywords_style,
            dialect=keywords_dialect,
            warnings=keywords_restriction
        )


    def scrape_defns(self, list_scraped_defns) -> list[WordDefinition]:
        """
        Receives a list of .SENSE-BODY or .SUB-SENSE-BODY html elements
        from a MacMillian Dicionary entry page

        Return a list of WordDefinition objects
        """
        list_sanitized_defns = []
        for scraped_defn in list_scraped_defns:

            # definition number
            scraped_number = scraped_defn.select('.SENSE-NUM')
            sanitized_number = '' if not scraped_number else scraped_number[0].get_text()

            scraped_defn = scraped_defn.find(True, class_=['SENSE-CONTENT', 'SUB-SENSE-CONTENT'])
            # meaning info (e.g TRANSITIVE, COUNTABLE...)
            # .STYNTAX-CODING: transitive ...
            # .RESTRICTION-CLASS: never progressive ...
            # .STYLE-LEVEL: mainly spoaken ...
            list_scraped_keywords = scraped_defn.find_all(True,
                class_=[
                    'SYNTAX-CODING',
                    'RESTRICTION-CLASS',
                    'STYLE-LEVEL',
                    'GRAMMAR-TEXT',
                    'DIALECT'
                ],
            recursive=False)
            sanitized_keywords = self.scrape_keywords(list_scraped_keywords)

            # extracting definition
            scraped_meaning = scraped_defn.select('.DEFINITION, .SAMEAS, .QUICK-DEFINITION')
            sanitized_meaning = scraped_meaning[0].get_text()

            # extracting sentences examples and collocations
            list_sanitized_examples = []
            list_scraped_examples = scraped_defn.find_all('div', class_='EXAMPLES', recursive=True)
            if list_scraped_examples:
                list_sanitized_examples = self.scrape_defn_examples(list_scraped_examples)

            sanitized_defn = WordDefinition(
                number=sanitized_number,
                defn=sanitized_meaning,
                examples=list_sanitized_examples,
                keywords=sanitized_keywords
            )

            # append in list_sanitized_defns
            if scraped_defn.attrs['class'][0] == 'SUB-SENSE-CONTENT':
                if class_last_defn == 'SUB-SENSE-CONTENT':
                    list_sanitized_defns[-1].subdefns.append(sanitized_defn)
                else:
                    last_sanitized_defn.subdefns.append(sanitized_defn)
            else:
                list_sanitized_defns.append(sanitized_defn)

            class_last_defn = scraped_defn.attrs['class'][0]
            last_sanitized_defn = sanitized_defn

        return list_sanitized_defns


    def scrape_defn_examples(self, list_scraped_examples) -> list[ExampleGroup]:
        """
        Receives a list of div.EXAMPLES HTML elements
        from a MacMillian Dictionary entry page

        Returns a list of ExampleGroup objects

        div.EXAMPLES structure
            span.PATTERNS-COLLOCATIONS
            [...]
            p.EXAMPLE
        """
        list_sanitized_patterns = []

        # divide the list of div.EXAMPLES
        list_pattern_indexes  = []
        for index, scraped_example in enumerate(list_scraped_examples):
            if scraped_example.select('.PATTERNS-COLLOCATIONS'):
                list_pattern_indexes.append(index)

        list_parts = split_list(list_scraped_examples, indexes=list_pattern_indexes)
        for part in list_parts:
            scraped_pattern = part[0].select('.PATTERNS-COLLOCATIONS')
            list_sanitized_examples = []
            for scraped_example in part:
                sanitized_example = scraped_example.select('p.EXAMPLE')[0].get_text()
                list_sanitized_examples.append(sanitized_example)

            sanitized_pattern = '' if not scraped_pattern else scraped_pattern[0].get_text()
            list_sanitized_patterns.append(ExampleGroup(
                pattern=sanitized_pattern, examples=list_sanitized_examples
            ))

        return list_sanitized_patterns            


    def parse_error_page(self):
        return self.scrape_error_page()


    def scrape_error_page(self) -> ErrorList:
        """
        Scrape the content of the error page
        (e.g. when you types an word that does not exist)
        Returns an ErrorList object
        """
        # scrape the texts
        text_title = self.source_page.select('#search-results h1')[0].get_text()
        text_subtitle = self.source_page.select('.entry-bold')[0].get_text()

        # scrape the list of words
        wordlist = []
        list_elm_word = self.source_page.select('.display-list li')
        for elm_word in list_elm_word:
            wordlist.append(elm_word.get_text())

        return ErrorList(
            texts=[text_title, text_subtitle],
            wordlist=wordlist
        )

    def _remove_zero_space(self, tag):
        unnecessary_tag = tag.find('span', class_='zwsp')
        if unnecessary_tag:
            unnecessary_tag.clear()

