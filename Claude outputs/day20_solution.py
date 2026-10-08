## Detective Gutenberg: Sample Solutions (Days 1 & 2)
## Books: Mansfield Park (Austen), Alice in Wonderland (Carroll),
##        The Odyssey (Homer, tr. Samuel Butler)

import re
from collections import Counter
import matplotlib.pyplot as plt

stopwords = ["the", "to", "and", "of", "a", "her", "i", "in", "was", "it",
             "she", "he", "be", "that", "you", "not", "had", "as", "his", "for",
             "with", "is", "have", "but", "at", "so", "all", "my", "been", "him",
             "on", "by", "could", "would", "very", "no", "what", "which", "they",
             "were", "there", "me", "an", "must", "this", "said", "from", "or",
             "will", "any", "much", "than", "such", "their", "them", "if", "do",
             "did", "one", "when", "your", "more", "are", "we", "who", "up",
             "out", "down", "into", "s", "t"]


# =====================================================================
# DAY 1
# =====================================================================

## Loading the books

try:
    with open("../../data/gutenberg/mansfield_park.txt", "r", encoding="utf-8") as f:
        mansfield_lines = f.readlines()
    with open("../../data/gutenberg/alice.txt", "r", encoding="utf-8") as f:
        alice_lines = f.readlines()
    with open("../../data/gutenberg/odyssey.txt", "r", encoding="utf-8") as f:
        odyssey_lines = f.readlines()
except FileNotFoundError:
    print("Couldn't find a file — check the filename and location.")
    raise    # stop here; nothing below works without the books

## Removing the Gutenberg headers & footers

while not mansfield_lines[0].startswith("*** START"):
    mansfield_lines = mansfield_lines[1:]     # chop off the first line
mansfield_lines = mansfield_lines[1:]         # chop off the *** START line itself
while not mansfield_lines[-1].startswith("*** END"):
    mansfield_lines = mansfield_lines[:-1]    # chop off the last line
mansfield_lines = mansfield_lines[:-1]        # chop off the *** END line itself

while not alice_lines[0].startswith("*** START"):
    alice_lines = alice_lines[1:]
alice_lines = alice_lines[1:]
while not alice_lines[-1].startswith("*** END"):
    alice_lines = alice_lines[:-1]
alice_lines = alice_lines[:-1]

while not odyssey_lines[0].startswith("*** START"):
    odyssey_lines = odyssey_lines[1:]
odyssey_lines = odyssey_lines[1:]
while not odyssey_lines[-1].startswith("*** END"):
    odyssey_lines = odyssey_lines[:-1]
odyssey_lines = odyssey_lines[:-1]

mansfield_text = "".join(mansfield_lines)
alice_text = "".join(alice_lines)
odyssey_text = "".join(odyssey_lines)

## Cleaning and splitting into words

mansfield_words = re.split(r"\W+", mansfield_text.lower())
mansfield_words = [w for w in mansfield_words if w != ""]

alice_words = re.split(r"\W+", alice_text.lower())
alice_words = [w for w in alice_words if w != ""]

odyssey_words = re.split(r"\W+", odyssey_text.lower())
odyssey_words = [w for w in odyssey_words if w != ""]

## Type–token ratio, whole book

mansfield_ttr = len(set(mansfield_words)) / len(mansfield_words)
alice_ttr = len(set(alice_words)) / len(alice_words)
odyssey_ttr = len(set(odyssey_words)) / len(odyssey_words)

print("Austen TTR:", round(mansfield_ttr, 3))
print("Carroll TTR:", round(alice_ttr, 3))
print("Homer TTR:", round(odyssey_ttr, 3))

## Type–token ratio, first 10,000 words (a fair comparison)

mansfield_ttr_10000 = len(set(mansfield_words[:10000])) / len(mansfield_words[:10000])
alice_ttr_10000 = len(set(alice_words[:10000])) / len(alice_words[:10000])
odyssey_ttr_10000 = len(set(odyssey_words[:10000])) / len(odyssey_words[:10000])

print("Austen TTR (10,000 words):", round(mansfield_ttr_10000, 3))
print("Carroll TTR (10,000 words):", round(alice_ttr_10000, 3))
print("Homer TTR (10,000 words):", round(odyssey_ttr_10000, 3))

## Explore 3: Average word length

mansfield_wd_len_total = 0
for w in mansfield_words:
    mansfield_wd_len_total += len(w)
mansfield_avg_word_len = mansfield_wd_len_total / len(mansfield_words)

alice_wd_len_total = 0
for w in alice_words:
    alice_wd_len_total += len(w)
alice_avg_word_len = alice_wd_len_total / len(alice_words)

odyssey_wd_len_total = 0
for w in odyssey_words:
    odyssey_wd_len_total += len(w)
odyssey_avg_word_len = odyssey_wd_len_total / len(odyssey_words)

print("Austen average word length:", round(mansfield_avg_word_len, 2))
print("Carroll average word length:", round(alice_avg_word_len, 2))
print("Homer average word length:", round(odyssey_avg_word_len, 2))

