import io, math, re, sys

# A simple tokenizer. Applies case folding
def tokenize(s):
    tokens = s.lower().split()
    trimmed_tokens = []
    for t in tokens:
        if re.search('\w', t):
            # t contains at least 1 alphanumeric character
            t = re.sub('^\W*', '', t) # trim leading non-alphanumeric chars
            t = re.sub('\W*$', '', t) # trim trailing non-alphanumeric chars
        trimmed_tokens.append(t)
    return trimmed_tokens

# Find the most similar response in terms of token overlap.
def most_sim_overlap(query, responses):
    q_tokenized = tokenize(query)
    max_sim = 0
    max_resp = "Sorry, I don't understand"
    for r in responses:
        r_tokenized = tokenize(r)
        sim = len(set(r_tokenized).intersection(q_tokenized))
        if sim > max_sim:
            max_sim = sim
            max_resp = r
    return max_resp

def w2v_implementation(query, dict_responses, word_vectors):
    q_tokenized = tokenize(query)
    query_val = {}
    list_querValues = []
    dict_cosine_response = {}
    denum1 = 0
    denum2 = 0
    size = len (q_tokenized)
    max_resp = "Sorry, I don't understand"
    for query_word in q_tokenized:
        if query_word in word_vectors:
            list_querValues.append(word_vectors.get(query_word))
    query_val[query] =  [sum(x)/size for x in zip(*list_querValues)]
    for response in dict_responses:
        if len(dict_responses.get(response))!=0:
            num = 0
            query_square = 0
            response_square = 0
            for i in range(0,len(query_val[query])):
                num += query_val.get(query)[i] * dict_responses.get(response)[i]
                query_square += query_val.get(query)[i] * query_val.get(query)[i]
                response_square += dict_responses.get(response)[i] * dict_responses.get(response)[i]
            denum1 = math.sqrt(query_square)
            denum2 = math.sqrt(response_square)
            if denum1 == 0 or denum2 == 0:
                return max_resp
            dict_cosine_response[response] = num/(denum1*denum2)
    return str([key for key in dict_cosine_response if dict_cosine_response[key] == max(dict_cosine_response.values())]).strip("['']")
    
# Code for loading the fasttext (word2vec) vectors from here (lightly
# modified): https://fasttext.cc/docs/en/crawl-vectors.html
def load_vectors(fname):
    fin = io.open(fname, 'r', encoding='utf-8', newline='\n', errors='ignore')
    data = {}
    for line in fin:
        tokens = line.rstrip().split(' ')
        data[tokens[0]] = list(map(float, tokens[1:]))
    return data

if __name__ == '__main__':
    # Method will be one of 'overlap' or 'w2v'
    method = sys.argv[1]
    responses_fname = 'gutenberg.txt'
    vectors_fname = 'cc.en.300.vec.10k'

    responses = [x.strip() for x in open(responses_fname)]
    dict_responses = {}
    list_respValues = []
    dict_denominator = {}
    # Only do the initialization for the w2v method if we're using it
    if method == 'w2v':
        print("Loading vectors...")
        word_vectors = load_vectors(vectors_fname)
        for response in responses:
            tokens = tokenize(response)
            size = len(tokens)
            for token in tokens:
                if token in word_vectors:
                    num = 0
                    if token not in dict_denominator:
                        for index in range(0,len(word_vectors.get(token))):
                            num += word_vectors.get(token)[index] * word_vectors.get(token)[index]
                        dict_denominator[token] = math.sqrt(num)
                        for index in range(0,len(word_vectors.get(token))):
                            word_vectors[token][index] = word_vectors.get(token)[index]/dict_denominator.get(token)
                    list_respValues.append(word_vectors.get(token))
            dict_responses[response] =  [sum(x)/size for x in zip(*list_respValues)]
            list_respValues = []
    
    print ("Hi, Let's chattttt!!!!")
    while True:
        query = input()
        if method == 'overlap':
            response = most_sim_overlap(query, responses)
        elif method == 'w2v':
            response = w2v_implementation(query, dict_responses, word_vectors)

        print(response)
