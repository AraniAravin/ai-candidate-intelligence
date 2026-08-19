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

## Day 7 - Review Work Done in Week 1 
A good understanding of how semantic similarity works and how the CV text and JD will be compared should verified.

## Day 8 — Vector Databases & Qdrant

## what is a vector DB
A Vector DB is a way of storing data where the retrieval does not require exact texts to match but the meaning. DBs like PostgreSQL and MySql store structured data and the retrieval of the data requires exact keyword mathces, but in QDrant which is the vector DB used here we store the vectors of the content needed to be stored (CV text) and pass the JD embedding to match the results to be retrieved from the Vec Db, in that way we dont just match keywords but search for the meaning of the word.
## What is top K retrieval
When pulling data from the DB, we pass a limit to QDrant to return top x number of candidates who match the JD, which is called top-K retrieval. What QDrant does here is take both the JD and CV vectors stored in that collection and compute their similarity and rank the results based on the scores and return the top K results 

In Vec Db collections are like tables of a traditional Db, and points are like rows of the table, representing one entry in the data structure and payload is a extra meta data stored along side the vector, this is a human readable form of the data stored and why we need is unless this exists QDrant is not aware what data it is passing over.

Also remember that Qdrant API expects plain lists only not numpy and upsert means insert or update

## Day 9 — Vector DB CRUD

## Why do we need an interface structure?
Why we have this interface structure is, for the vector_store.py to act as a service module and this is the structure compliant with FastAPI which will come into the picture next week as its routers will call the necessary functions, a router handler receiving an upload will call the insert_candidate() etc.

## What is the plan for ID later..
The plan for IDs for the week will be once a structured Db like postgresql is created and candidate details will be stored in it firstly, generating a unique primary key for each record, which will be a single source of truth for IDs, which will be stored as the point number for the vector in QDrant in that way the data in both the DB can be kept on sync and no more manual working on it - 
The Problem we are trying to solve here is if we run the script everytime for the data to be stored or deleted, and suppose two people upload their CVs twice and the data gets overwritten (further discussed in debugging stage below) to avoid this edge case we are using this approach.

## Debugging Results
when trying to insert the same id for the point numbers I expected same number to get inserted but the actual results were the data was getting overwritten and previously inputted data getting pushed back like data gets overwritten to 1 and previous data go like 2.. 3...

When considering the file of documents in a folder this is now the name split works
cv_path = Path("data/cvs/john_doe_resume.pdf")
cv_path.name → "john_doe_resume.pdf" (full filename with extension)
cv_path.stem → "john_doe_resume" (filename without the extension)
cv_path.suffix → ".pdf" (just the extension)

And why delete operation matters here is in case a recruiter decides to delete a JD or a candidate withdraws a CV it should be withdrawn from the DB as well

As we have done in Day 6 approach at that point state management (insert/update/delete) is not necessary as we recompute everthing from scratch each time. But as data grows we cannot do this all the time, so real databases seperate computation from storage, data is persistent there and that is why we need CRUD Operations as reliable primitives rather than smthing you improve using python lists.

## Day 10 — RAG (Retrieval-Augmented Generation)
R - Retrieval - pulling the necessary context from a vector database 
A - Augmented - passing it to the LLM for knowledge
G - Generation - the output will be generated with the augmented context without hallucinations

Remember RAG is an architecture of operation

## Why Grounding reduces hallucination?
without grounding the LLM will hallucinate over something it doesnt know so this technique provides the materials for it to look into and answer 

## Difference between thin context and richer context
When cv text was passed in as context to the LLM prompt a richer output was produced with justification of why a candidate is better suiting than another and a critical evaluation between candidates and who suits the role more. 
Moreover, the results produced with different contexts were different, there is a difference of candidates chosen depending on the context.

## Debugging
When asking the same question 2 times the answer given is the same and the scores generated are also same which is expected as we compute the cosine similarity using the same formula and the LLM will use the scores to clasify the ranking

While tracing the LLM output with the given text two outcomes were found firstly there isnt much context given just the scores and so the LLM only speaks abt the scores which is expected no hallucination there. Secondly when passing the cv text and getting the LLM output most of the details stated are able to be traced and therefore it confirms that the LLM is only speaking the details it knows and grounding works well here and no imaginary text

## Day 11 — Targeted RAG vs Generic RAG

We have two different retrieval pattern in this project:
1. Open ended similarity search - pass a question and ask Qdrant to search for a similar candidate
2. Direct retrieval - what we have done for the day, pass the name of the candidate and ask Qdrant to retrieve

In this context we are passing the question with the answer and asking for an explanation from the LLM, for which a similarity search is not necessary as in the previous week we have already done the semantic search where we pass the question to the vector DB which searches the matching candiates for the whole here all we need is the explanation so we dont need to search meaning but instead the data itself like how we do in traditional SQL servers

When a poor candidate is tested the LLM is honest with its answer and provides a justification for its results.