## Plotting it out: TTR

plt.bar(["Austen", "Carroll", "Homer (tr. Butler)"],
        [mansfield_ttr_10000, alice_ttr_10000, odyssey_ttr_10000])
plt.title("TTR (First 10,000 Words)")
plt.xlabel("Author")
plt.ylabel("TTR")
plt.savefig("ttr_comparison.png")
plt.show()


# =====================================================================
# DAY 2
# =====================================================================

## Explore 4: Adverbs & Affixes

mansfield_ly = [w for w in mansfield_words if w.endswith("ly")]
alice_ly = [w for w in alice_words if w.endswith("ly")]
odyssey_ly = [w for w in odyssey_words if w.endswith("ly")]

mansfield_ly_rate = len(mansfield_ly) / len(mansfield_words) * 1000
alice_ly_rate = len(alice_ly) / len(alice_words) * 1000
odyssey_ly_rate = len(odyssey_ly) / len(odyssey_words) * 1000

print("Austen -ly per 1,000 words:", round(mansfield_ly_rate, 2))
print("Carroll -ly per 1,000 words:", round(alice_ly_rate, 2))
print("Homer -ly per 1,000 words:", round(odyssey_ly_rate, 2))

print(set(alice_ly))      # not all adverbs: family? only? early? reply?
print(set(odyssey_ly))    # what sneaks in here?

mansfield_un = [w for w in mansfield_words if w.startswith("un")]
alice_un = [w for w in alice_words if w.startswith("un")]
odyssey_un = [w for w in odyssey_words if w.startswith("un")]

print("Austen un- per 1,000 words:", round(len(mansfield_un) / len(mansfield_words) * 1000, 2))
print("Carroll un- per 1,000 words:", round(len(alice_un) / len(alice_words) * 1000, 2))
print("Homer un- per 1,000 words:", round(len(odyssey_un) / len(odyssey_words) * 1000, 2))

## Explore 5: Dialogue

# start from the header-free lists of lines, and remove the empty lines
mansfield_lines = [line.strip() for line in mansfield_lines if line.strip() != ""]
alice_lines = [line.strip() for line in alice_lines if line.strip() != ""]
odyssey_lines = [line.strip() for line in odyssey_lines if line.strip() != ""]

# opening quotation marks only: skip ’ because of don’t, Alice’s, etc.
mansfield_dialogue = [line for line in mansfield_lines if '"' in line or '“' in line or '‘' in line]
alice_dialogue = [line for line in alice_lines if '"' in line or '“' in line or '‘' in line]
odyssey_dialogue = [line for line in odyssey_lines if '"' in line or '“' in line or '‘' in line]

mansfield_dialogue_pct = len(mansfield_dialogue) / len(mansfield_lines) * 100
alice_dialogue_pct = len(alice_dialogue) / len(alice_lines) * 100
odyssey_dialogue_pct = len(odyssey_dialogue) / len(odyssey_lines) * 100

print("Austen dialogue lines:", round(mansfield_dialogue_pct, 1), "%")
print("Carroll dialogue lines:", round(alice_dialogue_pct, 1), "%")
print("Homer dialogue lines:", round(odyssey_dialogue_pct, 1), "%")

## Explore 6: Most Common Content Words

mansfield_content = [w for w in mansfield_words if w not in stopwords]
alice_content = [w for w in alice_words if w not in stopwords]
odyssey_content = [w for w in odyssey_words if w not in stopwords]

print("Austen:", Counter(mansfield_content).most_common(10))
print("Carroll:", Counter(alice_content).most_common(10))
print("Homer:", Counter(odyssey_content).most_common(10))

## Explore 7, part 1: Bar chart

plt.bar(["Austen", "Carroll", "Homer (tr. Butler)"],
        [mansfield_ly_rate, alice_ly_rate, odyssey_ly_rate])
plt.title("-ly Words per 1,000 Words")
plt.xlabel("Author")
plt.ylabel("-ly words per 1,000")
plt.savefig("ly_rates.png")
plt.show()

## Explore 7, part 2: Zipf plot, all three books on one chart

mansfield_freqs = [pair[1] for pair in Counter(mansfield_words).most_common()]
mansfield_ranks = range(1, len(mansfield_freqs) + 1)    # 1, 2, 3, ... up to the number of types

alice_freqs = [pair[1] for pair in Counter(alice_words).most_common()]
alice_ranks = range(1, len(alice_freqs) + 1)

odyssey_freqs = [pair[1] for pair in Counter(odyssey_words).most_common()]
odyssey_ranks = range(1, len(odyssey_freqs) + 1)

plt.plot(mansfield_ranks, mansfield_freqs, label="Austen")
plt.plot(alice_ranks, alice_freqs, label="Carroll")
plt.plot(odyssey_ranks, odyssey_freqs, label="Homer (tr. Butler)")
plt.title("Zipf's Law in Three Books")
plt.xlabel("Rank")
plt.ylabel("Frequency")
plt.xscale("log")
plt.yscale("log")
plt.legend()
plt.savefig("zipf_all.png")
plt.show()
