from textblob import TextBlob
import re

########## function which checks spellings ##############
#         INPUT : essay
#         OUTPUT: returns the number of misspelt words AND key-value pairs of misspelled words and suggestions to correct them

def spellCheck(text):
    # Split the text into words
    wordList = re.findall(r'\w+', text)
    
    misspelt = {}
    numIncorrect = 0
    
    ### Checking for misspelled words ###
    for word in wordList:
        blob = TextBlob(word)
        corrected_word = str(blob.correct())
        
        if corrected_word != word:
            misspelt[word] = corrected_word  # Store the word and its suggestion
            numIncorrect += 1
            
    return numIncorrect, misspelt

######  INDEPENDENTLY TESTING THE SCRIPT ########
if __name__ == '__main__':
    
    #### open essay, in the format (.txt) ####
    sourceFileName = "Sample_Essays/technology.txt"
    with open(sourceFileName, "r", encoding="utf-8") as sourceFile:
        # Read essay
        text = sourceFile.read()
    
    incorr2, misspelt2 = spellCheck(text)
    print("\n\nIncorrectly spelled count: ", incorr2, "\n")
    
    for key in misspelt2:
        print(key, " :: ", misspelt2[key], "\n\n")
