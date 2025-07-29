# RAKE short for Rapid Automatic Keyword Extraction algorithm
# from rake_nltk import Rake

# # Uses stopwords for english from NLTK, and all puntuation characters by
# # default
# r = Rake()

# text_str = "how hydrogen can reduce stress"
# text_list = [
#     "how hydrogen can reduce stress",
#     "effect of hydrogen in daily lifestyle",
#     "benefit of hydrogen"
# ]

# # Extraction given the text.
# r.extract_keywords_from_text(text_str)

# # Extraction given the list of strings where each string is a sentence.
# r.extract_keywords_from_sentences(text_list)

# # To get keyword phrases ranked highest to lowest.
# r.get_ranked_phrases()

# # To get keyword phrases ranked highest to lowest with scores.
# r.get_ranked_phrases_with_scores()


import spacy

def extract_keywords_spacy(sentence):
    # Load the English language model
    nlp = spacy.load("en_core_web_sm")
    # nlp_download_path = nlp._path
    # print(nlp_download_path)
    #
    doc = nlp(sentence)
    keywords = [token.text for token in doc if not token.is_stop and not token.is_punct]
    keyword_string = " ".join(keywords)
    return keyword_string

if __name__ == "__main__":
    sentence = "DeepSeek AI is an advanced artificial intelligence platform"
    # Output: ['DeepSeek', 'AI', 'advanced', 'artificial', 'intelligence', 'platform']

    sentence = 'how hydrogen can reduce stress'
    # Output: ['hydrogen', 'reduce', 'stress']

    print(extract_keywords_spacy(sentence))