from .Foundation import BaseTokenizer, build_list, build_heap, merge_pair
import regex as re
import heapq

PATTERN = r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}++|\p{N}{1,3}+| ?[^\s\p{L}\p{N}]++[\r\n]*+|\s++$|\s*[\r\n]|\s+(?!\S)|\s"""

class Tuesday(BaseTokenizer):
    def __init__(self):
        super().__init__()
        self.pattern = re.compile(PATTERN)
    
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
    
    def encode(self, text, merges, specials=None, fast_encode=False):
        encodings = []

        if specials is not None:
            segments = self.split_on_special(text)
        else:
            segments = [text]

        special_lookup = {v:k for k,v in specials.items()} if specials else {}

        for segment in segments:
            if segment in special_lookup:
                encodings.append(special_lookup[segment])
                continue

            if not fast_encode:
                chunks = self.encode_chunk(segment)
                for pair,new_id in merges.items():
                    chunks = [self.merge_pair(chunk, pair, new_id) for chunk in chunks]
                encodings.extend(token for chunk in chunks for token in chunk)
            elif fast_encode == True:
                for word in re.findall(self.pattern, segment):
                    ids = self.getEncoding(word)
                    merged = self.encode_performance(ids, merges)
                    encodings.extend(merged)
            else:
                raise ValueError(f"Encode type {fast_encode} is not valid")
            
        return encodings
    
    def encode_performance(self, chunk, merges):
        encodings = []

        link = build_list(chunk) 
        heap = build_heap(link, merges)

        while heap:
            # Where left.id == x and right.id == y in (x, y) 
            # left.id == x in pair because heap contains (r, p, node, node.next)
            rank, _, pair, left, right = heapq.heappop(heap)

            if left.id == pair[0] and right.id == pair[1] and left.next == right:
                # Perform merge
                left.id = rank
                left.next = right.next

                # Unlink
                if right.next is not None:
                    right.next.prev = left

                if left.prev is not None:
                    new_pair = (left.prev.id, left.id)
                    rank = merges.get(new_pair)
                    if rank is not None:
                        heapq.heappush(heap, (rank, _, new_pair, left.prev, left))

                if right.next is not None:
                    new_pair = (left.id, left.next.id)
                    rank = merges.get(new_pair)
                    if rank is not None:
                        heapq.heappush(heap, (rank, _, new_pair, left, left.next))
            else:
                continue

        node = link
        while node is not None:
            encodings.append(node.id)
            node = node.next

        return encodings

    def decode(self, ids, vocab, specials=None):
        bytes = []

        for id in ids:
            if specials is not None and id in specials:
                bytes.append(specials[id].encode("utf-8"))
            else:
                bytes.append(vocab[id])

        byte = b''.join(bytes)
        decoded = byte.decode("utf-8", errors="replace")
        return decoded
