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

## Day 4 — Structured LLM Extraction

Generally when we get outputs from LLMs we get it in a specific format not out desired format getting it in our preferred format is associated with how we write the prompts to get the output from the LLM

In here we are expecting an output in the json structure from the LLM so that we use the json.load() command in python easily to load the model

In the prompt we are giving the role of the LLM and what we are expecting from it as an output and then we give the structure of the outputted elements to be retrieved from the raw text.
We also make sure to handle edge cases by giving the rules, such as in situations like when we cannot deduce the number of year we return it as null instead of fake numbers, not prediction of data if data does not exist it will be given as null.

The issues faced were in some resume templates though it was in pdf form not all skills got extracted at first and then when the format of the resume with a different layout was given then most skills were extracted, but even withing the CV format some skills are not retrieved and if the skills section name is having synonymous words still the skills are not extracted.

## Day 5 — Job Profile Extraction

From Day 1's learning it is confirmed that we do not need a structured output for the JD as it is already compact in size and so we can make embeddings and find the similarity but later on in the project we will be doing skill-overlap match for which we need a set of skills to match with the candidate skills and not just plain vectors are enough for it.

Both semantic matching and explicit matching will be required later when we start building a dashboard.

An issue was found with the earlier prompt where the bonus skills were also found to be considered as required skills by the LLM and therefore the prompt was modified to handle edge cases and consider any bonus or preferred skills as it is and another change was found when the LLM considered soft tone skills as preferred so that was also handled.

Some real LinkedIn JD was tested out, it gave out adequate but not very impressive results, when the format of the JD was changed some skills which are not mentioned under any 'skills' heading was not considered a skill

## Day 6 — End-to-End Pipeline

All the functionalities implemented in the beginning of the week was incorporated into one pipeline to do the task of CV ranking. Where the CV raw text was extracted and embeddings was calculated for them and then embeddings was created for JD and similarity score found using cosine similarity and candidates were ranked based on that.

The JSON structure extracted was not put to use in this pipeline, as for embedding the raw text is only necessary, but it was experimented as it will be necessary for skills matching in the later weeks.

Already created functions from other modules were imported and used in the pipeline as it is an easier way of managing the system design than redundantly repeating code within the same project.