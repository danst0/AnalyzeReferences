#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess, sys
from pprint import pprint

import re, codecs, markup, os, commands

def listFiles(dir):
    basedir = dir
    list = []
    #print "Files in ", os.path.abspath(dir), ": "
    tmp_list = []
    try:
        tmp_list = os.listdir(dir)
    except:
        # kein directory!
        pass
        tmp_list = None
    if tmp_list == None:
        # also ein file
        list = dir
        #print list
    else:
        for item in tmp_list:
            #print "item", item
            tmp = listFiles(os.path.join(basedir, item))
            if tmp != []:
                #print tmp
                if isinstance(tmp, type([])):
                    for i in tmp:
                        list.append(i)
                else:
                    list.append(tmp)
                #print "file", item
    #print list
    return list

def getClipboardData():
    p = subprocess.Popen(['pbpaste'], stdout=subprocess.PIPE)
    #retcode = p.wait()
    data = p.stdout.read()
    data = unicode(data, "utf-8")
    return data

def setClipboardData(data):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(data)
    p.stdin.close()
    #retcode = p.wait()
    
def makeCompareable(text):
    return text.lower().replace(":","").replace(".","").replace(" ","").replace("-","").replace(",","").replace("\"","")
    
def extractBibliography(pdfname):
    outfile = pdfname + ".txt"
    text = ""
    notAllowed = False
    if not os.path.isfile(outfile) or os.path.getsize(outfile) < 100:
        print "Lese", pdfname
        tmp = commands.getoutput("python pdf2txt.py -o \"" + outfile + "\" \"" + pdfname + "\"")
        if tmp.find("PDFTextExtractionNotAllowed") != -1:
            print "Extraktion der Daten nicht erlaubt."
            print pdfname
            notAllowed = True
        elif tmp != "":
            print "Fehler beim Einlesen des PDFs"
            print pdfname
            print tmp
            sys.exit(1)

    if not notAllowed:
        #raw_input()
        file = codecs.open(outfile, "r", "utf-8")
        bib = False
        for line in file.readlines():
            if (line.lower().strip() == "bibliography") or (line.lower().strip() == "references"):
                bib = True
            if bib:
                line = line.replace(u"\ufb01", "fi")
                line = line.replace(u"\ufb03", "ffi")
                line = line.replace(u"\ufb02", "fl")
                line = line.replace(u"\xe9", "e")
                line = line.replace(u"\xe8", "e")
                line = line.replace(u"\xf6", "oe")
                line = line.replace(u"\u2014", "-")
                line = line.replace(u"’’", "\"")
                line = line.replace(u"\xd6", "Oe")
                line = line.replace(u"\xae", "(c)")
                line = line.replace(u"\xd5", "\"")
                line = line.replace(u"\xd4", "\"")
                line = line.replace(u"\u2018\u2018", "\"")
                line = line.replace(u"\xe0", "a")
                line = line.replace(u"\xfc", "u")
                line = line.replace(u"\xe7", "c")
                line = line.replace(u"\xe1", "a")
                line = line.replace(u"\xe4", "a")
                line = line.replace("  ", " ")
                text += line + " "
        file.close()

    return text


def GetText():
    text = getClipboardData()
    return text

