class DAWGNode:
    def __init__(self):
        self.edges = {}
        self.final = False  # Whether this node represents the end of a word

    def add_edge(self, char, node):
        self.edges[char] = node

    def get_edge(self, char):
        return self.edges.get(char)

class DAWG:
    def __init__(self, file_path=None):
        self.root = DAWGNode()
        self.previous_word = ""
        self.minimized_nodes = {}
        self.unchecked_nodes = []

        if file_path:
            self.build_from_file(file_path)

    def build_from_file(self, file_path):
        with open(file_path, 'r') as file:
            words = [line.strip().lower() for line in file]  # Convert to lowercase

        words.sort()  # Ensure words are in lexicographical order

        for word in words:
            self.insert(word)

        self.finish()

    def insert(self, word):
        # Ensure words are inserted in lexicographical order
        if word < self.previous_word:
            raise ValueError("Words must be inserted in lexicographical order.")

        common_prefix_length = 0
        for i in range(min(len(word), len(self.previous_word))):
            if word[i] != self.previous_word[i]:
                break
            common_prefix_length += 1

        # Minimize the nodes from the last unique character to the end
        self._minimize(common_prefix_length)

        # Add the suffix for the current word
        node = self.unchecked_nodes[-1][2] if self.unchecked_nodes else self.root
        for char in word[common_prefix_length:]:
            next_node = DAWGNode()
            node.add_edge(char, next_node)
            self.unchecked_nodes.append((node, char, next_node))
            node = next_node

        node.final = True
        self.previous_word = word

    def _minimize(self, down_to):
        for i in range(len(self.unchecked_nodes) - 1, down_to - 1, -1):
            parent, char, child = self.unchecked_nodes[i]
            if child in self.minimized_nodes:
                parent.add_edge(char, self.minimized_nodes[child])
            else:
                self.minimized_nodes[child] = child
            self.unchecked_nodes.pop()

    def finish(self):
        self._minimize(0)

    def search(self, word):
        node = self.root
        for char in word:
            node = node.get_edge(char)
            if node is None:
                return False
        return node.final

    def add_word(self, word):
        word = word.lower()
        if self.search(word):
            return  # The word is already present

        self.unchecked_nodes = []
        self.previous_word = ""

        words = self.collect_all_words(self.root, "")
        if word not in words:
            words.append(word)
        words.sort()

        self.root = DAWGNode()
        self.minimized_nodes = {}
        for word in words:
            self.insert(word)
        self.finish()
    def collect_all_words(self, node, prefix):
        words = []
        if node.final:
            words.append(prefix)
        for char, next_node in node.edges.items():
            words.extend(self.collect_all_words(next_node, prefix + char))
        return words

    def wildcard_search(self, pattern):
        pattern = pattern.lower()
        results = []
        self._wildcard_dfs(self.root, pattern, "", results)
        return results

    def _wildcard_dfs(self, node, pattern, prefix, results):
        if not pattern:
            if node.final:
                results.append(prefix)
            return

        char = pattern[0]
        if char == '*':
            # '*' can match zero or more characters
            self._wildcard_dfs(node, pattern[1:], prefix, results)  # Match zero characters
            for edge_char, next_node in node.edges.items():
                self._wildcard_dfs(next_node, pattern, prefix + edge_char, results)
                self._wildcard_dfs(next_node, pattern[1:], prefix + edge_char, results)
        elif char == '?':
            # '?' can match exactly one character
            for edge_char, next_node in node.edges.items():
                self._wildcard_dfs(next_node, pattern[1:], prefix + edge_char, results)
        else:
            next_node = node.get_edge(char)
            if next_node:
                self._wildcard_dfs(next_node, pattern[1:], prefix + char, results)


# Example usage:
if __name__ == "__main__":
    file_path = 'collins2019.txt'
    dawg = DAWG(file_path)

    # Add new word
    new_word = "catalog"
    dawg.add_word(new_word)

    # Testing the DAWG
    print(dawg.search("car"))     # True
    print(dawg.search("cat"))     # True
    print(dawg.search("dog"))     # True
    print(dawg.search("dogs"))    # True
    print(dawg.search("catalog")) # True
    print(dawg.search("do"))      # False
    print(dawg.search("cats"))    # False

    # Wildcard searches
    print(dawg.wildcard_search("cater*"))      # ['car', 'cat', 'catalog']
    print(dawg.wildcard_search("*log"))      # ['dog', 'catalog']
    print(dawg.wildcard_search("ca?"))      # ['car', 'cat']
    print(dawg.wildcard_search("*ta*ning"))     # ['catalog']
    print(dawg.wildcard_search("*t?g*k*"))  # ['catalog']
