# Concepts — Day 1

## What are embeddings?
for the purpose of machines understanding human languages, numerical vectors of words or phrases are created. And based on the closeness of vectors we can determine if they are similar or not


## Why are embeddings useful for this project?
we can compare the job description to the candidates skills section and identify if the candidate has a good match to the job in that way we can find a suitable candidate

## What is cosine similarity, and why use it over other distance measures?
Cosine similarity is a way determing the similarity of the words betwen sentences, like if we take 4 reviews of a movie 3 will be positive and  will be negative using the cosine similarity we can find which are the positive ones and negative ones. When we take two sentences a way of calculating the cosing similarity is by:
1.  adding a table for all the words and counting the occurences first
2. Plotting to a graph and drawing vectors
3. the angle between the two will be determined and the cosine of that will determine the cosine similarity
4. when we have sentences with more number of words how we get the cosine similarity is by using the formula
5. This is useful over other methods due to its unique approach of finding similarity of text that are not completely same as it only works for key work matching

## Observations from my experiment
When the text in CV description is changed and based on its relevance to the Job description text the cosine similarity changes and when we add the same text then the cosine similarity is 1.0 suggesting a 100% match and by using words like 'React' the similarity is like 0.09.

# Concepts — Day 2

## What are sentence transformers?
It is a library of hugging face, which converts sentencers into vector embedding which can be easiy passed to find the cosine similarity to understand the best match of a candidate to the JD

## Pretrained Embedded Models
There are various pretrained embedded models to do the vector embeddings on the sentences so that we do not have to do the training and validation from the beginning of the cycle. We have already used a model called 'all-MiniLM-L6-v2' which is a small lightweight model performing simple actions and the shape of it is (384,) meaning 384 numbers will be used to represent a sentence. There are other embedding models that give other dimensions

## Vector Dimensions
But when we try to match two vectors it needs to be in the same dimenstions also to be passed to cosine similarity

## Day 3 — PDF Text Extraction
PDF - page description format
Unlike the other types of text files like docx and .txt which store a linear stream of text, pdfs only store the instructions for where to draw each character, line or image on a page. Therefore extracting the text is harder as it means reconstruction of the text.

PyMuPDF is a python library used to extract, modify or render any text from pdf and if it is a scanned pdf or image the extraction will not work currently and if the layout is not correct the order of the text will get messed

Document Parsing is a way of structuring raw and messy text pulled out from pdf, scanned images or word documents for computers to understand. But in this project that will be done by an LLM as part of the last steps 