#!/usr/bin/env python

# THIRD PARTY LIBRARIES
import pandas as pd
import numpy as np
import click

# STANDARD PYTHON
from collections import Counter, defaultdict
from os.path import exists
from sys import stdin


class PGalyzer:
    def __init__(self, text_file, clean_pg=False):
        """
        Create a PGalyzer object.

        This method initializes a PGalyzer object.  This has two
        modes: the first to simply load the file; the second to
        parse and clean the file.  Cleaning entails the following:
            - Removing certain punctuations
            - Removing headers and footers
            - Joining sentences in one paragraph
            - Convert all text to lowercase

        Loaded text data is saved under the text attribute.

        Parameters
        ----------
        text_file: string
            Filepath of a Project Gutenberg file
        clean_pg: boolean
            Flag for cleaning

        Returns
        -------
        : a PGalyzer object
            Loaded text data from file as saved under the text
            attribute

        Examples
        --------
        >>> analyzer = PGalyzer('pg_start_only.txt', clean_pg=True)
        "produced by roger squires a study in scarlet by a conan doyle 1"

        >>> test_file = "/mnt/data/public/gutenberg/2/6/2/0/26206/26206.txt"
        >>> analyzer = PGalyzer(test_file, True)
        >>> analyzer.text[:200]
        "produced by greg weeks dave lovelace stephen blundell and the online"
        "distributed proofreading team at httpwwwpgdpnet\n_pandemic_\n_by j f"
        "bone_\n        _generally           human beings don't do       t"

        """
        # Load the file contents
        if type(text_file) == str:
            with open(text_file, 'r') as f:
                file = f.read()
        else:
            file = text_file[0] + text_file[1].read().replace('\r', ' ')

        if clean_pg:
            # Convert to lower case
            # Divide according to paragraphs
            file = file.lower().split('\n\n')

            # Remove header and footer
            head = '*** start of this project gutenberg ebook'
            foot = '*** end of this project gutenberg ebook'

            for ix, text in enumerate(file):
                if text.startswith(head):
                    del file[:ix+1]
                    break

            for ix, text in enumerate(file[::-1]):
                if text.startswith(foot):
                    del file[-(ix+1):]
                    break

            # Remove punctuation and empty strings
            punct = '|;,.:?!"()[]{}/\\-+'
            file = list(filter(('').__ne__, file))

            for ix, text in enumerate(file):
                text = text.strip('\n').replace('\n', ' ')
                for p in punct:
                    text = text.replace(p, '')
                file[ix] = text + '\n'

            self.text = ''.join(file).strip()
        else:
            self.text = file

    def ngrams(self, n=1):
        """
        Count the number of times a group of words (defined by n)
        are found within a file.

        Parameters
        ----------
        n: int
            Number of (consecutive) words to group together.

        Returns
        -------
        ngrams: dict
            Count of n-gram repetitions

        """
        paragraphs = self.text.split('\n')
        ngrams = []

        for p in paragraphs:
            words_all = p.split()
            for i in range(len(words_all)):
                if i+n > len(words_all):
                    break
                else:
                    ngrams.append(' '.join(words_all[i:i+n]))

        return Counter(ngrams)

    def word_count(self):
        """
        Return the count of each word (characters bounded by whitespace).
        """
        return Counter(self.text.split())

    def concordance(self, word, neighborhood_size=10):
        """
        Takes in a `word` and the optional argument `neighborhood_size`
        and returns a list of tuples with format `(string_before,
        string_after)`. The `string_before` is the string of words
        starting from the `word` and counting back by the
        `neighborhood_size`. The `string_after` is the string of words
        starting from the word and counting forward
        by the `neighborhood_size`.

        Parameters
        ----------
        text: str
            Text file to search word in
        word: str
            Word to search for
        neighborhood_size : int
            Default: 10
            Number of words to count backwards/forward from the `word

        Returns
        -------
        concordance: list of tuples
            In the format of `(string_before, string_after)`

        Example
        -------
        text = 'Mary Had a Little Lamb' full song lyrics
        word = 'mary'
        neighborhood_size = 4
        concordance = [('', 'had a little lamb'),
                       ('snow and everywhere that', 'went the lamb was'),
                       ('waited patiently about till', 'did appear why does'),
                       ('does the lamb love', 'so the eager children'),
                       ('eager children cry why', 'loves the lamb you')]
        """

        # Setting things up
        concordance = []
        text_split = self.text.split('\n')
        for line in text_split:
            items = line.split()

            # Figuring out the indices of each word occurence
            indices = [i for i, s in enumerate(items) if word == s]

            # Setting up the backward and forward index for neighboring words
            for i in indices:
                if i - neighborhood_size < 0:
                    backward_index = 0
                else:
                    backward_index = i - neighborhood_size

                forward_index = i + neighborhood_size + 1

                # Appending 'string_before' and 'string_after' as a tuple
                string_before = (' ').join(items[backward_index:i])
                string_after = (' ').join(items[i+1:forward_index])
                concordance.append((string_before, string_after))

        return concordance

    def display_concordance(self, word, neighborhood_size=10):
        """
        Accepts the same arguments as `concordance`: `word`
        and `neighborhood_size` and then displays the aligned
        `word`s flanked by their corresponding `string_before`s
        and `string_after`s

        Parameters
        ----------
        text: str
            Text file to search word in
        word: str
            Word to search for
        neighborhood_size : int
            Default: 10
            Number of words to count backwards/forward from the `word

        Returns
        -------
        display: str
            the strings are aligned in monospace font:
            `string_before1` <b>word</b> `string_after1`
            `string_before2` <b>word</b> `string_after2`
            `string_before3` <b>word</b> `string_after3`

        Example
        -------
        text = 'Mary Had a Little Lamb' full song lyrics
        word = 'mary'
        neighborhood_size = 4
        concordance = [('', 'had a little lamb'),
                       ('snow and everywhere that', 'went the lamb was'),
                       ('waited patiently about till', 'did appear why does'),
                       ('does the lamb love', 'so the eager children'),
                       ('eager children cry why', 'loves the lamb you')]
        display =
        <pre>
                                    <b>mary</b> had a little lamb
           snow and everywhere that <b>mary</b> went the lamb was
        waited patiently about till <b>mary</b> did appear why does
                 does the lamb love <b>mary</b> so the eager children
             eager children cry why <b>mary</b> loves the lamb you
        </pre>
        """

        # Being efficient and utilizing the concordance method
        concordance = self.concordance(word=word,
                                       neighborhood_size=neighborhood_size)

        # Calculating number of spaces to append for alignment
        display = []
        space = max([len(l) for l in list(zip(*concordance))[0]])

        # Setting up the lines of display
        for element in concordance:
            display.append(' '*(space - len(element[0])) + element[0]
                           + ' ' + '<b>' + word + '</b>' + ' ' + element[1])

        # Finalizing display
        display[0] = '<pre>' + display[0]
        display[len(display)-1] = display[len(display)-1] + '</pre>'
        display = ('\n').join(display)
        return display

    def likely_next(self, word, n=5):
        """
        Returns the most likely next words in a text

        A word is defined as a sequence of all non-whitespace characters
        between. whitespaces. Words are case-insensitive.

        Parameters
        ----------
        self : str
            Pertaining to init function on where to get text
            Contains text to train at.
        word : string
            Find the most likely next words of `word`
        n : int
            The number words to show (default is 5)


        Returns
        -------
        A list of tuples
            This is a list of the `n` most likely next words along with their
            frequency as a tuple, sorted by decreasing likelihood.

        Example
        -------
        word : 'of'
        n : default (5)

        Expected output:

        [('the', 30), ('his', 5), ('it', 5), ('that', 4), ("thurston's", 4)])
        """
        text_split = self.text.split('\n')
        count_dict = {}
        new_dict = defaultdict(list)
        for line in text_split:
            words = line.split()
            for index in range(len(words)-1):
                new_dict[words[index]] += [words[(index + 1)]]
                # next word
        for key in new_dict.keys():
            count_dict[key] = sorted(Counter(new_dict[key]).most_common(),
                                     key=lambda i: (-i[1], i[0]))

        return (count_dict[word])[:n]

    def likely_previous(self, word, n=5):
        """
        Returns the most likely previous words in a text

        A word is defined as a sequence of all non-whitespace characters
        between. whitespaces. Words are case-insensitive.

        Parameters
        ----------
        self : str
            Pertaining to init function on where to get text
            Contains text to train at.
        word : string
            Find the most likely previous words of `word`
        n : int
            The number words to show (default is 5)

        Returns
        -------
        A list of tuples
            This is a list of the `n` most likely previous words along
            with their frequency as a tuple, sorted by decreasing likelihood.

        Example
        -------
        word : 'of'
        n : 10

        Expected output:

        [('out', 7), ('one', 6), ('cent', 4), ('end', 4), ('cloud', 3),
         ('number', 3), ('part', 3), ('afraid', 2), ('because', 2),
         ('died', 2)]

        """
        text_split = self.text.split('\n')
        new_dict = defaultdict(list)
        count_dict = {}
        for line in text_split:
            words = line.split()
            for index in range(1, len(words)):
                new_dict[words[index]] += [words[(index - 1)]]
                # previous word
        for key in new_dict.keys():
            count_dict[key] = sorted(Counter(new_dict[key]).most_common(),
                                     key=lambda i: (-i[1], i[0]))

        return (count_dict[word])[:n]

