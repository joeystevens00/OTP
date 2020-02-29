#-*-coding:utf8;-*-
#qpy:3
#qpy:console
import secrets
import string
import sys
VERSION = 0.11

letters = string.ascii_letters
numbers = string.digits
symbols = string.punctuation
ascii_chars = ''.join(chr(x) for x in range(128))
utf_chars = ''.join(chr(x) for x in range(0x110000-1))

def securegen(len, charset=letters):
    s = ""
    for i in range(len):
        s += secrets.choice(charset)
    return s

class VigenereCipher:
    def __init__(self, key, msg, mode='encrypt', charset=letters):
        self.key = key
        self.msg = msg
        mode = self.modedetect(mode)
        self.mode = mode
        self.charset = charset
        if mode == 'encrypt':
             self.translated = self.encrypt()
        else:
            self.translated = self.decrypt()
    @classmethod
    def modedetect(cls, mode):
        modes = { 'e':'encrypt','d':'decrypt'}
        parsed_mode = modes.get(mode.lower()[0])
        return parsed_mode
    @classmethod
    def translate_charset(cls, key, msg, mode, charset=letters):
        translated = []
        keyIndex = 0
        for symbol in msg:
            if isinstance(symbol, int) and isinstance(msg, bytes):
                num = symbol
            else:
                num = charset.find(symbol)
            if num != -1: # if not none found
                if mode == 'encrypt':
                    num += charset.find(key[keyIndex])
                elif mode == 'decrypt':
                    num -= charset.find(key[keyIndex])
                num %= len(charset) # Handle any wrap around
                translated.append(charset[num])
                keyIndex += 1
                if keyIndex == len(key):
                    keyIndex = 0
            else: # Character not in charset
                translated.append(symbol)
        return ''.join(translated)
    @classmethod
    def translate(cls, key, msg, mode):
        translated = []
        keyIndex = 0
        key = key.upper()
        for symbol in msg:
            num = letters.find(symbol.upper())
            if num != -1: # if not none found
                if mode == 'encrypt':
                    num += letters.find(key[keyIndex])
                elif mode == 'decrypt':
                    num -= letters.find(key[keyIndex])
                num %= len(letters)
                if symbol.isupper():
                    translated.append(letters[num])
                elif symbol.islower():
                    translated.append(letters[num].lower())
                keyIndex += 1
                if keyIndex == len(key):
                    keyIndex = 0
            else:
                translated.append(symbol)
        return ''.join(translated)
    def encrypt(self):
        return self.translate_charset(self.key, self.msg, self.mode, charset=self.charset)
    def decrypt(self):
        return self.translate_charset(self.key, self.msg, self.mode, charset=self.charset)

def otp(msg, key=None, encrypt=True, charset=letters):
    if key is None:
        key = securegen(len(msg), charset=charset)
    mode = 'e' if encrypt else 'd'

    #print(f'otp msg={msg}, key={key}, encrypt={encrypt}')
    return VigenereCipher(msg=msg, key=key, mode=mode, charset=charset).translated, key
