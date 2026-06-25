from .Foundation import BaseTokenizer
import regex as re

PATTERN = r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}++|\p{N}{1,3}+| ?[^\s\p{L}\p{N}]++[\r\n]*+|\s++$|\s*[\r\n]|\s+(?!\S)|\s"""

class Tuesday(BaseTokenizer):
    def __init__(self):
        super().__init__()
        self.pattern = re.compile(PATTERN)
    
    def merge_pair(self, encodings, pair, new_id):
        merged = []

        i = 0
        for _ in encodings:
            if i < len(encodings):
                if i < len(encodings) - 1 and pair[0] == encodings[i] and pair[1] == encodings[i + 1]:
                    merged.append(new_id)
                    i += 2
                else:
                    merged.append(encodings[i])
                    i += 1

        return merged

    def register_special(self, special_tokens, starting_id):
        specials = {}

        new_special_id = starting_id + 1
        for special in special_tokens:
            specials[new_special_id] = special
            new_special_id += 1

        return specials
    
    def split_on_special(self, text):
        split_pattern = r'(<.*?>)'
        split = re.split(re.compile(split_pattern), text)
        return split
    
    def encode_chunk(self, text):
        encoded_chunk = []
        split_text = re.findall(self.pattern, text)
        for split in split_text:
            encoded_chunk.append(self.getEncoding(split))

        return encoded_chunk

    def encode(self, text, merges, specials=None):
        encoded_chunks = []

        if specials is not None:
            split_text = self.split_on_special(text)
            for word in split_text:
                encoded_word = self.getEncoding(word)
                for k,v in specials.items():
                    encoded_special = self.getEncoding(v)
                    if encoded_word == encoded_special:
                        encoded_chunks.append([k])
                    else: 
                        encoded_chunks.append(encoded_word)
        else:
            encoded_chunks = self.encode_chunk(text)

        for merge in merges:
            merged_chunks = []
            for chunk in encoded_chunks:
                merged_chunks.append(self.merge_pair(chunk, merge, merges[merge]))
            encoded_chunks = merged_chunks
        encoded_chunks = [encoding for chunk in merged_chunks for encoding in chunk]
        return encoded_chunks

    def decode(self, ids, vocab, specials=None):
        bytes = []

        for id in ids:
            if specials is not None and id in specials:
                bytes.append(specials[id].encode("utf-8"))
            else:
                bytes.append(vocab[id])

        byte = b''.join(bytes)
        decoded = byte.decode("utf-8")
        return decoded