## Debuggings

Right now for the direct retrieval logic from QDrant what we do is use 'client.scroll(limit=1000)' in the search candidate by name function, which pulls over 1000 matching candidates over to the script and then manually loop through them to find the right match, which is actually a poor implementation as it contradicts with the whole idea of using a vecDB as we bring in the whole brute-force Python loop logic again which was meant to be resolved by Qdrant from day 8 as it has proper mechanism to find the exactly listed points, currently it wont be an issue for 5 10 candidates but when it grows to 1000s it will cause a scaling issue (redundancy huge unnecessary data over the network and CPU cycle). 
So why we are doing this right now is until we introduce postgresql which is the real retriever of direct data we have this as a option as we do not want to repeat the same logic for both the DB.

When testing a poor fit candidate for the role the LLM is being honest and listing out the missing skills and what the candidate is good at.

The scores shown in the day 6s work, where we compute the cosine similarity for each candidate and the title is matching with the output of the LLM for the high ranked candidates it gives a positive response and else if gives out why they are not a good fit, it is expected as if the texts are matching only the similarity rate will be high and matching.

When we ask for details about a non existent candidate the answer is no match found which is expected


## Day 12 — FastAPI Fundamentals
API is an intermediary layer used for communcation between layers, in this case the FE and BE.

An endpoint is a specific URL path your API responds to, to send or receive data, it calls onto a specific function to get an input and to perform a task and give an output based on it.

HTTP is a set of protocal used when passing data over the internet (Web Request).

Every Web request has a method (kind of action) and path (which resource), web response comes back with a status code (400,500,200) and a body (Json)

Two methods exists here GET is used to receive something from the server and POST is to add something to the server.

Pydantic is a python library used for data validation, it is used to avoid data mismatch errors later and catch them earlier before even running the logic. how it works it by getting the json input and FastAPi validates the format against the defined pydantic model and if it passes validation we are good to go else we get a clear error message instead of crashing deep inside yur function.

Data was getting stored in two forms here one local in-memory data as a python dictionary or list (Job description, Candidates details) and the other to the QDrant (Analysing candidate information and storing them and for direct retrieval of the candidate from the Db for ranking explanation).

## Debuggings
When the json structure that is being passed as an input for example in the post/jobs api before the function is even called and crashes midway, the error message is thrown, which is the benefit of the pydantic model.

When we try to upload a CV that is non existent there is a error message thrown. 

## Day 13 — Error Handling in a Multi-Step AI Pipeline
per-item error handling is crucial, if not in cases where one item fails then the rest of the items in the batch is blocked and is not processed after end point crashes, after implementing the try/exception handling and maintaining a list for the failed items it is more easier to keep tract of CVS that failed as we know failure can happen in two ways, when the CV pdf is not proper and next is when we dont get a proper json reponse from the LLM

GET /candidates/status - is very helpful in understanding the status of the CVs uploaded/analysed/failed

Earlier when we did not check if the extracted text from candidates really did extract or not and call for the LLM response, it was not handling edge cases when an image or broken pdf was passed over and was returning an empty json and was storing empty data to the VecDB, now after adding 'cv_text.strip()' function that is handled as only if a proper CV pdf is passed then it gets analysed or is classed as failed doc.

In the /candidates/analyze endpoint we have a status check 'if record["status"] != "uploaded": continue' which was added to avoid reanalysing candidates we have already analysed but then this also skips retrying candidates who have failed already, two options exists one is implementing a logic asking the candidates to re upload a different file and a much simpler option is to change the if logic so that we retry candidates who have failed before mayb due to a Json truncation issue, which is non deterministic since LLM output varies run to run, or a Qdrant hiccup, FOR NOW THE CHANGE IS NOT MADE

When the DB is down and we send a request the try catch blocks catch the error and handle them well displaying the correct error which shows the robustness of the error handling mechanisms implemented

## Day 14 — Full Pipeline Integration
Todays final building block was ranking candidates for a specific job description and now the whole pipeline is ready.
First we have to upload a JB 
The upload the candidate CVs
Analyse the candidate CVs and update Vector Databases
Produce ranking based on specific JDs
RAG chat - answering questions related to the ranking.

## Debuggings
When a job id which is non existent and is searched, an empty array is returned currently with no error message which is handled to throw a 404 error and a message indicating the missing job id.

currently there is an issue with uploading CVs and JD there is a word count limitations when we upload a long cv or long description we have json truncation issue that needs to be handled some time soon, mayb we need to handle to thru the model olama

Found a real scoping gap: search_candidates() searches ALL candidates ever inserted into Qdrant, not just ones relevant to a specific job — meaning stale test data from earlier days was polluting rankings.
Immediate fix: cleared the Qdrant collection to remove stale test data.
According to the real design it will be a job-scoped search in this scenario so we have to wait till postgresql is wired in to associate a job is to a candidate it, as a permanent fix for this

