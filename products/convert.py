import re

CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ',
                'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ',
                'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']

JONGSUNG_LIST = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ',
                'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']


def korean_to_englished_string(korean_word):
    r_lst = ''
    for w in list(korean_word.strip()):
        if '가' <= w <= '힣':
            ch1 = (ord(w) - ord('가')) // 588
            ch2 = ((ord(w) - ord('가')) - (588 * ch1)) // 28
            ch3 = (ord(w) - ord('가')) - (588 * ch1) - 28 * ch2
            r_lst += ''.join([CHOSUNG_LIST[ch1], JUNGSUNG_LIST[ch2], JONGSUNG_LIST[ch3]])
        else:
            r_lst += w
    return r_lst

def key_mapping(string):
    mapping = {
        "Q": "ㅃ", "q": "ㅂ", "W": "ㅉ", "w": "ㅈ", "E": "ㄸ", "e": "ㄷ", "R": "ㄲ", "r": "ㄱ", "T": "ㅆ",
        "t": "ㅅ", "Y": "ㅛ", "y": "y", "U": "ㅕ", "u": "ㅕ", "I": "i", "i": "ㅑ", "O": "ㅒ", "o": "ㅐ",
        "P": "ㅖ", "p": "ㅔ", "A": "ㅁ", "a": "ㅁ", "S": "ㄴ", "s": "ㄴ", "D": "ㅇ", "d": "ㅇ", "F": "ㄹ",
        "f": "ㄹ", "G": "ㅎ", "g": "ㅎ", "H": "ㅗ", "h": "ㅗ", "J": "ㅓ", "j": "ㅓ", "K": "ㅏ", "k": "ㅏ",
        "L": "ㅣ", "l": "ㅣ", "Z": "ㅋ", "z": "z", "X": "ㅌ", "x": "ㅌ", "C": "ㅊ", "c": "ㅊ", "V": "ㅍ",
        "v": "ㅍ", "B": "ㅠ", "b": "ㅠ", "N": "ㅜ", "n": "ㅜ", "M": "ㅡ", "m": "ㅡ"
    }
    return mapping[string]

def word_to_mapping(client_words):
    mapping_result = ''
    regex_alpha = re.compile('[a-zA-Z]+')
    for word in client_words:
        if regex_alpha.match(word):
            mapping_result += key_mapping(word)
        else:
            pass
    return mapping_result