# CLI Section
@click.group()
def cli():
    pass


# main block
@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('-c', '--clean-pg', is_flag=True,
              help='Flag for triggering file cleanup.')
def main(file, clean_pg):
    """Create a PGalyzer object."""
    if file == '-':
        for line in stdin:
            if 'Project Gutenberg' not in line:
                raise click.ClickException("The file or content is not "
                                           "a Project Gutenberg text "
                                           "content file.")
            break
        file = (line, stdin)
    else:
        # Echo error if exists = False
        if not exists(file):
            raise click.ClickException(
                "Invalid value for file path. "
                "Path {} does not exist.".format(file)
            )

    return PGalyzer(file, clean_pg)


# ngrams block
@cli.command(context_settings=dict(
             ignore_unknown_options=True,
             ))
@click.argument('file', type=click.Path(allow_dash=True))
@click.option('-n', default=1, type=click.INT,
              help='Number of words in the n-gram.')
@click.option('-c', '--clean-pg', is_flag=True,
              help='Flag for triggering file cleanup.')
def ngrams(file, n, clean_pg):
    """
    Retrieve the sorted ngram counts of the requested file.

    Create a PGalyzer object using the passed filename.
    Count the n-grams based on the input number, and sort them
    by count and alphabetically (in that order of precedence).

    Parameters
    ----------
    file: string
        Filepath
    n: int
        Number of words in each n-gram; default=1
    clean_pg: bool
        Flag for cleaning the parsed file; default=False

    Returns
    -------
    : string
        Concatenated list of all possible n-grams in the file,
        sorted by count and alphabetically. Each n-gram entry
        is separated from its count by a tab character (`\t`),
        and each entry appears on its own line (`\n`).

    Example
    -------
    $ python pgalyzer.py ngrams <filename>

    'the\t483\nof\t248\na\t211\nand\t196\nto\t187\nin\t134\n
    you\t118\nwith\t97\nor\t86\nthat\t79\nProject\t78\nI\t76\n
    he\t63\nwas\t63\nit\t57\nthis\t57\nfor\t55\nis\t54\n
    Gutenberg-tm\t53\nbe\t52\n*\t50\nas\t47\non\t46\nhave\t45\n
    at\t43\nshe\t42\nnot\t41\nwork\t41\nare\t40\nfrom\t40\n
    The\t40\nany\t39\nHe\t39\nKramer\t37\nhad\t33\nMary\t33\n
    "I\t32\nby\t32\nher\t31\nShe\t31\nbut\t30\ndo\t30\n...'

    """
    if file == '-':
        for line in stdin:
            if 'Project Gutenberg' not in line:
                raise click.ClickException("The file or content is not "
                                           "a Project Gutenberg text "
                                           "content file.")
            break
        file = (line, stdin)
    else:
        # Echo error if exists = False
        if not exists(file):
            raise click.ClickException(
                "Invalid value for file path. "
                "Path {} does not exist.".format(file)
            )

    file = PGalyzer(file, clean_pg)
    ngrams = file.ngrams(n)
    ngrams = sorted([x for x in ngrams.most_common()],
                    key=lambda x: (-x[1], x[0].lower()))
    ngrams = [x + '\t' + str(y) for x, y in ngrams]
    click.echo('\n'.join(ngrams))


