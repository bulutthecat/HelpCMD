import operator

class TrieNode(object):
    def __init__(self, char):
        self.char = char
        self.children = []
        self.wordFinished = False


class TextPredictionAPI(object):
    def __init__(self):
        self.unigramMap = dict()
        self.bigramMap = dict()
        self.trigramMap = dict()
        self.ngramMap = dict()
        self.nextWordsListMap = dict()

        self.root = TrieNode('*')
        self.corpusArray = self.getStringArrayFromCorpus('Big.txt')

        self.makeUnigramMap()
        self.makeBigramMap()
        self.makeTrigramMap()
        self.makeNgramMap()
        self.makeNextWordsListMap()
        self.addWordsToTrie()

        self.wordList = []

    def getStringArrayFromCorpus(self, fileName):
        with open(fileName, 'r') as myfile:
            data = myfile.read().replace('\n', ' ')
        return data.split(' ')

    def makeUnigramMap(self):
        for string in self.corpusArray:
            self.unigramMap[string] = self.unigramMap.get(string, 0) + 1

    def makeBigramMap(self):
        size = len(self.corpusArray)
        for i in range(size - 1):
            string = self.corpusArray[i] + ' ' + self.corpusArray[i + 1]
            self.bigramMap[string] = self.bigramMap.get(string, 0) + 1

    def makeTrigramMap(self):
        size = len(self.corpusArray)
        for i in range(size - 2):
            string = self.corpusArray[i] + ' ' + self.corpusArray[i + 1] + ' ' + self.corpusArray[i + 2]
            self.trigramMap[string] = self.trigramMap.get(string, 0) + 1

    def makeNgramMap(self):
        size = len(self.corpusArray)
        for i in range(size - 3):
            string = self.corpusArray[i] + ' ' + self.corpusArray[i + 1] + ' ' + self.corpusArray[i + 2] + ' ' + self.corpusArray[i + 3]
            self.ngramMap[string] = self.ngramMap.get(string, 0) + 1

    def makeNextWordsListMap(self):
        for string in self.corpusArray:
            self.nextWordsListMap[string] = set()

        size = len(self.corpusArray)
        for i in range(size - 1):
            self.nextWordsListMap[self.corpusArray[i]].add(self.corpusArray[i + 1])

    def addWordsToTrie(self):
        size = len(self.corpusArray)
        for i in range(size):
            word = str(self.corpusArray[i])
            node = self.root

            for char in word:
                charFound = False
                for child in node.children:
                    if char == child.char:
                        node = child
                        charFound = True
                        break
                if not charFound:
                    newNode = TrieNode(char)
                    node.children.append(newNode)
                    node = newNode
            node.wordFinished = True

    def getLastWordFromSentence(self, screenText):
        screenTextArray = screenText.split()
        size = len(screenTextArray)
        return screenTextArray[size - 1]

    def getLargestCommonPrefix(self, root, word):
        node = root
        prefix = ""
        for char in word:
            charFound = False
            for child in node.children:
                if char == child.char:
                    node = child
                    charFound = True
                    prefix = prefix + child.char
                    break
            if not charFound:
                return self.DFSOnTrie(node, prefix)
        return self.DFSOnTrie(node, prefix)

    def DFSOnTrie(self, node, prefixNow):
        if node.wordFinished:
            self.wordList.append(prefixNow)

        for child in node.children:
            self.DFSOnTrie(child, prefixNow + child.char)

    def calculateProbability(self, num, den):
        return float(float(num) / float(den))

    def clearWordList(self):
        self.wordList = []

    def nextWordPrediction(self, screenText):
        screenTextArray = screenText.split()
        size = len(screenTextArray)
        probabilityMap = dict()

        if(size == 0):
            for key, value in self.unigramMap.items():
                probabilityMap[str(key)] = float(value)
        elif(size == 1):
            denString = screenTextArray[size - 1]
            lastWord = screenTextArray[size - 1]
            den = float(self.unigramMap.get(denString))

            for numString in self.nextWordsListMap[lastWord]:
                search = denString + ' ' + numString
                num = float(self.bigramMap.get(search, 0) if self.bigramMap.get(search) is not None else 0)
                value = self.calculateProbability(num, den)
                probabilityMap[numString] = value
        elif(size == 2):
            denString = screenTextArray[size - 2] + ' ' + screenTextArray[size - 1]
            lastWord = screenTextArray[size - 1]
            den = float(self.bigramMap.get(denString))

            for numString in self.nextWordsListMap[lastWord]:
                search = denString + ' ' + numString
                num = float(self.trigramMap.get(search, 0) if self.trigramMap.get(search) is not None else 0)
                value = self.calculateProbability(num, den)
                probabilityMap[numString] = value
        else:
            denString = screenTextArray[size - 3] + ' ' + screenTextArray[size - 2] + ' ' + screenTextArray[size - 1]
            lastWord = screenTextArray[size - 1]
            den = float(self.trigramMap.get(denString))

            for numString in self.nextWordsListMap[lastWord]:
                search = denString + ' ' + numString
                num = float(self.ngramMap.get(search, 0) if self.ngramMap.get(search) is not None else 0)
                value = self.calculateProbability(num, den)
                probabilityMap[numString] = value

        sortedProbabilityMap = sorted(probabilityMap.items(), key=operator.itemgetter(1), reverse=True)

        topWords = []
        for key, value in sortedProbabilityMap[:3]:
            topWords.append(key)

        return topWords

    def wordCompletion(self, screenText):
        self.clearWordList()
        lastWord = self.getLastWordFromSentence(screenText)
        self.getLargestCommonPrefix(self.root, lastWord)

        frequencyMap = dict()
        for word in self.wordList:
            frequencyMap[word] = self.unigramMap[word]

        sortedFrequencyMap = sorted(frequencyMap.items(), key=operator.itemgetter(1), reverse=True)

        topWords = []
        for key, value in sortedFrequencyMap[:3]:
            topWords.append(key)

        return topWords