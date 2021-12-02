''' LeIA - Léxico para Inferência Adaptada
https://github.com/rafjaa/LeIA

Este projeto é um fork do léxico e ferramenta para análise de 
sentimentos VADER (Valence Aware Dictionary and sEntiment Reasoner) 
adaptado para textos em português.

Autor do VADER: C.J. Hutto
Repositório: https://github.com/cjhutto/vaderSentiment

'''

import re
import math
import unicodedata
from itertools import product
import os

PACKAGE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Empirically derived mean sentiment intensity rating increase for booster words
# TODO: Portuguese update
B_INCR = 0.293
B_DECR = -0.293

# Empirically derived mean sentiment intensity rating increase for using ALLCAPs to emphasize a word
# TODO: Portuguese update
C_INCR = 0.733
N_SCALAR = -0.74

# For removing punctuation
REGEX_REMOVE_PUNCTUATION = re.compile('[%s]' % re.escape('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'))

PUNC_LIST = [
    ".", "!", "?", ",", ";", ":", "-", "'", "\"", "...",
    "—", "–", "!?", "?!", "!!", "!!!", "??", "???", "?!?", 
    "!?!", "?!?!", "!?!?"
]

# Negations (Portuguese)
NEGATE = [t.strip() for t in open(
    os.path.join(PACKAGE_DIRECTORY, 'lexicons', 'negate.txt')
)]

# Booster/dampener 'intensifiers' or 'degree adverbs' (Portuguese)
boosters = []
for boost in open(os.path.join(PACKAGE_DIRECTORY, 'lexicons', 'booster.txt')):
    parts = boost.strip().split(' ')
    boosters.append([' '.join(parts[:-1]), parts[-1]])

BOOSTER_DICT = {}
for t, v in boosters: 
    BOOSTER_DICT[t] = B_INCR if v == 'INCR' else B_DECR


# Check for special case idioms containing lexicon words
# TODO: Portuguese
SPECIAL_CASE_IDIOMS = {}


def negated(input_words, include_nt=True):
    """
    Determine if input contains negation words
    """
    input_words = [str(w).lower() for w in input_words]
    neg_words = []
    neg_words.extend(NEGATE)
    for word in neg_words:
        if word in input_words:
            return True
    # if include_nt:
    #     for word in input_words:
    #         if "n't" in word:
    #             return True
    return False


def normalize(score, alpha=15):
    """
    Normalize the score to be between -1 and 1 using an alpha that
    approximates the max expected value
    """
    norm_score = score / math.sqrt((score * score) + alpha)
    if norm_score < -1.0:
        return -1.0
    elif norm_score > 1.0:
        return 1.0
    else:
        return norm_score


def allcap_differential(words):
    """
    Check whether just some words in the input are ALL CAPS
    :param list words: The words to inspect
    :returns: `True` if some but not all items in `words` are ALL CAPS
    """
    is_different = False
    allcap_words = 0
    for word in words:
        if word.isupper():
            allcap_words += 1
    cap_differential = len(words) - allcap_words
    if 0 < cap_differential < len(words):
        is_different = True
    return is_different


def scalar_inc_dec(word, valence, is_cap_diff):
    """
    Check if the preceding words increase, decrease, or negate/nullify the
    valence
    """
    scalar = 0.0
    word_lower = word.lower()
    if word_lower in BOOSTER_DICT:
        scalar = BOOSTER_DICT[word_lower]
        if valence < 0:
            scalar *= -1
        
        # Check if booster/dampener word is in ALLCAPS (while others aren't)
        if word.isupper() and is_cap_diff:
            if valence > 0:
                scalar += C_INCR
            else:
                scalar -= C_INCR
    return scalar


