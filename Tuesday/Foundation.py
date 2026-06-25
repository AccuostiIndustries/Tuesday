import json

class BaseTokenizer:
    def __init__(self):
        self.merges = {}
        self.vocab, self.specials = self.buildVocab()
        self.pattern = ""

    def encode(self, text, merges, specials=None):
        raise NotImplementedError
    
    def decode(self, ids, vocab, specials=None):
        raise NotImplementedError

    def getEncoding(self, text):
        """Converts text into a list of utf-8 encodings"""
        encodings = list(text.encode("utf-8"))
        return encodings
    
    def buildVocab(self, specials=None):
        """
        Specials is None by default, but you can optionally pass in a list of special tokens.  
        """
        vocab = {}
        special_tokens = {}

        for i in range(256):
            vocab[i] = bytes([i])

        for (x,y),v in self.merges.items():
            vocab[v] = vocab[x] + vocab[y]

        starting_special_id = max(self.merges.values()) if self.merges else 255
        if specials is not None:
            special_tokens = self.register_special(specials, starting_special_id)

        return vocab, special_tokens
        
    def loadState(self, file):
        """
        This provided load function accepts a json and returns the merges, vocab, and specials from it.
        
        The Tokenizer expects the JSON to be formatted: 
        {"merges": [[x,y,z]], "specials": {"int":string}, "vocab": {"int":[bytes]}} 
        """
        merges = {}
        vocab = {}
        specials = {}

        with open(file, "r") as f:
            data = json.load(f)

        loaded_merges = data["merges"]
        loaded_vocab = data["vocab"]
        loaded_specials = data["specials"]

        for merge in loaded_merges:
            pair = (merge[0], merge[1])
            merges[pair] = merge[2]
        
        for k,v in loaded_vocab.items():
            vocab[int(k)] = bytes(v)

        for k,v in loaded_specials.items():
            specials[int(k)] = v

        self.merges = merges
        self.vocab = vocab
        self.specials = specials