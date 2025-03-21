from Statistics.Statistics import *
from Grammar.grammar2 import *
from Spellings.Spellings import *
from Coherence.Coherence import *
from operator import itemgetter
#from six.moves import input
#from validate import predict_score

def get_logical_sentences(essay):
    sentences = [" ".join([word.text for word in sentence.words]) for sentence in nlp(essay).sentences]  # ✅ Correct
    logical_sentences = []

    for sentence in sentences:
        if has_logical_connectors(sentence):
            logic_consistency_score = 1  # You can modify this based on your needs
            logical_sentences.append({'sentence': sentence, 'score': logic_consistency_score})

    return logical_sentences

def return_score(essay1,key):
    essay=essay1
    key1=key
    print(essay)
    wordCount = getWordCount(essay)
    sentCount = getSentenceCount(essay)
    paraCount = getParaCount(essay)
    avgSentLen = getAvgSentenceLength(essay)
    stdDevSentLen = getStdDevSentenceLength(essay)

    # Spellings
    numMisspelt, misspeltWordSug = spellCheck(essay)


    grammarCumScore, grammarSentScore = get_grammar_score(essay)


    coherenceScore = check_coherence(essay,key)


    overallScore = str(
    format(
        (
            ((1 - (float(numMisspelt) / wordCount)) * 5)
            + grammarCumScore
            + coherenceScore
        )
        / 3,
        ".2f",
    )
)


    logical_sentences = get_logical_sentences(essay)

    s = '''<!DOCTYPE html>
<html lang="en">

<head>
    <title>Optimized Automated Essay Grader</title>
    <meta charset="utf-8" />
    <link type="text/css" rel="stylesheet" href="../style.css" />
</head>

<body>
    <div id="canvas">
        <div>
            <div id="heading"> <h1><center> OPTIMIZED AUTOMATED ESSAY GRADER </center></h1></div>
            <br />'''

    s = s + '''<br /> <hr /> <hr /> <br />

        <div style="float:left; font-size:18pt" id="scoretable">
            <img src="../images/grade.jpg" />
            <h2> Overall Score</h2>
            <table border="1" align="right">
                <tr> <th class="big">GRADE (0-5)</th> <th class="big">''' + str(
    overallScore
) + '''</th></tr>
                <tr> <th>Spelling(0-5)</th> <td>''' + str(
    format((1 - (float(numMisspelt) / wordCount)) * 5, ".2f")
) + '''</td></tr>
                <tr> <th>Grammar(0-5)</th> <td>''' + str(
    format(grammarCumScore, ".2f")
) + '''</td></tr>
                <tr> <th>Coherence(0-5)</th> <td>''' + str(
    format(coherenceScore, ".2f")
) + '''</td></tr>
            </table>
        </div>

        <div style="float:right" id="statistics">
            <img src="../images/stats.jpg" />
            <h2> Essay Statistics</h2>
            <table border="1" align="left">
                <tr align='left'> <th>Word Count</th> <td>''' + str(
    wordCount
) + '''</td></tr>
                <tr align='left'> <th>Sentence Count</th> <td>''' + str(
    sentCount
) + '''</td></tr>
                <tr align='left'> <th>Paragraph Count</th> <td>''' + str(
    paraCount
) + '''</td></tr>
                <tr align='left'> <th>Average Sentence Length</th> <td>''' + str(
    format(avgSentLen, ".2f")
) + '''</td> </tr>
                <tr align='left'> <th>Standard Deviation from the Average Sentence Length</th> <td>''' + str(
    format(stdDevSentLen, ".2f")
) + '''</td> </tr>
            </table>
        </div>
        </div>

        <br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /><br /> <hr /> <hr /> <br />

        <div id="spellings">
            <img src="../images/spell.jpg" />
            <h2> Spellings </h2>
            <h3 style="text-align:left">Number of Misspelt Words ::''' + str(
    numMisspelt
) + '''</h3>
            <h2 style="text-align:right" class="score" >Score :: ''' + str(
    format((1 - (float(numMisspelt) / wordCount)) * 5, ".2f")
) + '''</h2>

            <table border="1">
                <thead> <tr> <th>Misspelt Word</th> <th> Spelling Suggestions</th> </tr> </thead>
                <tbody>'''

    for key in misspeltWordSug:
        s = s + "<tr> <td>" + key + "</td> <td> " + str(
        misspeltWordSug[key]
    ) + "</td> </tr>"

    s = s + """</tbody>
            </table>
        </div>
        <br /> <hr /> <hr /> <br />

        <div id="grammar">
            <img src="../images/grammar.jpg" />
            <h2> Grammar </h2>
            <h2 style="text-align:right" class="score" >Score :: """ + str(
    format(grammarCumScore, ".2f")
) + """</h2>

            <table border="0">
                <thead> <tr> <th>Sentences</th> <th> Score</th> </tr> </thead>
                <tbody>"""

# prints sorted table
    for key in reversed(
        sorted(list(grammarSentScore.items()), key=itemgetter(1))
):
        s = s + "<tr> <td>" + key[0] + "</td> <td> " + str(
        key[1]
    ) + "</td> </tr>"

    s = s + """ </tbody>
            </table>
        </div>
        <br /> <hr /> <hr /> <br />


        <div id="coherence">
            <img src="../images/coherence.jpg" />
            <h2> Coherence </h2>
            <h2 class="score" style="text-align:right"> Score :: """ + str(
    format(coherenceScore, ".2f")
) + """</h2>

            <table border="0">
                <thead> <tr> <th>Sentences</th> <th> Score</th> </tr> </thead>
                <tbody>"""

    for logical_sentence in logical_sentences:
        s += f"<tr> <td>{logical_sentence['sentence']}</td> <td>{logical_sentence['score']}</td> </tr>"

    s += """</tbody>
            </table>
        </div>
        <br /> <hr /> <hr /> <br />


        <div>
        <img src="../images/essay.jpg" />

        <h2> Essay </h2> <div id="essay">"""

    for para in essay.splitlines():
        if para == "":
            s = s + "<br /> <br />"
        else:
            s = s + para

    s = s + """</div></div> <br /> <hr /> <hr /> <br />

    </div>

</body>

</html>


"""

    embed=0.5  #predict_score(essay1,key1)

    res ='\ngrammer cummilative score : '+str(grammarCumScore) +'\n spelling score :'+str(format((1 - (float(numMisspelt) / wordCount)) * 5, ".2f"))+'\n coherence score '+str(coherenceScore)+'\n Overall score :'+str(overallScore)
     
    return s,res,overallScore

if __name__=="__main__":
    print(return_score(input(),input()))
