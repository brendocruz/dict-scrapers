from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True, kw_only=True)
class ExampleGroup():
    """ A class that groups a set of related sentences.

    Attributes:
        examples    a list of sentences
        pattern     a sentence that is used as a pattern
    """
    examples: list[str] = field(default_factory=list)
    pattern:  str       = field(default_factory=str)


@dataclass(slots=True, frozen=True, kw_only=True)
class Keywords():
    grammar:  list[str] = field(default_factory=list)
    style:    list[str] = field(default_factory=list)
    dialect:  list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list) 


@dataclass(slots=True, frozen=True, kw_only=True)
class WordDefinition():
    """A word dictionary entry.

    Attributes:
        defn        The word definition
        number      The entry number
        keywords    
        examples    
        subdefns    
    """
    defn:     str                = field(default_factory=str)
    number:   str                = field(default_factory=str)
    keywords: list[Keywords]     = field(default_factory=list)
    examples: list[ExampleGroup] = field(default_factory=list)
    subdefns: list[any]          = field(default_factory=list)


@dataclass(slots=True, frozen=True, kw_only=True)
class Phonetics():
    spelling:  str = field(default_factory=str)
    dialect:   str = field(default_factory=str)
    qualifier: str = field(default_factory=str)


@dataclass(slots=True, frozen=True, kw_only=True)
class DictEntry():
    word:      str                  = field(default_factory=str)
    pos:       list[str]            = field(default_factory=list) 
    phonetics: list[Phonetics]      = field(default_factory=list)
    keywords:  list[Keywords]       = field(default_factory=list)
    defns:     list[WordDefinition] = field(default_factory=list)
    freq:      str                  = field(default_factory=str)
    source:    str                  = field(default_factory=str)


@dataclass(slots=True, frozen=True, kw_only=True)
class ErrorList:
    """
    Classe que representa a lista de possíveis palavras
    dadas por um dicionário, quando ele não acha a palavras
    que você está procurando.

    texts = mensagens (de error) do dicionário
    wordlist = lista de possíveis palavras
    """
    texts:    list[str] = field(default_factory=list)
    wordlist: list[str] = field(default_factory=list)


if __name__ == '__main__':
    pass
