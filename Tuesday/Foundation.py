import json
import heapq

"""""""""
This file contains helper functions, structures, and other resources that are critical to the operation of Tuesday
"""""""""

# ================================================
# Structures

class Node():
    def __init__(self, prev, id, next):
        self.prev = prev
        self.id = id
        self.next = next

# ================================================
# Helper functions

def build_list(chunk):
    """
    Accepts a list of token ids and returns the head of a linked list.
    """
    head = Node(None, chunk[0], None)

    current = head
    for i,_ in enumerate(chunk):
        if i < len(chunk) - 1:
            new = Node(current, chunk[i+1], None)
            current.next = new
            current = new

    return head

def build_heap(head, merges):
    """
    Accepts the head node of a linked list and the merges dictionary.
    Returns a heap.
    """
    heap = []
    counter = 0
    
    node = head
    while node is not None:
        if node.next is not None:
            pair = (node.id, node.next.id)

            if pair in merges:
                heapq.heappush(heap, (merges[pair], counter, pair, node, node.next))
                counter += 1

        node = node.next

    return heap

# ================================================
# The base tokenizer class 

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
        This function returns a dictionary for both vocab and special tokens.  
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
        This provided load function accepts a json in the following format: 
        {"merges": [[x,y,z],[x,y,z]], "specials": {"id":special}, "vocab": {"id":[bytes]}} 
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
