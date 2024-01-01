import random
import json
import time
import numpy


class LinkedList:
    def __init__(self):
        self.start = None
        self.end = None

    def add(self, item):
        node = LLNode(item)
        if self.start is None:
            self.start = node
        else:
            self.end.next = node
        self.end = node

    def createArray(self):
        array = []
        current = self.start
        while current:
            array.append(current.data.word)
            current = current.next
        return array


class LLNode:
    def __init__(self, data):
        self.data = data
        self.next = None


class LetterMap:
    def __init__(self, wordIndex):
        self.array = numpy.array([LinkedList() for _ in range(26)],
                                 dtype=LinkedList)  # fixed size of 26 indexed from 0-25
        self.wordIndex = wordIndex
        self.fixedArray = []

    def getIndex(self, string):
        return {chr(i + 97): i for i in range(26)}[string.lower()]

    def createFixedArray(self):
        for list in self.array:
            self.fixedArray.append(list.createArray())


class PositionMap:
    allSetWords = set()
    array = numpy.array([LetterMap(i) for i in range(5)], dtype=LetterMap)  # fixed size of 6 indexed from 0-5

    def __init__(self):

        self.allWords = PositionMap.allSetWords.copy()
        self.usedLetters = []
        self.letterRatingOrder = [chr(i + 97) for i in range(26)]
        self.guesses = []

    def getRating(self, word):
        points = 0
        for letter in word:
            points += self.letterRatingOrder.index(letter)

        return 100 - points

    def getCancelRating(self):
        letterFreq = {chr(i + 97): 0 for i in range(26)}
        for word in self.allWords:
            seenletters = []
            for letter in word:

                letterFreq[letter] += 1
                if letter in self.usedLetters:
                    letterFreq[letter] -= 10
                if letter in seenletters:
                    letterFreq[letter] -= 2
                seenletters.append(letter)

        self.letterRatingOrder = sorted(letterFreq.keys(), key=lambda x: letterFreq[x])

    def addWord(word):
        wordObj = Word(word)
        for i, letter in enumerate(wordObj.word):
            PositionMap.array[i].array[PositionMap.array[i].getIndex(letter)].add(wordObj)
        PositionMap.allSetWords.add(word)

    @staticmethod
    def done():
        for letterMap in PositionMap.array:
            letterMap.createFixedArray()

    def getWords(self, queries):
        word = ""
        for i, query in enumerate(queries):
            word += query.letter

            if query.colour == "green":
                self.usedLetters.append(query.letter)
                self.allWords = self.allWords.intersection(self.GetGreens(i, query.letter))
            if query.colour == "orange":
                self.usedLetters.append(query.letter)
                self.allWords = self.allWords.intersection(self.GetOranges(i, query.letter))

            if query.colour == "grey":
                self.allWords = self.allWords.intersection(self.GetReds(query.letter))

        self.allWords.discard(word)
        self.getCancelRating()
        self.guesses.append(word)

        return sorted(self.allWords, key=lambda x: self.getRating(x))

    def GetGreens(self, index, letter):
        return PositionMap.array[index].fixedArray[PositionMap.array[index].getIndex(letter)]

    def GetReds(self, letter):
        wordSet = []
        first = True
        for index in range(5):
            if first:
                wordSet = set(self.GetGreens(index, letter))
                first = False
            else:
                wordSet = wordSet | set(self.GetGreens(index, letter))

        return self.allWords - wordSet

    def GetOranges(self, index, letter):
        wordSet = []
        first = True
        for i in range(5):
            if i != index:
                if first:
                    wordSet = set(self.GetGreens(i, letter))
                    first = False
                else:
                    wordSet = wordSet | set(self.GetGreens(i, letter))

        return wordSet


class query:
    def __init__(self, letter, colour):
        self.letter = letter
        self.colour = colour.lower()


class Word:
    def __init__(self, word):
        self.word = word


class game:
    avgGuess = 0
    amountPlayed = 0
    avgLuck = 0

    def __init__(self, answer, printInfo=False):
        game.amountPlayed += 1

        self.answer = answer
        self.printInfo = printInfo
        if printInfo: print("Answer : " + answer)
        self.map = PositionMap()
        self.guesses = 0
        self.amountPossibleGuesses = 0

    def guess(self, word):

        self.guesses += 1
        if self.printInfo: print("Guess " + str(self.guesses) + ": " + word)
        colours = []
        for i, letter in enumerate(word):
            if letter == self.answer[i]:
                colours.append("green")
            elif letter in self.answer:
                colours.append("orange")
            else:
                colours.append("grey")

        self.generateQueries(colours, word)

    def generateQueries(self, colours, word):
        queries = []
        amountGreens = 0
        for i in range(5):
            if colours[i] == "green":
                amountGreens += 1
            queries.append(query(word[i], colours[i]))
        if amountGreens >= 5:
            game.avgGuess += self.guesses
            if self.amountPossibleGuesses != 0:
                game.avgLuck += round(1 / self.amountPossibleGuesses, 2)
                if self.printInfo: print("Probability of word : " + str(round(1 / self.amountPossibleGuesses, 2)))
            return

        possibleWords = self.map.getWords(queries)

        self.amountPossibleGuesses = len(possibleWords)
        self.guess(possibleWords[0])


filePath = 'words.json'

# Open and read the JSON file
with open(filePath, 'r') as file:
    data = json.load(file)

now = time.time()
for i in data:
    PositionMap.addWord(i)
PositionMap.done()
print(time.time() - now)

now = time.time()
for i in range(1000):
    answer = data[random.randint(0, len(data) - 1)].lower()
    g = game(answer, printInfo=True)
    g.guess("slate")

print("AvgGuesses: " + str(game.avgGuess / game.amountPlayed))
print("AvgLuck: " + str(game.avgLuck / game.amountPlayed))

print("AvgTimePerGame: " + str(float((time.time() - now)) / game.amountPlayed))