# word_count block
@cli.command()
@click.argument('file', type=click.Path(allow_dash=True))
@click.option('-c', '--clean-pg', is_flag=True,
              help='Flag for triggering file cleanup.')
def word_count(file, clean_pg):
    """
    Retrieve the sorted word counts of the requested file.

    Create a PGalyzer object using the passed filename.
    Count the words, and sort them by count and alphabetically
    (in that order of precedence).

    Parameters
    ----------
    file: string
        Filepath
    clean_pg: bool
        Flag for cleaning the parsed file; defaul=False

    Returns
    -------
    : string
        Concatenated list of all possible words in the file,
        sorted by count and alphabetically. Each word entry
        is separated from its count by a tab character (`\t`),
        and each entry appears on its own line (`\n`).

    Example
    -------
    $ python pgalyzer.py word-count <filename>

    'the\t483\nof\t248\na\t211\nand\t196\nto\t187\nin\t134\n
    you\t118\nwith\t97\nor\t86\nthat\t79\nProject\t78\nI\t76\n
    he\t63\nwas\t63\nit\t57\nthis\t57\nfor\t55\nis\t54\n
    Gutenberg-tm\t53\nbe\t52\n*\t50\nas\t47\non\t46\nhave\t45\n
    at\t43\nshe\t42\nnot\t41\nwork\t41\nare\t40\nfrom\t40\n
    The\t40\nany\t39\nHe\t39\nKramer\t37\nhad\t33\nMary\t33\n
    "I\t32\nby\t32\nher\t31\nShe\t31\nbut\t30\ndo\t30\n...'

    """
    if file == '-':
        for line in stdin:
            if 'Project Gutenberg' not in line:
                raise click.ClickException("The file or content is not "
                                           "a Project Gutenberg text "
                                           "content file.")
            break
        file = (line, stdin)
    else:
        # Echo error if exists = False
        if not exists(file):
            raise click.ClickException(
                "Invalid value for file path. "
                "Path {} does not exist.".format(file)
            )

    file = PGalyzer(file, clean_pg)
    wc = file.word_count()
    wc = sorted([x for x in wc.most_common()],
                key=lambda x: (-x[1], x[0].lower()))
    wc = [x + '\t' + str(y) for x, y in wc]
    click.echo('\n'.join(wc))


