"""Made by N Purushotam Kumar (COMP A - AIT Pune) | github link : https://github.com/RealLegendiQ"""
""" A cascaded cryptography system based on an idea presented in a research paper.
Encryption/Decryption of text, image, audio and video file is being done using armstrong numbers and matrices,
also used multithreading while processing data to increase efficiency. """

import os
import threading
import abc


class KeyGenerator:
    ARMSTRONG_DIGITS = (1, 5, 3, 3, 7, 0, 3, 7, 1, 4, 0, 7)
    KEY_LENGTH = len(ARMSTRONG_DIGITS)

    def __init__(self, user_remark):
        self.numerickey = []
        sum = 0

        for k in user_remark:
            temp = ord(k)
            if temp not in self.numerickey:
                self.numerickey.append(temp)
            sum += temp

        if len(self.numerickey) < KeyGenerator.KEY_LENGTH:
            raise Exception('Weaker Key')

        self.numerickey = self.numerickey[:KeyGenerator.KEY_LENGTH]
        for x in range(KeyGenerator.KEY_LENGTH):
            self.numerickey[x] = (self.numerickey[x] + KeyGenerator.ARMSTRONG_DIGITS[x]) % 256

        self.numerickey.append(sum)

    def get_key(self):
        return self.numerickey


class ByteManager:
    @classmethod
    def byte_to_nibbles(cls, byte):
        lower_nibble = byte & 0xF
        higher_nibble = byte >> 4
        return (higher_nibble, lower_nibble)

    @classmethod
    def nibbles_to_byte(cls, nibbles):
        return (nibbles[0] << 4) | nibbles[1]


class Cryptography(abc.ABC):
    def __init__(self, user_remark):
        self.numericKey = KeyGenerator(user_remark).get_key()
        self.color_index = 0
        self.numericKey_index = 0
        self.color = self.makeColor()
        self.size = len(self.color)

    def makeColor(self):
        r = (sum(self.numericKey[:4]) + self.numericKey[-1]) % 256
        g = (sum(self.numericKey[4:8]) + self.numericKey[-1]) % 256
        b = (sum(self.numericKey[8:12]) + self.numericKey[-1]) % 256
        return r, g, b

    @abc.abstractmethod
    def process(self, data):
        pass


class Encryptor(Cryptography):
    def __init__(self, user_remark):
        Cryptography.__init__(self, user_remark)

    def process(self, data):
        # level1
        data = data ^ self.numericKey[self.numericKey_index]
        self.numericKey_index = (self.numericKey_index + 1) % KeyGenerator.KEY_LENGTH

        # level2
        row, col = ByteManager.byte_to_nibbles(data)
        encoded = (self.color[self.color_index] + row * 16 + col) % 256
        self.color_index = (self.color_index + 1) % self.size

        return encoded


class Decryptor(Cryptography):
    def __init__(self, user_remark):
        Cryptography.__init__(self, user_remark)

    def process(self, encoded):
        # level2
        temp = (encoded - self.color[self.color_index] + 256) % 256
        row = temp // 16
        col = temp % 16
        self.color_index = (self.color_index + 1) % self.size
        data = ByteManager.nibbles_to_byte((row, col))

        # level1
        data = data ^ self.numericKey[self.numericKey_index]
        self.numericKey_index = (self.numericKey_index + 1) % KeyGenerator.KEY_LENGTH
        return data


class ChunkProcessor:
    def __init__(self, src_file_name, trgt_file_name, start_pos, end_pos, objCrypto):
        # input data
        self.src_file_name = src_file_name
        self.trgt_file_name = trgt_file_name
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.objCrypto = objCrypto

        # a thread as a member of the class
        self.thrd = threading.Thread(target=self.process)
        # activate the thread
        self.thrd.start()

    def process(self):
        # open the source file for reading
        src_handle = open(self.src_file_name, 'rb')
        # open the target file for writing
        trgt_handle = open(self.trgt_file_name, 'wb')

        # ensure that chunk is read within the limits
        src_handle.seek(self.start_pos, 0)
        x = self.start_pos
        while x < self.end_pos:
            buff = int.from_bytes(src_handle.read(1), byteorder='big')
            buff = self.objCrypto.process(buff)
            trgt_handle.write(int.to_bytes(buff, length=1, byteorder='big'))
            x += 1

        # close
        trgt_handle.close()
        src_handle.close()


class FileProcessor:
    def __init__(self, src_file_name, trgt_file_name, action, user_key):
        if not os.path.exists(src_file_name):  # checks whether the file exists  or not
            raise Exception(src_file_name + ' doesnt exist!')
        self.src_file_name = src_file_name
        self.trgt_file_name = trgt_file_name
        self.action = action
        self.user_key = user_key

    def process(self):
        n = 8  # number of parts file is divided into
        # Dividing source file into n small continuous parts.
        chunks = self.divide_into_chunks(n)  # Lets refer to the divided parts as chunks
        cps = []
        for ch in chunks:
            if self.action == 'E':
                objE = Encryptor(self.user_key)
                cps.append(ChunkProcessor(self.src_file_name, ch[0], ch[1], ch[2], objE))
            elif self.action == 'D':
                objD = Decryptor(self.user_key)
                cps.append(ChunkProcessor(self.src_file_name, ch[0], ch[1], ch[2], objD))

        # suspend this thread until chunk processors are done
        for cp in cps:
            cp.thrd.join()

        # merge into the trgt_file_name
        trgt_handle = open(self.trgt_file_name, 'wb')
        for ch in chunks:
            ch_handle = open(ch[0], 'rb')
            while True:
                buff = ch_handle.read(2048)
                if not buff:
                    break
                trgt_handle.write(buff)
            ch_handle.close()

        trgt_handle.close()

        # delete the chunk files
        for ch in chunks:
            os.remove(ch[0])

    def divide_into_chunks(self, n):
        chunks = []

        # chunk boundaries
        src_file_size = os.path.getsize(
            self.src_file_name)  # returns size of file in bytes, raises FileNotFoundError if file doesnt exist.
        size_of_chunk = src_file_size // n
        end = 0

        # generate the names
        tup = os.path.splitext(self.src_file_name)  # returns a tuple of (parent_dir_file_name, file_ext)

        # n-1 chunks
        i = -1
        for i in range(n - 1):
            start = end
            end = start + size_of_chunk
            chunks.append((tup[0] + str(i) + tup[1], start, end))

        # nth chunk
        chunks.append((tup[0] + str(i + 1) + tup[1], end, src_file_size))
        return chunks


def main():
    src_file = 'Data/Original_Img.jpg'
    encrypted_file = 'Data/Encrypted_Img.jpg'
    final_file = 'Data/FinalDecrypted_Img.jpg'

    user_key = 'What is your favourite color?'
    # Encrypting original file creating a new  encrypted file
    fp1 = FileProcessor(src_file, encrypted_file, 'E', user_key)
    fp1.process()

    print('File Encrypted Successfully!')
    # Decrypting previously encrypted file
    fp2 = FileProcessor(encrypted_file, final_file, 'D', user_key)
    fp2.process()
    print('File Decrypted Successfully!')


main()
