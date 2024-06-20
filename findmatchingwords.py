from dawg import DAWG
from itertools import permutations, chain, combinations

def generate_combined_results(pattern, char_list):
    # Identify the positions of '?'
    positions = [i for i, char in enumerate(pattern) if char == '?']

    # Generate all permutations of characters to fill '?'
    permuted_values = permutations(char_list, len(positions))

    combined_results = set()

    for perm in permuted_values:
        temp_pattern = list(pattern)
        for pos, char in zip(positions, perm):
            temp_pattern[pos] = char
        result_pattern = "".join(temp_pattern)

        # Calculate unused characters
        used_chars = list(perm)
        unused_chars = char_list.copy()
        for char in used_chars:
            unused_chars.remove(char)

        # Generate all subsets of unused characters
        subsets = list(chain.from_iterable(combinations(unused_chars, r) for r in range(len(unused_chars)+1)))

        # Generate all permutations of each subset
        for subset in subsets:
            for perm in permutations(subset):
                perm_list = list(perm)
                for i in range(len(perm_list) + 1):
                    prefix = ''.join(perm_list[:i])
                    postfix = ''.join(perm_list[i:])
                    combined_result = prefix + result_pattern + postfix
                    combined_results.add(combined_result)

    return combined_results

# Function to filter valid words from combined results
def filter_valid_words(combined_results, word_dictionary):
    valid_words = set()
    for word in combined_results:
        if '?' in word:
            matches = word_dictionary.wildcard_search(word.lower())
            valid_words.update(matches)
        else:
            if word_dictionary.search(word.lower()):
                valid_words.add(word)
    return valid_words

def find_matching_words(pattern, char_list, word_dictionary):
    combined_results = generate_combined_results(pattern, char_list)
    words = filter_valid_words(combined_results, word_dictionary)
    return words

if __name__ == "__main__":
    # Initialize the DAWG dictionary
    dictionary_path = "collins2019.txt"
    word_dictionary = DAWG(dictionary_path)

    pattern = "?"
    char_list = ["i", "s", "n", "a", "o", "c", "a"]
    print(f"Pattern: {pattern}")
    valid_words = find_matching_words(pattern, char_list, word_dictionary)
    for word in valid_words:
        print(word)
