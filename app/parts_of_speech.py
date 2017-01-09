#!/usr/bin/env python

class PartsOfSpeech:
    NOUN = set(['名詞', '名詞接尾辞', '冠名詞', '英語接尾辞', '補助名詞',
            'Alphabet', 'Kana', 'Katakana', 'Kanji', 'Roman', 'Undef',
            '括弧', '句点', '読点', '空白', 'Symbol'])
    VERB = set(['動詞語幹', '動詞活用語尾', '動詞接尾辞', '冠動詞', '判定詞'])
    ADJECTIVE = set(['形容詞語幹', '形容詞接尾辞', '冠形容詞'])
    PRENOMINAL = set(['連体詞'])
    ADVERB = set(['連用詞'])
    CONJECTION = set(['接続詞'])
    EXCLAMATION = set(['独立詞'])
    SUFFIX = set(['接続接尾辞'])
    PARTICLE = set(['格助詞', '引用助詞', '連用助詞', '終助詞', '間投詞', '助数詞', '助助数詞', '冠数詞'])
    # SYMBOL = ['括弧', '句点', '読点', '空白', 'Symbol']
    NUMBER = set(['Year', 'Month', 'Day', 'YearMonth', 'MonthDay',
              'Hour', 'Minute', 'Second', 'HourMinute', 'MinuteSecond',
              'PreHour', 'PostHour', 'Number'])
    ALL_MORPHS = [NOUN, VERB, ADJECTIVE, PRENOMINAL, ADVERB, CONJECTION,
           EXCLAMATION, SUFFIX, PARTICLE, NUMBER]

    @classmethod
    def parts_of_speech(cls, morphs):
        '''
        品詞のリストからひとつの品詞を特定
        '''
        morphs_set = set(morphs)
        for i, parts_of_speech_set in enumerate(cls.ALL_MORPHS):
            if morphs_set & parts_of_speech_set == morphs_set:
                return i
        return -1
