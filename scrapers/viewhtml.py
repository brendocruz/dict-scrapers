from bs4 import BeautifulSoup as Soup
import lxml
import cchardet

from models import *


class ExampleGroupToHTML():
    """Convert an ExampleGroup object to HTML

    Structure for reference:
        div.example-group-container
            div.pattern
            ul.examples
                li

    """
    def __init__(self, example_group: ExampleGroup):
        self.example_group = example_group

    def convert(self) -> None:
        soup = Soup('<div></div>', 'lxml')
        soup.div['class'] = 'example-group-container'

        div_pattern = soup.new_tag('div', **{'class': 'pattern'})
        div_pattern.string = self.example_group.pattern
        soup.div.append(div_pattern)

        ul_examples = soup.new_tag('ul', **{'class': 'examples'})
        for example in self.example_group.examples:
            li_example = soup.new_tag('li')
            li_example.string = example
            ul_examples.append(li_example)
        soup.div.append(ul_examples)
        return soup.div

class KeywordsToHTML():
    def __init__(self, keywords: Keywords):
        self.keywords = keywords

    def convert(self):
        soup = Soup('<div></div>', 'lxml')
        soup.div['class'] = 'keywords-container'

        for keyword_type in (self.keywords.grammar, self.keywords.style,
                self.keywords.dialect, self.keywords.warnings):
            for keyword in keyword_type:
                span_keyword = soup.new_tag('span')
                span_keyword.string = keyword + ','
                soup.div.append(span_keyword)
        return soup.div

class WordDefinitionToHTML():
    """Convert a WordDefinition object to HTML

    Structure for reference:
        div.word_definition-container
            div.number            (number)
            div.definition        (defn)
            div.keywords          (keywords)
            div.examples          (examples)
            div.sub-definitions   (subdefns)
    """

    def __init__(self, word_definition: WordDefinition):
        self.word_definition = word_definition

    def convert(self):
        soup = Soup('<div></div>', 'lxml')
        soup.div['class'] = 'word-definition-container'
        
        # div.number
        div_number = soup.new_tag('div', **{'class': 'number'})
        div_number.string = str(self.word_definition.number)
        soup.div.append(div_number)
        
        # div.definition
        div_defn = soup.new_tag('div', **{'class': 'definition'})
        div_defn.string = self.word_definition.defn
        soup.div.append(div_defn)

        # div.keywords
        div_keywords = soup.new_tag('div', **{'class': 'keywords'})
        converter_keywords = KeywordsToHTML(self.word_definition.keywords)
        div_keywords.append(converter_keywords.convert())
        soup.div.append(div_keywords)

        # div.examples
        div_examples = soup.new_tag('div', **{'class': 'examples'})
        for examples in self.word_definition.examples:
            converter_examples = ExampleGroupToHTML(examples)
            div_examples.append(converter_examples.convert())
        soup.div.append(div_examples)

        # div.sub-definitions
        div_subdefns = soup.new_tag('div', **{'class': 'sub-definitions'})
        for subdefn in self.word_definition.subdefns:
            converter_defn = WordDefinitionToHTML(subdefn)
            div_subdefns.append(converter_defn.convert())
        soup.div.append(div_subdefns)
        return soup.div


class PhoneticsToHTML():
    """Convert a Phonetics objeto to HTML

    Structure of reference:
        div.phonetics-container
            div.spelling  (spelling)
            div.dialect   (dialect)
            div.qualifier (qualifier)
    """
    def __init__(self, phonetics: Phonetics):
        self.phonetics = phonetics

    def convert(self):
        root = Soup('<div></div>', 'lxml')
        root.div['class'] = 'phonetics-container'

        # div.spelling
        div_spelling = root.new_tag('div', **{'class': 'spelling'})
        div_spelling.string = self.phonetics.spelling
        root.div.append(div_spelling)

        # div.dialect
        div_dialect = root.new_tag('div', **{'class': 'dialect'})
        div_dialect.string = self.phonetics.dialect
        root.div.append(div_dialect)

        # div.qualifier
        div_qualifier = root.new_tag('div', **{'class': 'qualifier'})
        div_qualifier.string = self.phonetics.qualifier
        root.div.append(div_qualifier)

        return root.div


class DictEntryToHTML():
    """Convert a DictEntry object to HTML

    Structure for reference:
        div.dict-entry-container
            div.word          (word)
            ul.part-of-speech (pos)
                li
            div.phonetics     (phonetics)
            div.keywords      (keywords)
            div.definitions   (defns)
            div.frequency     (freq)
    """
    def __init__(self, dict_entry: DictEntry):
        self.dict_entry = dict_entry

    def convert(self):
        root = Soup('<div></div>', 'lxml')
        root.div['class'] = 'dict-entry-container'

        # div.word
        div_word = root.new_tag('div', **{'class': 'word'})
        div_word.string = self.dict_entry.word
        root.div.append(div_word)

        # ul.pos
        ul_pos = root.new_tag('ul', **{'class': 'part-of-speech'})
        for word_type in self.dict_entry.pos:
            li = root.new_tag('li')
            li.string = word_type
            ul_pos.append(li)
        root.div.append(ul_pos)

        # div.phonetics
        div_phonetics = root.new_tag('div', **{'class': 'phonetics'})
        for phonetics in self.dict_entry.phonetics:
            converter = PhoneticsToHTML(phonetics)
            div_phonetics.append(converter.convert())
        root.div.append(div_phonetics)

        # div.keywords
        div_keywords = root.new_tag('div', **{'class': 'keywords'})
        converter = KeywordsToHTML(self.dict_entry.keywords)
        div_keywords.append(converter.convert())
        root.div.append(div_keywords)
        
        # div.defn
        div_defns = root.new_tag('div', **{'class': 'definitions'})
        for defn in self.dict_entry.defns:
            converter = WordDefinitionToHTML(defn)
            div_defns.append(converter.convert())
        root.div.append(div_defns)

        return root

