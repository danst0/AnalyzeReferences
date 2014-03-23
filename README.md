AnalyzeReferences
===

From the article ([http://scrmblog.com/review/creating-a-reference-tree-from-an-existing-pdf-collection](http://scrmblog.com/review/creating-a-reference-tree-from-an-existing-pdf-collection))


I am currently in the Snowballing Phase of the Systematic Review approach (explained here). So I already have accumulated a amount of papers (most of them as PDF files) for my current research goals using a keyword search on several databases (Econis, EBSCOhost and ScienceDirect, etc.).

Problem
---

Now I thought about how to proceed with the analysis of the references mentioned in the papers I already found. I was afraid, that the amount of work necessary, to make a manual analysis of all papers available in my library and manually would be just overwhelming.
My calculation was as follows: My library for this goal consists of 200+ papers, let’s assume each with 15 references, thereof seven already in my library. From the remaining eight references per paper, three are going to be relevant for my research.

So in sum I would have to screen over 3000 references (for relevance for my research goal and for existence in my library) and have to manually copy and paste 600 papers into a database search engine.
Even if I am very fast it sounds like hours of monotone, uninteresting labor.

Solution
---

Usually in those situations I try to rely on the internet to help me with a tool, but after I made a thorough search I did not find anything which could help me with my problem.

So at the moment I am reactivating my Python skills and learning something about regular expression to turn something from a PDF into a list of author-year-title-combinations which can be automatically compared to my existing library (using Papers) and made into a search query at Google Scholar or a similar database.
Status

At the moment I am making good progress with the core pattern matching. The open questions are how to read from the PDF files and how to compare the results to my existing library (using title and author or only title).
I will post update.

Future work could then analyze the possibility to create a reference tree connecting the literature within a library to show “connections of thought” between them.