class SentiText(object):
    """
    Identify sentiment-relevant string-level properties of input text.
    """

    def __init__(self, text):
        if not isinstance(text, str):
            text = str(text).encode('utf-8')
        self.text = text
        self.words_and_emoticons = self._words_and_emoticons()
        
        # Doesn't separate words from adjacent
        # punctuation (keeps emoticons & contractions)
        self.is_cap_diff = allcap_differential(self.words_and_emoticons)


    def _words_plus_punc(self):
        """
        Returns mapping of form:
        {
            'cat,': 'cat',
            ',cat': 'cat',
        }
        """
        no_punc_text = REGEX_REMOVE_PUNCTUATION.sub('', self.text)
        
        # Removes punctuation (but loses emoticons & contractions)
        words_only = no_punc_text.split()
        
        # Remove singletons
        words_only = set(w for w in words_only if len(w) > 1)
        
        # The product gives ('cat', ',') and (',', 'cat')
        punc_before = {''.join(p): p[1] for p in product(PUNC_LIST, words_only)}
        punc_after = {''.join(p): p[0] for p in product(words_only, PUNC_LIST)}
        words_punc_dict = punc_before
        words_punc_dict.update(punc_after)

        return words_punc_dict


    def _words_and_emoticons(self):
        """
        Removes leading and trailing puncutation
        Leaves contractions and most emoticons
            Does not preserve punc-plus-letter emoticons (e.g. :D)
        """
        wes = self.text.split()
        words_punc_dict = self._words_plus_punc()
        wes = [we for we in wes if len(we) > 1]
        for i, we in enumerate(wes):
            if we in words_punc_dict:
                wes[i] = words_punc_dict[we]
        return wes