def AnalyzeText(text, pdfname):
    # was weiß ich über den text
    # Jahr zwischen 1920 und 2100
    # Autoren zuerst, mit vorname oder ohne, vorher oder danach
    # Titel länger, idr. kein "journal"
    error = 0
    author = []
    year = 0
    title = ""
    papers = []
  
    
    # first pattern
    # Azaron, A., Katagiri, H., Kato, K., Sakawa, M., 2006. Modelling complex assemblies as a queueing network for lead time control. European Journal of Operational Research 174, 150–168.
    pAuthor = "(?P<author>([A-Z][a-z]+,\s([A-Z-\.]{1,4}\.)+((,\s)|(\sand\s)|(,\sand\s)||(\s)))+)"#"(?P<author>(([A-Za-z-]+),\s([A-Z]\.)+(,)?\s)+)"
    pYear = "(([2][0][0-2][0-9])|([1][9][2-9][0-9]))\.\s"
    pTitle = "(?P<title>[-\sA-Za-z0-9':\",\(\)]{10,150}\.\s)"
    pJournal = "[\sA-Za-z0-9\.]+\s"
    pIssue = "[A-Za-z0-9\(\)]+[,\.:]\s"
    pPages = "[-0-9]{3,11}\."
    pattern = pAuthor + pYear + pTitle + pJournal + pIssue + pPages
    find = re.finditer(pattern, text)
    if find != None:    
        for item in find:
            #print "REGEXP", item.group(0), ":::"
            author = item.group("author")
            title = item.group("title")
            papers.append({"author": author, "title": title, "pattern": "ayt", "compare": makeCompareable(title), "pdf": pdfname})
            text = text.replace(unicode(item.group(0)), "xxxxxxxx")

            
    #second pattern
    # Chapman, P., Christopher, M., Ju ̈ ttner, U., Peck, H. and Wilding, R., Identifying and managing supply chain vulnerability. Focus, 2002, May, 59–64. Child, J., Organizational structure, environment and performance: the role of strategic choice. Sociology, 1972, 6, 1–22. 
    pAuthor = "(?P<author>([A-Z][a-z]+,\s([A-Z]\.)+((,\s)|(\sand\s)))+)"
    pTitle = "(?P<title>[-\sA-Za-z0-9,:]{10,150}(\.|,)\s)"
    pJournal = "[\.\sA-Za-z0-9]+,\s"
    pYear = "(([2][0][0-2][0-9])|([1][9][2-9][0-9])),\s"
    pIssue = "[A-Za-z0-9\(\)]+,\s"
    pPages = "[-0-9]{3,11}\."
    pattern = pAuthor + pTitle + pJournal + pYear + pIssue + pPages
    find = re.finditer(pattern, text)
    if find != None:    
        for item in find:
            author = item.group("author")
            title = item.group("title")
            papers.append({"author": author, "title": title, "pattern": "aty", "compare": makeCompareable(title), "pdf": pdfname})
            text = text.replace(unicode(item.group(0)), "xxxxxxxx")
    
    # second b pattern
    #M. Ronnqvist, An exact method for the two-echelon, single-source, capacitated facility location problem, European Journal of Operational Research 123 (2000) 473-489.'
    pAuthor = "(?P<author>((([A-Z]\.)+\s[A-Z][a-z]+)+((,\s)|(\sand\s)))+)"
    pTitle = "(?P<title>[-\sA-Za-z0-9,:\"\'\(\)]{10,150}(\.|,)\s)"
    pJournal = "[\.\sA-Za-z0-9]+\s"
    pIssue = "[A-Za-z0-9\(\)]+\s"
    pYear = "\((([2][0][0-2][0-9])|([1][9][2-9][0-9]))\)(,?)\s"
    pPages = "[-0-9\s]{3,11}\."
    pattern = pAuthor + pTitle + pJournal + pIssue + pYear + pPages
    find = re.finditer(pattern, text)
    if find != None:    
        for item in find:
            author = item.group("author")
            title = item.group("title")
            papers.append({"author": author, "title": title, "pattern": "at(y)", "compare": makeCompareable(title), "pdf": pdfname})
            text = text.replace(unicode(item.group(0)), "xxxxxxxx")
            
    #third pattern
    #Spira, L.F. and Page, M. (2002), “Risk management: the reinvention of internal control and the changing role of internal audit”, Accounting, Auditing & Accountability Journal, Vol. 16 No. 4, pp. 640-61.
    pAuthor = "(?P<author>((([A-Z][a-z]+)|([A-Z][a-z]+-[A-Z][a-z]+)),\s([A-Z-\.]{1,8}\.)+((,\s)|(\sand\s)|(\s)))+)"
    pYear = "\((([2][0][0-2][0-9])|([1][9][2-9][0-9]))\)(,|\.)\s"
    pTitle = "(?P<title>(\")?[-/\sA-Za-z0-9,:'&]{10,150}?(\")?(,|\.)\s)"
    #pTitle = "(?P<title>(\")?[-/\sA-Za-z0-9,:]{10,150}?(\")?,\s)"
    #pTitle = "(?P<title>(\")?[-/\sA-Za-z0-9,:]{10,150}?(\")?,\s)"
    pJournal = "[&-,\.\sA-Za-z0-9]{3,}?,\s"
    pIssue = "[A-Za-z0-9\(\)\.\s]+[,\.:]\s"#"(V|v)ol\.\s[A-Za-z0-9\(\)\.\s]+,\s"#"[A-Za-z\.0-9\s]+,\s" #
    pPages = "pp\.\s[-0-9]{3,11}\." #"[A-Za-z0-9\.,\s-]+\."
    pattern = pAuthor + pYear + pTitle + pJournal + pIssue + pPages
    find = re.finditer(pattern, text)
    if find != None:    
        for item in find:
            #print "REGEXP", item.group(0), ":::"
            author = item.group("author")
            title = item.group("title")
            papers.append({"author": author, "title": title, "pattern": "a(y)t", "compare": makeCompareable(title), "pdf": pdfname})
            text = text.replace(unicode(item.group(0)), "xxxxxxxx")
    
    # books & rest
    # Birge, J.R., Louveaux, F., 1997. Introduction to Stochastic Programming. Springer, New York.
    pAuthor = "(?P<author>((([A-Z][a-z]+)|([A-Z][a-z]+-[A-Z][a-z]+)),\s([A-Z-\.]{1,8}\.)+((,\s)|(\sand\s)|(\s)))+)" #"(?P<author>((([A-Z][a-z]+)|([A-Z][a-z]+-[A-Z][a-z]+)),\s([A-Z-\.]{1,3}\.)+((,?\s)|(\sand\s)|(\s)))+)" #"(?P<author>(([A-Za-z-]+),\s([A-Z]\.)+,\s)+)"
    pYear = "(\(?)(([2][0][0-2][0-9])|([1][9][2-9][0-9]))(\)?)(\.|,)\s"
    pTitle = "(?P<title>[-\sA-Za-z0-9':]{10,200}(\.|,)\s)"
    pJournal = "[\(\),\sA-Za-z0-9-\./:']{3,}(,?)\s"
    pIssue = "[A-Za-z0-9\(\)\s]+\."
    #pPages = "[-0-9]{3,11}\."
    pattern = pAuthor + pYear + pTitle + pJournal + pIssue ##+ pPages
    find = re.finditer(pattern, text)
    if find != None:    
        for item in find:
            #print "REGEXP", item.group(0), ":::"
            author = item.group("author")
            title = item.group("title")
            papers.append({"author": author, "title": title, "pattern": "book", "compare": makeCompareable(title), "pdf": pdfname})
            text = text.replace(unicode(item.group(0)), "xxxxxxxx")
    
            
               
    return error, papers, text
    
