import nltk
import sys
import re

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to" | "until"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> S CP | NPPP VPPP
NPPP -> NP | NP PP
VPPP -> VP | VP PP | VP PP Adv
NP -> N | DP NP
VP -> V | V NPPP | Adv VP | V Adv
DP -> Det | Det AP
AP -> Adj | Adj AP
PP -> P NP | P S
CP -> Conj S | Conj VP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    words = list()

    # Tokenize the sentence to receive a list of words
    for word in nltk.tokenize.word_tokenize(sentence):
        # If there is no single alphabet, skip the word
        if len(re.findall("[a-zA-Z]", word)) == 0:
            continue
        # All characters to lower case
        words.append(word.lower())
    return words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    # If an NP tree has N or DP NP as children, it is the smallest noun phrase
    noun_phrases = list()
    for s in tree.subtrees(lambda t: t.label() == 'NP'):
        # s.label() == 'NP'. (child of s) .label() == 'NP' and (child (child of s)) .label() == 'N'
        try:
            if s[0].label() == 'N':
                noun_phrases.append(s)
            elif s[0].label() == 'DP':
                if s[1].label() == 'NP':
                    noun_phrases.append(s)
        except IndexError:
            pass

    return remove_duplicates(noun_phrases)


def remove_duplicates(noun_phrases):
    """ Removes the smaller noun phrase tree if a super-tree contains this. """
    remove_trees = list()
    for noun_tree_1 in noun_phrases:
        for noun_tree_2 in noun_phrases:
            if noun_tree_1 == noun_tree_2:
                continue
            # If noun_tree_1 contains noun_tree_2, remove noun_tree_2
            if noun_tree_2 in noun_tree_1.subtrees(lambda t: t.label() == noun_tree_2.label()):
                remove_trees.append(noun_tree_2)

    for remove_tree in remove_trees:
        try:
            noun_phrases.remove(remove_tree)
        except ValueError:
            pass

    return noun_phrases


if __name__ == "__main__":
    main()