class SentimentIntensityAnalyzer(object):
    """
    Give a sentiment intensity score to sentences.
    """

    def __init__(
            self,
            lexicon_file=os.path.join(
                PACKAGE_DIRECTORY,
                'lexicons',
                'vader_lexicon_ptbr.txt'
            ),
            emoji_lexicon=os.path.join(
                PACKAGE_DIRECTORY,
                'lexicons',
                'emoji_utf8_lexicon_ptbr.txt'
            )
    ):
        with open(lexicon_file, encoding='utf-8') as f:
            self.lexicon_full_filepath = f.read()
        self.lexicon = self.make_lex_dict()

        with open(emoji_lexicon, encoding='utf-8') as f:
            self.emoji_full_filepath = f.read()
        self.emojis = self.make_emoji_dict()


    def make_lex_dict(self):
        """
        Convert lexicon file to a dictionary
        """
        lex_dict = {}
        for line in self.lexicon_full_filepath.split('\n'):
            if len(line) < 1:
                continue
            (word, measure) = line.strip().split('\t')[0:2]
            lex_dict[word] = float(measure)
        return lex_dict


    def make_emoji_dict(self):
        """
        Convert emoji lexicon file to a dictionary
        """
        emoji_dict = {}
        for line in self.emoji_full_filepath.split('\n'):
            if len(line) < 1:
                continue
            (emoji, description) = line.strip().split('\t')[0:2]
            emoji_dict[emoji] = description
        return emoji_dict


    def polarity_scores(self, text):
        """
        Return a float for sentiment strength based on the input text.
        Positive values are positive valence, negative value are negative
        valence.
        """

        # Remove acentos
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')

        # convert emojis to their textual descriptions
        text_token_list = text.split()
        text_no_emoji_lst = []
        for token in text_token_list:
            if token in self.emojis:
                # get the textual description
                description = self.emojis[token]
                text_no_emoji_lst.append(description)
            else:
                text_no_emoji_lst.append(token)
        text = " ".join(x for x in text_no_emoji_lst)

        sentitext = SentiText(text)

        sentiments = []
        words_and_emoticons = sentitext.words_and_emoticons
        for item in words_and_emoticons:
            valence = 0
            i = words_and_emoticons.index(item)
            # check for vader_lexicon words that may be used as modifiers or negations
            if item.lower() in BOOSTER_DICT:
                sentiments.append(valence)
                continue

            sentiments = self.sentiment_valence(valence, sentitext, item, i, sentiments)

        sentiments = self._but_check(words_and_emoticons, sentiments)
        valence_dict = self.score_valence(sentiments, text)

        return valence_dict


    def sentiment_valence(self, valence, sentitext, item, i, sentiments):
        is_cap_diff = sentitext.is_cap_diff
        words_and_emoticons = sentitext.words_and_emoticons
        item_lowercase = item.lower()
        if item_lowercase in self.lexicon:

            # Get the sentiment valence
            valence = self.lexicon[item_lowercase]

            # Check if sentiment laden word is in ALL CAPS (while others aren't)
            if item.isupper() and is_cap_diff:
                if valence > 0:
                    valence += C_INCR
                else:
                    valence -= C_INCR

            for start_i in range(0, 3):
                # Dampen the scalar modifier of preceding words and emoticons
                # (excluding the ones that immediately preceed the item) based
                # on their distance from the current item.
                if i > start_i and words_and_emoticons[i - (start_i + 1)].lower() not in self.lexicon:
                    s = scalar_inc_dec(words_and_emoticons[i - (start_i + 1)], valence, is_cap_diff)
                    if start_i == 1 and s != 0:
                        s = s * 0.95
                    if start_i == 2 and s != 0:
                        s = s * 0.9
                    valence = valence + s
                    valence = self._negation_check(valence, words_and_emoticons, start_i, i)
                    if start_i == 2:
                        valence = self._special_idioms_check(valence, words_and_emoticons, i)

            # valence = self._least_check(valence, words_and_emoticons, i)
        sentiments.append(valence)

        return sentiments


    # TODO: Portuguese
    # def _least_check(self, valence, words_and_emoticons, i):
    #     # check for negation case using "least"
    #     if i > 1 and words_and_emoticons[i - 1].lower() not in self.lexicon \
    #             and words_and_emoticons[i - 1].lower() == "least":
    #         if words_and_emoticons[i - 2].lower() != "at" and words_and_emoticons[i - 2].lower() != "very":
    #             valence = valence * N_SCALAR
    #     elif i > 0 and words_and_emoticons[i - 1].lower() not in self.lexicon \
    #             and words_and_emoticons[i - 1].lower() == "least":
    #         valence = valence * N_SCALAR
    #     return valence


    @staticmethod
    def _but_check(words_and_emoticons, sentiments):
        # Check for modification in sentiment due to contrastive conjunction 'but'
        words_and_emoticons_lower = [str(w).lower() for w in words_and_emoticons]

        for mas in ['mas', 'entretanto', 'todavia', 'porem', 'porém']:
            if mas in words_and_emoticons_lower:
                bi = words_and_emoticons_lower.index(mas)
                for sentiment in sentiments:
                    si = sentiments.index(sentiment)
                    if si < bi:
                        sentiments.pop(si)
                        sentiments.insert(si, sentiment * 0.5)
                    elif si > bi:
                        sentiments.pop(si)
                        sentiments.insert(si, sentiment * 1.5)
            return sentiments


    @staticmethod
    def _special_idioms_check(valence, words_and_emoticons, i):
        words_and_emoticons_lower = [str(w).lower() for w in words_and_emoticons]
        onezero = "{0} {1}".format(
            words_and_emoticons_lower[i - 1], 
            words_and_emoticons_lower[i]
        )

        twoonezero = "{0} {1} {2}".format(
            words_and_emoticons_lower[i - 2],
            words_and_emoticons_lower[i - 1], 
            words_and_emoticons_lower[i]
        )

        twoone = "{0} {1}".format(
            words_and_emoticons_lower[i - 2], 
            words_and_emoticons_lower[i - 1]
        )

        threetwoone = "{0} {1} {2}".format(
            words_and_emoticons_lower[i - 3],
            words_and_emoticons_lower[i - 2], 
            words_and_emoticons_lower[i - 1]
        )

        threetwo = "{0} {1}".format(
            words_and_emoticons_lower[i - 3], 
            words_and_emoticons_lower[i - 2]
        )

        sequences = [onezero, twoonezero, twoone, threetwoone, threetwo]

        for seq in sequences:
            if seq in SPECIAL_CASE_IDIOMS:
                valence = SPECIAL_CASE_IDIOMS[seq]
                break

        if len(words_and_emoticons_lower) - 1 > i:
            zeroone = "{0} {1}".format(
                words_and_emoticons_lower[i], 
                words_and_emoticons_lower[i + 1]
            )
            if zeroone in SPECIAL_CASE_IDIOMS:
                valence = SPECIAL_CASE_IDIOMS[zeroone]

        if len(words_and_emoticons_lower) - 1 > i + 1:
            zeroonetwo = "{0} {1} {2}".format(
                words_and_emoticons_lower[i], 
                words_and_emoticons_lower[i + 1],
                words_and_emoticons_lower[i + 2]
                )
            if zeroonetwo in SPECIAL_CASE_IDIOMS:
                valence = SPECIAL_CASE_IDIOMS[zeroonetwo]

        # Check for booster/dampener bi-grams such as 'sort of' or 'kind of'
        n_grams = [threetwoone, threetwo, twoone]
        for n_gram in n_grams:
            if n_gram in BOOSTER_DICT:
                valence = valence + BOOSTER_DICT[n_gram]

        return valence


    @staticmethod
    def _negation_check(valence, words_and_emoticons, start_i, i):
        words_and_emoticons_lower = [str(w).lower() for w in words_and_emoticons]
        if start_i == 0:
            if negated([words_and_emoticons_lower[i - (start_i + 1)]]):  # 1 word preceding lexicon word (w/o stopwords)
                valence = valence * N_SCALAR
        if start_i == 1:
            if words_and_emoticons_lower[i - 2] == "nunca" and \
                    (words_and_emoticons_lower[i - 1] == "entao" or
                     words_and_emoticons_lower[i - 1] == "este"):
                valence = valence * 1.25
            elif words_and_emoticons_lower[i - 2] == "sem" and \
                    words_and_emoticons_lower[i - 1] == "dúvida":
                valence = valence
            elif negated([words_and_emoticons_lower[i - (start_i + 1)]]):  # 2 words preceding the lexicon word position
                valence = valence * N_SCALAR
        if start_i == 2:
            if words_and_emoticons_lower[i - 3] == "nunca" and \
                    (words_and_emoticons_lower[i - 2] == "entao" or words_and_emoticons_lower[i - 2] == "este") or \
                    (words_and_emoticons_lower[i - 1] == "entao" or words_and_emoticons_lower[i - 1] == "este"):
                valence = valence * 1.25
            elif words_and_emoticons_lower[i - 3] == "sem" and \
                    (words_and_emoticons_lower[i - 2] == "dúvida" or words_and_emoticons_lower[i - 1] == "dúvida"):
                valence = valence
            elif negated([words_and_emoticons_lower[i - (start_i + 1)]]):  # 3 words preceding the lexicon word position
                valence = valence * N_SCALAR
        return valence

    def _punctuation_emphasis(self, text):
        # Add emphasis from exclamation points and question marks
        ep_amplifier = self._amplify_ep(text)
        qm_amplifier = self._amplify_qm(text)
        punct_emph_amplifier = ep_amplifier + qm_amplifier

        return punct_emph_amplifier


    @staticmethod
    def _amplify_ep(text):
        # Check for added emphasis resulting from exclamation points (up to 4 of them)
        ep_count = text.count("!")
        if ep_count > 4:
            ep_count = 4
        # Empirically derived mean sentiment intensity rating increase for
        # exclamation points
        ep_amplifier = ep_count * 0.292

        return ep_amplifier


    @staticmethod
    def _amplify_qm(text):
        # Check for added emphasis resulting from question marks (2 or 3+)
        qm_count = text.count("?")
        qm_amplifier = 0
        if qm_count > 1:
            if qm_count <= 3:
                # Empirically derived mean sentiment intensity rating increase for
                # question marks
                qm_amplifier = qm_count * 0.18
            else:
                qm_amplifier = 0.96

        return qm_amplifier


    @staticmethod
    def _sift_sentiment_scores(sentiments):
        # Want separate positive versus negative sentiment scores
        pos_sum = 0.0
        neg_sum = 0.0
        neu_count = 0
        for sentiment_score in sentiments:
            if sentiment_score > 0:
                pos_sum += (float(sentiment_score) + 1)  # compensates for neutral words that are counted as 1
            if sentiment_score < 0:
                neg_sum += (float(sentiment_score) - 1)  # when used with math.fabs(), compensates for neutrals
            if sentiment_score == 0:
                neu_count += 1

        return pos_sum, neg_sum, neu_count


    def score_valence(self, sentiments, text):
        if sentiments:
            sum_s = float(sum(sentiments))
            # Compute and add emphasis from punctuation in text
            punct_emph_amplifier = self._punctuation_emphasis(text)
            if sum_s > 0:
                sum_s += punct_emph_amplifier
            elif sum_s < 0:
                sum_s -= punct_emph_amplifier

            compound = normalize(sum_s)
            # Discriminate between positive, negative and neutral sentiment scores
            pos_sum, neg_sum, neu_count = self._sift_sentiment_scores(sentiments)

            if pos_sum > math.fabs(neg_sum):
                pos_sum += punct_emph_amplifier
            elif pos_sum < math.fabs(neg_sum):
                neg_sum -= punct_emph_amplifier

            total = pos_sum + math.fabs(neg_sum) + neu_count
            pos = math.fabs(pos_sum / total)
            neg = math.fabs(neg_sum / total)
            neu = math.fabs(neu_count / total)

        else:
            compound = 0.0
            pos = 0.0
            neg = 0.0
            neu = 0.0

        sentiment_dict = {
            'neg': round(neg, 3),
            'neu': round(neu, 3),
            'pos': round(pos, 3),
            'compound': round(compound, 4)
        }

        return sentiment_dict


if __name__ == '__main__':
    pass

    # TODO: tests and examples (Portuguese)