def lengthOfDictItem(var, dict):
    length = 0
    for item in var:
        length += len(item[dict])
        #print (item[dict])
    return length
    
if __name__ == "__main__":

    print "-------------------- GET TEXT ---------------------"
    #text = GetText()

    files = listFiles("./pdfs") #os.listdir("./pdfs")
    #pprint(files)
    #raw_input()
    pdfs = []
    
    for number, item in enumerate(files):
        #print item
        #print item.lower()[-len(".pdf"):]
        if item.lower()[-len(".pdf"):] == ".pdf":
            pdfs.append(item)
    text = []
    for name in pdfs:
        extrakt = extractBibliography(name)
        #print name, "-"*15
        if extrakt == "":
            print "Fehler: Keine Bibliographie gefunden:"
            print "PDF", name
            #sys.exit()
        else:
            text.append({"pdf": name, "text": extrakt}) 

    print "Zahl der eingelesenen PDFS:", len(pdfs), "Länge:", lengthOfDictItem(text,"text")/1024, "KBytes"
    #pprint( text)
    print "-------------------- REPLACING WIRED CHARACTERS ---------------------"
    # split text
    for number, item in enumerate(text):
        text[number]["text"] = item["text"].replace("\r", " ")
        text[number]["text"] = item["text"].replace("\n", " ")
        text[number]["text"] = item["text"].replace(u"–","-")
        text[number]["text"] = item["text"].replace(u"”","\"")
        text[number]["text"] = item["text"].replace(u"“","\"")
        text[number]["text"] = item["text"].replace(u"’","'")
        text[number]["text"] = item["text"].replace(u"-","-")
        while text[number]["text"].find("  ") != -1:
            text[number]["text"] = item["text"].replace("  ", " ")
        # Ersetze ein komisches Ü
        text[number]["text"] = item["text"].replace(u" ̈ ", "e")
    # Ersätze xx- (zeilentrennungszeichen!)
    onehundred = len(text)
    last_percent = 0
    print "0 %"
        
    for number, pdf in enumerate(text):
        
        while True:
            #print "1"
            item = re.search("[a-z][a-z]-\s", pdf["text"])
            if item != None:
                endOfItem = item.end()
                
                #print cur_percent
                #print item.group(0), endOfItem
                #print text[endOfItem - 10: endOfItem + 10]
                pdf["text"] = pdf["text"][:endOfItem - 2] + pdf["text"][endOfItem:]
                #print text[endOfItem - 10: endOfItem + 10]
                #raw_input()
            else:
                break
        cur_percent = number/float(onehundred) * 100
        if cur_percent - last_percent >= 25:
            last_percent = cur_percent
            print int(cur_percent), "%"
            
    print "100 %"
    print "Zahl der verbliebenen eingelesenen Referenzenzeichen:", lengthOfDictItem(text,"text")/1024, "KBytes"
    #print text
    #sys.exit()
    print "-------------------- ANALYZING TEXT ---------------------"
    allPapers = []
    stringsNotFound = []
    numberRecognized = 0
    
    for number, pdf in enumerate(text):
        error, feedback, notFound = AnalyzeText(pdf["text"], pdf["pdf"])
        #print len(feedback)
        #raw_input()
        
        if error != 0:
            print "Fehler"
            sys.exit(1)
        for name in feedback:
            #print name
            allPapers.append(name)
            #sys.exit()
            #print name["title"]
        #raw_input()

        stringsNotFound.append({"pdf": pdf["pdf"], "text": notFound.split("xxxxxxxx")})
        numberRecognized += len(feedback)
    #if error == 0:
    #    pprint (feedback)
    
    #for item in papers:
    #    print item[2]
    print "Zahl der erkannten Referenzen:", len(allPapers)
    print "-------------------- REMAINING PAPERS NOT RECOGNIZED ---------------------"
    
    numberNotRecognized = 0
    for number, text in enumerate(stringsNotFound):    
        finalNotFound = []
        for i, item in enumerate(text["text"]):
            #print item
            #print item.strip()
            #print "-"*20
            tmp = item.strip()
            if len(tmp) > 12: # and tmp != "Bibliography" and tmp != "References":
                finalNotFound.append(tmp)
        #pprint(finalNotFound)
        stringsNotFound[number]["text"] = finalNotFound
        numberNotRecognized += len(finalNotFound)
    print "Zahl der nicht erkannten Teile:", numberNotRecognized
    pprint(stringsNotFound)
    #sys.exit()
    #xxxx was machen wir mit den not found dingen

    
    print "-------------------- REMOVING DUPLICATES ---------------------"
    
    notDeletedNumbers = []
    totalNumber = len(allPapers)
    for number1 in range(totalNumber):
        double = False
        for number2 in range(number1+1, totalNumber):
            #print number1, number2, totalNumber
            if allPapers[number1]["compare"] == allPapers[number2]["compare"]:
                double = True
                break
        if not double:
            notDeletedNumbers.append(allPapers[number1])
    #pprint(notDeletedNumbers)
    print "Zahl der doppelten Referenzen:", totalNumber - len(notDeletedNumbers)
    print "Zahl der verbliebenen Referenzen:", len(notDeletedNumbers)
    allPapers = notDeletedNumbers
                
    #xxxx das lower, replace etc. in ein weiteres
    #xxxx schauen, ob es pdfs gibt in denen keine referenzen gefunden werden
    
    print "-------------------- CHECKING EXISTING PAPERS ---------------------"
    
    numberBefore = len(allPapers)
    file = codecs.open("bibliography.bib", "r", "utf-8")
    lines = file.readlines()
    for number, line in enumerate(lines):
        if line[:len("title")] == "title":
            bibTitle = makeCompareable(line[line.find("{") + 1:line.find("}")].strip())
            #print "Suche", bibTitle,
            noPDF = False
            for i in range (20):
                # hat der Artikel auch schon ein PDF??
                if lines[number+i][:len("local-url")] == "local-url":
                    # alles super!
                    break
                if lines[number+i][:len("}")] == "}":
                    # wir haben die abschließende Klammer zuerst entdeckt -> also kein PDF hier
                    noPDF = True
                    break
            if noPDF:
                continue
            #print bibTitle
            # jetzt werden die gefundenen Referenzen durchgegangen, wenn ich die schon habe, dann wird die Referenz aus der Liste genommen.
            toDelete = None
            for number, newReference in enumerate(allPapers):
                ref = newReference["compare"]
                if ref == bibTitle:
                    # haben wir also schon
                    #print "gefunden"
                    #print bibTitle
                    toDelete = number
                    break
            #print
            if toDelete != None:
                #print "Deleted: ",
                allPapers.pop(toDelete)
    file.close()
    print "Zahl der gelöschten Referenzen:", numberBefore - len(allPapers)    
    print "Zahl der verbliebenen Referenzen:", len(allPapers)
    print "-------------------- GENERATING OUTPUT ---------------------"
    if len(allPapers) > 0:
        page = markup.page( )
        page.init( title="REMAINING NEW PAPERS", 
                   header="Links zu Google", 
                   footer="---------------" )
        page.br()
        for number, element in enumerate(feedback):
            #print element["author"],
            #print element["title"]
            link = "http://scholar.google.de/scholar?as_q=" + element["title"] + "&num=50&as_occt=title&hl=de" 
            page.a( element["author"] + ": " + element["title"] + "[" + element["pattern"] + "]", href=link)
            page.br()
        try:
            os.remove("output.html")
        except:
            pass
        f = open("output.html", 'w')
        f.write(page())
        f.close()
        
    
    #print page
        
    
    #pprint.pprint(papers)