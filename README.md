# pds_pgalyzer
Python module, with CLI, for text analysis of Project Gutenberg files.

This module is a project created for the Python for Data Science course under the MS in Data Science program of the Asian Institute of Management, taught by Prof. Christian Alis. The module specfications are also his own design.

The project was a collaboration between three people:  
1. Joseph Matthew Azanza  
2. Albertyn Nicolle Carpio  
3. Matthew Maulion  

## Module specifications
The module specifications are as follows:

## The `PGalyzer` class

The module should contain one class named `PGalyzer`. It should have the following specifications:

### Initialization

The class initializer should accept a string `text_file` which is the filepath to the text file that will be analyzed. It should also accept an optional parameter `clean_pg` (default `False`) which, when `True`, will assume the file is a Project Gutenberg file and clean it by doing the following operations:

* remove headers and footers
* join sentences in a paragraph
* remove punctuation
* make all letters lowercase

Header and footer boundaries are marked by `***` along with relevant text.

The text after performing the operations above or the raw text, if `clean_pg` is `False`, should be assigned to the attribute `text`.

It should raise a `PGalyzerError` that inherits from `ValueError` if the file is not a Project Gutenberg text content file. 

#### Features

##### $n$-gram count

An $n$-gram is a sequence of $n$ successive words in a paragraph of text. For this project, we define a word as a sequence of non-whitespace characters.

* Create a method `ngrams` which returns a dict-like object with the $n$-gram string as keys and their counts as values. It should accept an optional argument `n` with default value 1 which corresponds to the $n$ value of the $n$-gram.

##### Word count

* Create a method `word_count` that returns a dict-like object with the word as keys and the frequency as values.

##### Concordance

Word concordance lists the occurrence of a word along with its context in a text.

* Create a method `concordance` which returns the list of occurrences of the parameter `word` along with its context. It should have an optional argument `neighborhood_size` with default value 10. The return value should be a list of tuples: `(string_before, string_after)`. The `string_before` is the string consisting of (up to) `neighborhood_size` words before the word occurrence, and `string_after` is the string consisting of (up to) `neighborhood_size` words after the word occurrence. For example, the output for the word `mary` using the lyrics of the nursery song "Mary Had a Little Lamb" as text with `neighborhood_size = 4`,  should be similar to `[('', 'had a little lamb'), ('snow and everywhere that', 'went the lamb was'), ('waited patiently about till', 'did appear why does'), ('does the lamb love', 'so the eager children'), ('eager children cry why', 'loves the lamb you')]`. Sort by order of appearance.

* Create a method `display_concordance` which displays the word in context in a paragraph. It should accept the same arguments as `concordance`. When displayed on a notebook cell, the word for that occurrence should be bold and vertically aligned with other occurrences. For example, the sample output for `concordance` should be displayed as:

<pre>
                            <b>mary</b> had a little lamb
   snow and everywhere that <b>mary</b> went the lamb was
waited patiently about till <b>mary</b> did appear why does
         does the lamb love <b>mary</b> so the eager children
     eager children cry why <b>mary</b> loves the lamb you
</pre>

##### Most likely previous/next word

* Create methods `likely_next` and `likely_previous`, which returns a list of the `n` most likely next/previous words along with their frequency as a tuple, sorted by decreasing likelihood. Both methods should accept a parameter `word` and optional argument `n` (default: 5); the former being the word to search and the latter the number of likely words to return.

### CLI


#### Supported command line arguments

It should support the following command line arguments:

* `ngrams {pg_filepath} [-n n] [--clean-pg]`

   Output the $n$-grams along with their count, one per line. The n-gram and its count should be separated by a tab character and they should be sorted from most frequent $n$-gram to least. If two or more $n$-grams have the same count, then they are to be sorted alphabetically to determine the order. The optional parameter `n` specifies the `n` in $n$-gram and by default is equal to 1.
   
* `word-count {pg_filepath} [--clean-pg]`

   Output the words along with their count, one per line. The word and its count should be separated by a tab character and they should be sorted from most frequent word to least. If two or more words have the same count, then they are to be sorted alphabetically to determine the order.

* `concordance {pg_filepath} {word} [-n|--ns ns] [--clean-pg]`

    Output the words before and after `word`, separated by a tab character, one `word` per line similar to `concordance`. The optional parameter `n` or `ns` specifies the number of words before and after the `word` to be displayed and by default is equal to 10.
    
* `display-concordance {pg_filepath} {word} [-n|--ns ns] [--clean-pg]`

    Display the concordance of `word` similar to the output of `display_concordance`. However, instead of displaying `word` in bold, add `**` before and after it (`**word**`).


* `likely-next {pg_filepath} {word} [-n n] [--clean-pg]`
* `likely-previous {pg_filepath} {word} [-n n] [--clean-pg]`

    Output the most likely next or previous words of `word`, one word along with its frequency per line, sorted by decreasing frequency. The optional argument `n` specifies the number of words to output and by default is equal to 5.

 
#### Common optional arguments

The argument `{pg_filepath}` should be a filepath of a Project Gutenberg text content file. If it is `-` then it should read from the standard input and assume that it is the content of a Project Gutenberg file. It should print a message `ERROR: The file or content is not a Project Gutenberg text content file.` then exit if the file is not a Project Gutenberg text content file.

If passed, the `--clean-pg` flag performs cleaning operations on the input file similar to the `clean_pg` parameter of the `PGalyzer` initialization method.

#### I/O

All outputs should be to standard output.