# concordance block
@cli.command()
@click.argument('file', type=click.Path(allow_dash=True))
@click.argument('word')
@click.option('-n', '--ns', default=10, type=click.INT,
              help='Number of words to count back/forward from the `word`')
@click.option('-c', '--clean-pg', is_flag=True,
              help='Flag for triggering file cleanup.')
def concordance(file, word, ns, clean_pg):
    """
    Takes in a `word` and the optional argument `neighborhood_size`
    and returns a string with format `string_before\tstring_after
    where the `string_before` is the string of words starting from
    the `word` and counting back by the `ns` and the `string_after`
    is the string of words starting from the word and counting
    forward from the `neighborhood_size`.

    Parameters
    ----------
    file: str
        File to search word in
    word: str
        Word to search for
    ns : int
        Default: 10
        Number of words to count backwards/forward from the `word
    clean_pg: bool
        True: clean up file
        False: do nothing

    Echoes
    ----
    final: str
        A single string that contains the `string_before` and
        the `string_after` words separated by '\t', with
        one set per line separated by '\n'
    """
    if file == '-':
        for line in stdin:
            if 'Project Gutenberg' not in line:
                raise click.ClickException("The file or content is not "
                                           "a Project Gutenberg text "
                                           "content file.")
            break
        file = (line, stdin)
    else:
        # Echo error if exists = False
        if not exists(file):
            raise click.ClickException(
                "Invalid value for file path. "
                "Path {} does not exist.".format(file)
            )

    file = PGalyzer(file, clean_pg)
    concordance = file.concordance(word=word, neighborhood_size=ns)
    final = []
    for words in concordance:
        final.append(words[0] + '\t' + words[1]+'\n')
    final = ('').join(final)
    click.echo(final)


# display_concordance block
@cli.command()
@click.argument('file', type=click.Path(allow_dash=True))
@click.argument('word')
@click.option('-n', '--ns', default=10, type=click.INT,
              help='Number of words to count back/forward from the `word`')
@click.option('-c', '--clean-pg', is_flag=True,
              help='Flag for triggering file cleanup.')
