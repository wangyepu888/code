import re

class SentenceReadingAgent:
    def __init__(self):
        self.names = {
            "serena", "andrew", "bobbie", "cason", "david", "farzana", "frank",
            "hannah", "ida", "irene", "jim", "jose", "keith", "laura", "lucy",
            "meredith", "nick", "ada", "yeeling", "yan"
        }
  
        try:
            with open('mostcommon.txt', 'r') as f:
                self.common_words = set(line.strip().lower() for line in f)
        except FileNotFoundError:
            self.common_words = set()
        self.location_prepositions = {
            "in", "on", "at", "by", "with", "from", "under", "above",
            "over", "to", "of", "for"
        }
        self.time_pattern = re.compile(
            r"\b\d{1,2}:\d{2}(?:am|pm)?\b", re.IGNORECASE
        )
        self.people_nouns = {
            'man', 'men', 'woman', 'women', 'child', 'children',
            'person', 'people', 'adult', 'adults', 'friend', 'friends',
            'him', 'her', 'them', 'us', 'she', 'he'
        }

    def solve(self, sentence, question):
        sentence_words = self.tokenize(sentence)
        question_words = self.tokenize(question)
        question_text = ' '.join(question_words)

        # Map complex question phrases to types
        if 'what time' in question_text or 'at what time' in question_text:
            return self.answer_when(sentence_words, sentence, question_words)
        if any(
            phrase in question_text
            for phrase in ['how far', 'how long', 'how big', 'how do', 'how many']
        ):
            return self.answer_how(sentence_words, sentence, question_words)
        if 'what is my' in question_text and 'name' in question_text:
            return self.answer_what(
                sentence_words, sentence, question_words, special_case='name'
            )
        if 'what' in question_words and any(
            prop in question_words for prop in ['animal', 'color', 'size', 'shape']
        ):
            return self.answer_what(
                sentence_words, sentence, question_words, special_case='adjective_noun'
            )

        question_types = {
            "who": self.answer_who,
            "what": self.answer_what,
            "where": self.answer_where,
            "when": self.answer_when,
            "how": self.answer_how,
        }

        for q_type, handler in question_types.items():
            if q_type in question_words:
                return handler(sentence_words, sentence, question_words)
        return "No answer found"

    def tokenize(self, text):
        return [word.strip(",.?!").lower() for word in text.split()]

    def answer_who(self, sentence_words, sentence, question_words):
        if question_words[0] == 'who':
            if 'did' in question_words:

                prepositions = {'to', 'for'}
                for i, word in enumerate(sentence_words):
                    if word in prepositions and i + 1 < len(sentence_words):
                        next_word = sentence_words[i + 1]
                        if next_word in self.names or next_word in self.people_nouns:
                            return next_word
            else:
        
                if sentence_words[0] in {'he', 'she', 'they', 'we', 'i', 'you'}:
                    return sentence_words[0]
                else:

                    for word in sentence_words:
                        if word in self.names or word in self.people_nouns:
                            return word
        return "No answer found"

    def answer_what(self, sentence_words, sentence, question_words, special_case=None):
        articles = {'the', 'a', 'an'}
        if 'made' in sentence_words and 'of' in sentence_words:
            of_index = sentence_words.index('of')
            if of_index + 1 < len(sentence_words):
                return sentence_words[of_index + 1]
        elif special_case == 'name':
 
            pass
        elif special_case == 'adjective_noun':
            if 'is' in question_words:
                adj_index = question_words.index('is') + 1
            elif 'was' in question_words:
                adj_index = question_words.index('was') + 1
            else:
                adj_index = None
            if adj_index and adj_index < len(question_words):
                adjective = question_words[adj_index]
                for i, word in enumerate(sentence_words):
                    if word == adjective:
                 
                        if i + 1 < len(sentence_words):
                            return sentence_words[i + 1]
                        elif i > 0:
                            return sentence_words[i - 1]
        elif 'will' in sentence_words:
            will_index = sentence_words.index('will')
            if will_index + 1 < len(sentence_words):
                verb = sentence_words[will_index + 1]
                j = will_index + 2

                while j < len(sentence_words) and sentence_words[j] in {
                    'me', 'you', 'him', 'her', 'us', 'them'
                }:
                    j += 1
        
                object_words = []
                prepositions = self.location_prepositions
                time_indicators = {
                    'last', 'yesterday', 'today', 'tomorrow', 'tonight', 'morning',
                    'afternoon', 'evening', 'night', 'now'
                }
                stop_words = prepositions.union(time_indicators)
                while j < len(sentence_words) and sentence_words[j] not in stop_words:
                    object_words.append(sentence_words[j])
                    j += 1
                if object_words:
            
                    while object_words and object_words[0] in articles:
                        object_words.pop(0)
                    return ' '.join(object_words)
        else:
     
            verbs_with_indirect_objects = {
                'give', 'gave', 'send', 'sent', 'tell', 'told', 'bring', 'brought',
                'show', 'write', 'wrote', 'read', 'hand', 'handed'
            }
            for i, word in enumerate(sentence_words):
                if word in verbs_with_indirect_objects:
                    j = i + 1
         
                    while j < len(sentence_words) and sentence_words[j] in {
                        'me', 'you', 'him', 'her', 'us', 'them', 'my', 'your',
                        'his', 'her', 'their', 'our', 'friend', 'friends'
                    }:
                        j += 1
       
                    object_words = []
                    prepositions = self.location_prepositions.union({
                        'to', 'for', 'with', 'by', 'on', 'in', 'at'
                    })
                    while j < len(sentence_words) and sentence_words[j] not in prepositions:
                        object_words.append(sentence_words[j])
                        j += 1
                    if object_words:
               
                        while object_words and object_words[0] in articles:
                            object_words.pop(0)
                        return ' '.join(object_words)
         
            verbs = {
                'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                'do', 'does', 'did', 'can', 'could', 'will', 'would', 'shall', 'should',
                'may', 'might', 'must', 'bring', 'brought', 'watch', 'walk', 'go', 'give',
                'made', 'make', 'come', 'came', 'give', 'gave', 'get', 'got', 'see', 'saw',
                'know', 'knew', 'sing', 'play', 'run', 'ran', 'write', 'wrote', 'read'
            }
            prepositions = self.location_prepositions.union({
                'to', 'for', 'with', 'by', 'on', 'in', 'at'
            })
            time_indicators = {
                'last', 'yesterday', 'today', 'tomorrow', 'tonight', 'morning',
                'afternoon', 'evening', 'night', 'now', 'soon', 'later', 'immediately'
            }
            stop_words = prepositions.union(time_indicators)
            for i, word in enumerate(sentence_words):
                if word in verbs:
                    j = i + 1
               
                    while j < len(sentence_words) and sentence_words[j] in articles:
                        j += 1
                    object_words = []
                    while j < len(sentence_words) and sentence_words[j] not in stop_words:
                        object_words.append(sentence_words[j])
                        j += 1
                    if object_words:
                
                        while object_words and object_words[0] in articles:
                            object_words.pop(0)
                        return ' '.join(object_words)
        return "No answer found"

    def answer_how(self, sentence_words, sentence, question_words):
        question_text = ' '.join(question_words)
        if "how many" in question_text:
            number_words = {
                'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
                'nine', 'ten', 'eleven', 'twelve', 'hundred', 'thousand',
                'million', 'billion'
            }
            for i, word in enumerate(sentence_words):
                if word in number_words:
                    number_phrase = word
                    # Check for multi-word numbers
                    while i + 1 < len(sentence_words) and sentence_words[i + 1] in number_words:
                        i += 1
                        number_phrase += ' ' + sentence_words[i]
                    return number_phrase
                elif word.isdigit():
                    return word
        elif "how far" in question_text:
            number_words = {
                'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight',
                'nine', 'ten', 'eleven', 'twelve', 'hundred', 'thousand', 'million'
            }
            for i, word in enumerate(sentence_words):
                if word in number_words:
                    if i + 1 < len(sentence_words):
                        return word + ' ' + sentence_words[i + 1]
                    else:
                        return word
        elif "how long" in question_text:
            for word in sentence_words:
                if word in {"short", "long"}:
                    return word
        elif "how big" in question_text:
            size_adjectives = {
                'big', 'small', 'large', 'huge', 'tiny', 'very large'
            }
            for i, word in enumerate(sentence_words):
                if word in size_adjectives:
                    return word
                elif word == 'very' and i + 1 < len(sentence_words) and sentence_words[
                    i + 1
                ] in size_adjectives:
                    return 'very ' + sentence_words[i + 1]
        elif question_words[0] == 'how' and 'do' in question_words:
            verbs = {'walk', 'run', 'drive', 'fly', 'sail', 'ride', 'swim'}
            for word in sentence_words:
                if word in verbs:
                    return word
        return "No answer found"

    def answer_where(self, sentence_words, sentence, question_words):
        location_prepositions = self.location_prepositions.union({
            'to', 'of', 'east', 'west', 'north', 'south'
        })
        articles = {'the', 'a', 'an', 'this', 'that', 'these', 'those'}
        stop_words = {
            'every', 'when', 'at', 'if', 'and', 'but', 'that', 'there',
            'is', 'was', 'were', 'are', 'go', 'to'
        }
        for i, word in enumerate(sentence_words):
            if word in location_prepositions:
                location_words = []
                j = i + 1
                while j < len(sentence_words) and sentence_words[j] not in stop_words:
                    if sentence_words[j] not in articles:
                        location_words.append(sentence_words[j])
                    j += 1
                if location_words:
                    return ' '.join(location_words)
        return "No answer found"

    def answer_when(self, sentence_words, sentence, question_words):
        time_match = self.time_pattern.search(sentence)
        if time_match:
            return time_match.group()
        time_expressions = {
            'today', 'tomorrow', 'yesterday', 'tonight', 'morning',
            'afternoon', 'evening', 'night', 'this morning', 'this afternoon',
            'this evening', 'last night', 'last year', 'this year', 'soon',
            'now', 'later', 'immediately'
        }
        sentence_lower = sentence.lower()
        for expr in time_expressions:
            if expr in sentence_lower:
                return expr
        return "No answer found"