## Day 15 — Database Design & SQLAlchemy
The database designing is done here deciding what are the tables and columns in it and how they are going to be related as a system for data flow.
The relashionships between the tables will be:
One to many  - like one job connecting to many application 
many to many - like many candidates connecting to many skills, a join table is required for this joining the skill id and candidate id and so it does not have a seperate id 

SQL Alchemy is a python library that allows tables be to be defined as classes called an ORM - Object Relational Mapper, instead of writing raw sql output. You can access fields like candidates.names than writing a select query,is also allows us to connect to the Database and translating our python operations to SQL under the hood

## Day 16 — FastAPI + PostgreSQL Integration
In the database.py file a get_db() function was added as a dependency injection method, where the fast API calls the method through the Depends(), before the end point runs in that way gets a db session, hands you the session and closes it after wards. This avoids manually opening or closing a db connection in every single route.

Within the skills table, we need to make sure we do not duplicate the skills entered into the table, therefore each time before entering a skill we need to check if it exists and if not insert the skill. This is a common real world database problem called 'create or get'.
Each time a candidate with similar skills are uploaded they are connected through the candidate skills join table.
When uploading a CV the data is only inserted to posgresql id created then and when analyzing candidate the rest of the data is added and then the data is added to the vector database, maintaining the same IDs in both db for consistency. 

## Debuggings
The get_or_create_skill() has a db.flush() instead of db.commit() which other crud operations have, so to push the pending changes to the skills table (every skill gets an id) but not fully commiting as it will be done within the save_extracted_info(), which keeps skill creation and candidate details uploading one atomic transcation, preventing any data being half saved if anything goes wrong in the overall operation.

When a broken pdf is uploaded and when analysed the correct error response is given and also stored in the candidates db, through this it confirms that failed candidates and the reason for failure also persisted in the db

## Day 17 — Job Persistence & Data Serialization
For the candidate skills we are storing them into a table and combining them as a candidate_skills many to many join table and using them, so having commas in them is not a matter of fact.
But for the job skills we are not having a seperate job skills table but instead we store them as a combined comma joined string in the jobs table and then split it (using the comma as a delimiter) to a list whenever necessary.
The issue with this will be when having a skill like "Databases (MySQL, PostgreSQL)" when splitting the list it will get split to two skills though it is one single skill, the comma cannot be distinguised as a skill seperator or part of the item after combining to a list.

The reason for this is yet we have not considered the use case of finding jobs based on skills we are only thinking of collection candidates based on the skills at this point.

This is not yet a proven bug, but is worth noting as a point which could be considered fixing for the future - maybe by building a job skills table mirroring candidate skills, to ensure consistency.

## Day 18 — React Fundamentals

React is  javascript library which helps in building a webpage, each component of this will be an interactive UI, such as a button, card etc.
A component - Javascript function that returns a UI
JSX - HTML looking syntax but written directly inside javascript, the code gets compiled into javascript but written in markup language
Props- how a parent component will pass data into a child component
State - data can change within a component, and when it does, react automatically re renders the UI to display the new data. 
useEffect- a hook for running code when a component reloads or a value changes. This is how we get the jobs listed in the UI as soon as we load the page. 

CORS is protecting an endpoint from malicious access, therefore, when deliberating breaking the cors, an error telling access to the BE endpoint cannot be accessed as requests from our FE origin has been blocked.

## Day 19 — Conditional Rendering & Cross-Cutting Changes
An end point was created for selecting a candidate by the id, it was for the purpose of being able to select a ranked candidate and get to know further details about them.

selectedCandidate state was used to keep track of the data displayed about a particular candidate, selectedCandidate is updated in two places: cleared to null whenever the 
job role changes (since the ranked list is now different), and set to 
the fetched candidate data whenever a row is clicked.

Currently the ranked candidates list returned from Qdrant only has the name and score, but for us to pull out for details from postgresql, which isnt available in QDrant, we need the id of the candidate so we had to receive the parameter in the output list and make changes to functions that are related to it.
This is a good lesson that grep searching for a functions usages before updating its signature is a real habit worth building.

## Day 20 — Skill Matching & Combining Deterministic + AI Logic
Python sets were helpful in the skill matching and difference for the jobs and candidates, as both exists as lists, they have the direct syntax which we can use as a&b for intersection and a-b for difference.

Case sensitivity of the skills is an important consideration as a skills could exist as 'python' or 'Python', a naive set matching  treats them as different skills therefore it needs to have them in the same case which can be done using the in built function of python.

In the feature introduced for the day where we have the matching missing skills and explanation of the ranked candidates, there is a mix of data within the response displayed, part of it displayes the skill matching and missing, score which is generated by python( deterministic data,dast and 100% reliable ) and the rank explanation is provided by the LLM, as we do not need an LLM in every aspect of a project (use it where it adds value), only in necessary instances like Natural language reasoning. 
It is a legitimate design choice not a short cut