def display_concordance(file, word, ns, clean_pg):
    """
    Takes in a `word` and the optional argument `neighborhood_size`
    and returns a string with format `string_before\tstring_after
    where the `string_before` is the string of words starting from
    the `word` and counting back by the `ns` and the `string_after`
    is the string of words starting from the word and counting
    forward from the `neighborhood_size`.

    Parameters
    ----------
    file: str
        File to search word in
    word: str
        Word to search for
    ns : int
        Default: 10
        Number of words to count backwards/forward from the `word
    clean_pg: bool
        True: clean up file
        False: do nothing

    Echoes
    ----
    display: str
        A single string that contains the context and the word
        in this format: `string_before` **word** `string_after`
        with one set per line separated by '\n'
    """
    if file == '-':
        for line in stdin:
            if 'Project Gutenberg' not in line:
                raise click.ClickException("The file or content is not "
                                           "a Project Gutenberg text "
                                           "content file.")
            break
        file = (line, stdin)
    else:
        # Echo error if exists = False
        if not exists(file):
            raise click.ClickException(
                "Invalid value for file path. "
                "Path {} does not exist.".format(file)
            )

    file = PGalyzer(file, clean_pg)
    display = file.display_concordance(word=word, neighborhood_size=ns)
    display = display.replace('<pre>', '', 1)
    display = display.replace('</pre>', '', 1)
    display = display.replace('<b>', '**')
    display = display.replace('</b>', '**')
    click.echo(display)


# Likely_next block
@cli.command()
@click.argument('file', type=click.Path(allow_dash=True))
@click.argument('word')
@click.option('-n', default=5, type=click.INT,
              help='Number of likely next words to return.')
@click.option('-c', '--clean-pg', is_flag=True,
              help='Flag for triggering file cleanup.')
def likely_next(file, word, n, clean_pg):
    """
    Returns the most likely next words in a text

    A word is defined as a sequence of all non-whitespace characters
    between. whitespaces. Words are case-insensitive.

    Parameters
    ----------
    file : str
        Contains text to train at.
    word : string
        Find the most likely next words of `word`
    n : int
        The number words to show (default is 5)
    clean_pg : bool
        This is a flag for cleaning

    Echoes
    ----
    out : str
        This is a single string that contains the n most likely
        next words along with their frequency (separted by '\t')
        sorted by decreasing likelihood (every pair is separated by '\n')

    Example
    -------
    $ python pgalyzer.py likely-next <filename>

    Expected output:

    'the\t52\nthis\t17\na\t8\nProject\t7\nhis\t5\n\n'
    """
    if file == '-':
        for line in stdin:
            if 'Project Gutenberg' not in line:
                raise click.ClickException("The file or content is not "
                                           "a Project Gutenberg text "
                                           "content file.")
            break
        file = (line, stdin)
    else:
        # Echo error if exists = False
        if not exists(file):
            raise click.ClickException(
                "Invalid value for file path. "
                "Path {} does not exist.".format(file)
            )

    file = PGalyzer(file, clean_pg)
    likely_next = file.likely_next(word, n)
    out = []
    for tup in likely_next:
        out.append(tup[0] + '\t' + str(tup[1]) + '\n')
    out = ('').join(out)
    click.echo(out)


# likely_previous block
@cli.command()
@click.argument('file', type=click.Path(allow_dash=True))
@click.argument('word')
@click.option('-n', default=5, type=click.INT,
              help='Number of likely previous words to return.')
@click.option('-c', '--clean-pg', is_flag=True,
              help='Flag for triggering file cleanup.')
def likely_previous(file, word, n, clean_pg):
    """
    Returns the most likely previous words in a text

    A word is defined as a sequence of all non-whitespace characters
    between. whitespaces. Words are case-insensitive.

    Parameters
    ----------
    file : str
        Contains text to train at.
    word : string
        Find the most likely previous words of `word`
    n : int
        The number words to show (default is 5)
    clean_pg : bool
        This is a flag for cleaning

    Echoes
    ----
    out : str
        This is a single string that contains the n most likely
        previous words along with their frequency (separted by '\t')
        sorted by decreasing likelihood (every pair is separated by '\n')

    Example
    -------
    $ python pgalyzer.py likely-previous <filename>

    Expected output:

    'terms\t15\ncopies\t7\nout\t7\npart\t7\ndistribution\t5\n\n'
    """
    if file == '-':
        for line in stdin:
            if 'Project Gutenberg' not in line:
                raise click.ClickException("The file or content is not "
                                           "a Project Gutenberg text "
                                           "content file.")
            break
        file = (line, stdin)
    else:
        # Echo error if exists = False
        if not exists(file):
            raise click.ClickException(
                "Invalid value for file path. "
                "Path {} does not exist.".format(file)
            )

    file = PGalyzer(file, clean_pg)
    likely_previous = file.likely_previous(word, n)
    out = []
    for tup in likely_previous:
        out.append(tup[0] + '\t' + str(tup[1]) + '\n')
    out = ('').join(out)
    click.echo(out)


if __name__ == '__main__':
    cli()
