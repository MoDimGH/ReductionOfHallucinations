
**Bremen University of Applied Sciences**

**Faculty IV: Electrical Engineering and Computer Science**

![](https://de.m.wikipedia.org/wiki/Datei:Logo_HSB_Hochschule_Bremen.png)

Exposé for a bachelor thesis on the topic:
--
How effective are various methods for reducing hallucinations in RAG-based enterprise applications?
====================================================================================================

| |  |
| ------------------------ | ------------------------------------------ |
| Study program:           | Dual study program Computer Science B. Sc. |
| Planned submission date: | 13.07.2025                                 |

Bremen, 25.04.2025

# Motivation and problem definition

Dataport AöR is the IT service provider for public administration in a total of seven federal states in Germany. Eight locations have now been established across the sponsoring states. Among other things, Dataport is developing the service portal<sup>[\[1\]](#footnote-1)</sup> for the City of Hamburg.

A chatbot is now to be developed for this purpose, with which users of the site can chat to find out general information about various city administration services. In the event that users provide the chatbot with sensitive data, this must also be processed by it. To ensure the security of citizens' data, the Large Language Model (LLM) for the chatbot is to be operated in the in-house data center. The aim is to use the most resource-efficient model possible to avoid excessive hardware costs.

It is essential for the added value of the application to prevent the occurrence of hallucinations, which occur all the more frequently in models with fewer resources. "Hallucinations in the context of LLMs usually refer to situations where the model generates content that is not based on factual or correct information. The occasional generation of outputs that appear plausible but are factually incorrect undermines the reliability of LLMs in real-world scenarios<sup>[\[2\]](#footnote-2)</sup>\[author's translation\] (Cheng Niu, 2025, p. 1) . To avoid most of the hallucinations that arise, "Retrieval-Augmented Generation" (RAG) is to be used for the chatbot. This means that documents with a similar context to the user's search query are retrieved and delivered to an LLM so that it responds based on external context and not on intrinsic trained knowledge

Nevertheless, various types of hallucinations continue to occur even with the use of RAG: (Wan Zhang, 2025)

- Answer contradicts the source's own statements (intrinsic hallucination)
- LLM supplements information that is not in the source (extrinsic hallucination)
- Answer contains factually incorrect statements (factual hallucination)
- LLM deviates from the task set ("Faithfulness Hallucination")
- LLM invents credible-sounding but false facts ("factual mirage")
- LLM reacts to an incorrect assumption in the prompt with a fictitious response ("Silver Lining")

# Current state of science and technology

## Methods for reducing hallucinations in RAG applications

The scientific literature describes numerous strategies for reducing hallucinations, including specifically in RAG applications. In this section, these techniques are presented, scientifically categorized and then evaluated based on their applicability in this work.

### Optimization of embeddings by fine-tuning the models for the specific domain

The models for embedding can be trained on domain-specific data (Yunianto, Permanasari, & Widyawan, 2020) . This can significantly increase the relevance of the retrieved documents. Since domain-specific data is available for this work, this method is feasible.

### Hybrid search (dense + sparse)

The combination of sparse (e.g. BM25) and dense (e.g. Sentence-BERT) models is an effective method for improving precision and recall for document retrieval (Priyanka Mandikal, 2024) . Sparse models primarily extract documents in which the query occurs exactly word for word, but neglect documents with similar context or synonyms to the contents of the search query. Dense models, on the other hand, more easily overlook documents in which the search query occurs word for word, but pay close attention to the context of the documents. The strengths of both are therefore combined here, so that as many correct documents as possible are retrieved, but as few irrelevant documents as possible. This method is well suited for this work, as the identification of services often involves word-based searches, but the context often needs to be considered, as users may ask questions without domain-specific prior knowledge.

### Reformulation of user queries (query rewriting)

By reformulating the user input, information retrieval can be significantly improved (Shengyu Mao, 2024) . This technology can also help RAG to increase the quality of the retrieved documents. As the implementation is very lightweight, this can be used well for the planned prototype.

### Data preparation through Q&A

To increase the quality of the retrieved documents, it is also advisable to pre-process the data (Kettunen, 2025) . To do this, an LLM can create a question-and-answer list for the content of the section once for each document or each block of information that has been completed in terms of content. This list would contain answers to questions that are commonly asked. This makes it easier for the embedding model to successfully match questions to the correct documents and retrieve them. This strategy is suitable for the prototype to be built.

### Set threshold for retrieval score

If the RAG system finds matching documents, but their context does not match the context of the user input very closely, the system should output "I don't know" instead of trying to generate an answer, or if few more closely matching documents could be retrieved, the answer should be based only on these. As this excludes less relevant documents, the possibility of misdirection of the answer generation by them is also eliminated and the accuracy of the answers increases. We achieve this by introducing a threshold for the confidence values of the retrieved documents (Radeva, Popchev, & Dimitrova, 2024) . This is also lightweight, so it is also suitable for this work.

### Fact checking through separate models

It is possible to check the answers of the RAG system for factual correctness using another system. For example, the open source system "Poly-FEVER" (Hanzhi Zhang, 2025) was developed for this purpose. This consists of 77,973 labeled factual assumptions in over 11 languages. However, it is not of great use for the system to be developed as Poly-FEVER deals with general topics, but the present use case is in the area of government services. However, with some technical effort, custom benchmarks can be created on the available data of the use case, and hallucination detection can be performed using tools such as RAGAS (Shahul Es, 2025) .

### Prompt engineering to avoid speculation

Certain instructions in the prompt (Pranab Sahoo, 2024) can be used to suppress speculative statements by the LLM so that the LLM always prioritizes the external knowledge of the retrieved documents higher than the intrinsic knowledge acquired through training. It makes sense to implement this in the prototype.

### Zero-Shot Chain-of-Thought Prompting (ZS CoT)

The more complex the user's prompt, the more difficult it is for the LLM to provide a correct, meaningful answer. However, chain-of-thought prompting enables complex reasoning by dividing the reasoning chain into individual, less complex steps. This is particularly useful for calculations. Dividing the answer finding process into several steps increases transparency, which gives users more confidence in the answer and makes it easier to understand the content of the answer. (Takeshi Kojima, 2025) describes how this can be achieved by adding "Let's approach this step by step" to the user's prompt. This can also be integrated into the prototypes of this work.

### "Sorry, Come Again" (SCA) Prompting

If the user's prompt has been formulated in a way that is somewhat incomprehensible or no content has been found, the LLM could ask the user questions and provide clarification (Vipula Rawte, 2024) . Special prompt templates can be used for this purpose. This is feasible in principle.

### Combine RAG with Knowledge Graphs

The combination of a RAG system with a knowledge graph (Nicholas Matsumoto, 2024) as an additional source of knowledge significantly reduces hallucinations. However, a complex system architecture is required for implementation, which is beyond the scope of this paper.

### Use of user feedback for fine-tuning

The model responses can be improved through user feedback (Yu Bai, 2024) . On the one hand, the model can be trained using "Reinforcement Learning from Human Feedback" (RLHF). On the other hand, it is also possible for users to mark hallucinations in the answer and for these to be transferred to a collection for cross-checking in future answers. This is feasible for this work

### Hyperparameter tuning

The generation quality of RAG applications can also be improved by systematically tuning the retrieval and model parameters (Matthew Barker, 2025) . This can be implemented by means of an experimental approach in this work.

## Methods for detecting hallucinations in RAG applications

This section presents current techniques for detecting hallucinations in RAG applications and evaluating the reduction of hallucinations. The methods are scientifically classified and then evaluated based on their applicability in this work.

### LLM-as-a-Judge

In order to check the generated answers for coherence, factual accuracy and consistency, a powerful language model can be used as an evaluation instance. Examples include SelfCheckGPT (Potsawee Manakul, 2023) , G-Eval, Prometheus, Lynx or Trustworthy Language Model (TLM). A comparison of the different models was carried out by (Sardana, 2025) . This approach is well suited for this project, as no ground truth answers are given and the evaluation of the answers by humans would be too time-consuming. However, the quality of the assessments depends heavily on the assessment model used.

### Comparison with ground truth / human gold standard

Tools such as REDEEP (Zhongxiang Sun, 2024) and LibreEval (Research, 2025) make it possible to create your own benchmarks based on domain-specific documents. The aim is to measure metrics such as faithfulness, answer correctness or precision. The generated answers can then be compared with known, verified statements for the purpose of evaluating hallucinations. Even if the creation of benchmarks is time-consuming, hallucinations can also be recognized and possibly even mitigated in a domain-specific context. This makes it suitable for this project.

### Man-in-the-loop / Feedback

After going live, the RAG system can continue to be optimized based on user feedback (Yu Bai, 2024) . For this purpose, a functionality can be introduced that allows end users to mark hallucinations in answers or rate the answer based on its factual accuracy. In this way, the model can be trained using RLHF. This involves some technical effort, but is very practical for business applications.

### Automated metrics at retrieval level

The relevance and coverage of the retrieved documents can already be assessed at the retrieval level using tools such as RAGAS (Shahul Es, 2025) , REDEEP and reranking (e.g. with BERT (Koroteev, 2021) ). This involves checking whether the respective document proves the answer and evaluating metrics such as similarity scores, coverage or faithfulness. This can be very useful for the prototype to be developed in order to optimize the retrieval process, as no manual annotations are necessary here. However, automatically generated retrieval benchmarks can also be used here for continuous evaluation.

# Objective of the work

The aim of this bachelor thesis is the prototypical development of a domain-specific chatbot for the city of Hamburg's service portal<sup>[\[3\]](#footnote-3)</sup> based on the principle of "Retrieval-Augmented Generation" (RAG). The focus here is on reducing hallucinations in the generated answers. To address this challenge, selected measures to avoid hallucinations are integrated, tested and evaluated.

The first step involves the automated procurement and processing of relevant content from the publicly accessible areas of hamburg.de. This data will be merged into a knowledge database and a RAG pipeline will be implemented on the basis of this, in which a selection of easy-to-implement methods for hallucination avoidance will be integrated, including:

- Data preparation through Q&A generation
- Hybrid retrieval (sparse + dense),
- Threshold-based filtering of irrelevant documents
- Various methods of prompt engineering to avoid speculation

The aim is to investigate the effectiveness of these approaches with regard to the reduction of different types of hallucinations. For this purpose, suitable evaluation metrics are defined and automated evaluation procedures (LLM-as-a-Judge or RAGAS) are used for analysis. The evaluation is carried out using generated realistic test scenarios.

The focus of the work is on building a functional prototype that is both technically functional and methodologically meaningful enough to evaluate the effectiveness of individual hallucination reduction strategies in the context of a domain-specific use case. The aim is not a generally valid comparison of all theoretically possible approaches, but rather a proof of concept for the effectiveness of selected, practicable measures in the context of a specific application situation.

# Methodology and work planning

## Work planning

The focus of the implementation is on the technical realization of a RAG-supported chatbot for answering citizens' questions on the basis of publicly available administrative documents and on the evaluation of various methods for reducing hallucinations in the generated answers.

1. Data acquisition & preparation
    1. Scraping relevant content from hamburg.de/service and any related pages
    2. Pre-processing of documents (formatting, filtering)
    3. Q&A generation for structured information processing
2. System architecture & implementation
    1. Configuration and integration of a RAG system incl. vector database
    2. Implementation of a simple user interface for interaction
3. Evaluation preparation
    1. Selection and implementation of suitable benchmarking methods for hallucination detection (RAGAS, LLM-as-a-Judge)
    2. Creation of domain-specific metrics and ground truth data
4. Test runs & comparison
    1. Execution of test series with various optimization strategies (Q&A data preparation, hybrid search, prompt engineering, thresholds)
    2. Comparison of the systems based on qualitative and quantitative criteria
5. Documentation & evaluation
    1. Analysis and presentation of the results
    2. Reflection on the feasibility and effectiveness of the methods used
    3. Composing the written Bachelor thesis

## Scheduling

| week | Task |
| --- | --- |
| 1   | Data acquisition (scraping) and pre-processing |
| 2   | Q&A creation, development of the knowledge database |
| 3   | Implementation of the RAG pipeline, initial tests |
| 4   | UI development, expansion to include optimization methods |
| 5   | Preparation of the evaluation (metrics, test data, benchmarks) |
| 6   | Test runs and comparison of the methods for hallucination reduction |
| 7   | Evaluation, analysis, creation of figures and tables |
| 8-9 | Writing, fine-tuning and submitting the Bachelor's thesis |

## Work environment (e.g. technical infrastructure - HW/SW, test data)

Hardware:

1. Development on local computer
2. Use of cloud instances if necessary

Software and tools:

1. Python,
2. Postgres vector database
3. Streamlit for UI prototype
4. Github for version control
5. Access to LLM API

Test data:

1. Generation of own benchmarks for evaluation on the basis of publicly accessible content from the hamburg.de/service website

# Preliminary structure

1. Introduction
    1. Problem definition
    2. Objective of the work
    3. Structure of the work
2. Theoretical foundations
    1. Retrieval Augmented Generation (RAG)
    2. Hallucinations in LLM editions
    3. Methods for reducing hallucinations
    4. Overview of existing RAG-based systems in the context of public authorities
3. Requirements analysis and system design
    1. Use case: Citizen inquiries based on public administration information
    2. Requirements for data sources, security and timeliness
    3. System architecture and component overview
4. Implementation of the prototype
    1. Data acquisition and pre-processing (scraping, Q&A generation)
    2. Development of the RAG pipeline (retriever, LLM, vector database)
    3. Implementation of the user interface
5. Methods for hallucination avoidance and detection
    1. Retrieval optimization (hybrid search, filter)
    2. Prompt engineering and context restrictions
    3. Confidence metrics and evaluation procedures (e.g. RAGAS, LLM-as-a-Judge)
    4. Evaluation concept and test design
6. Evaluation and results
    1. Description of the test data and scenarios
    2. Comparison of the methods used
    3. Discussion of the results
    4. Boundaries and limitations
7. Conclusion and outlook
    1. Summary of the work
    2. Assessment of target achievement
    3. Outlook on further developments and potential for practical use
8. Appendix
    1. Illustrations, code snippets, configuration files
    2. List of sources
    3. Affidavit

# Bibliography

Cheng Niu, Y. W. (17. 04 2025). _RAGTruth: A Hallucination Corpus for Developing Trustworthy._ Retrieved from <https://arxiv.org/pdf/2401.00396>

Hanzhi Zhang, S. A. (25. 04 2025). _Poly-FEVER: A Multilingual Fact Verification Benchmark for Hallucination Detection in Large Language Models._ Retrieved from <https://arxiv.org/abs/2503.16541>

Kettunen, N. (2025). _Development of a framework for pre-processing domain-specific data using a technical language processing approach._ Retrieved from <https://lutpub.lut.fi/handle/10024/168926>

Koroteev, M. V. (22. 04 2021). _BERT: A Review of Applications in Natural Language Processing and Understanding._ Retrieved from <https://arxiv.org/abs/2103.11943>

Matthew Barker, A. B. (25. 2 2025). _Faster, Cheaper, Better: Multi-Objective Hyperparameter Optimization for LLM and RAG Systems._ Retrieved from <https://arxiv.org/abs/2502.18635>

Nicholas Matsumoto, J. M. (3. 6 2024). _KRAGEN: a knowledge graph-enhanced RAG framework for biomedical problem solving using large language models ._ Retrieved from <https://academic.oup.com/bioinformatics/article/40/6/btae353/7687047>

Potsawee Manakul, A. L. (15. 04 2023). _SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models._ Retrieved from <https://arxiv.org/abs/2303.08896>

Pranab Sahoo, A. K. (5. 2 2024). _A Systematic Survey of Prompt Engineering in Large Language Models: Techniques and Applications._ Retrieved from <https://rotmandigital.ca/wp-content/uploads/2024/09/A-Systematic-Survey-of-Prompt-Engineering-in-Large-Language-Models.pdf>

Priyanka Mandikal, R. M. (8. 1 2024). _Sparse Meets Dense: A Hybrid Approach to Enhance Scientific Document Retrieval._ Retrieved from <https://arxiv.org/abs/2401.04055>

Radeva, I., Popchev, I., & Dimitrova, M. (2024). _Similarity Thresholds in Retrieval-Augmented Generation._ Retrieved from <https://ieeexplore.ieee.org/abstract/document/10705214?casa_token=eQ-r5Pc63ccAAAAA:VOYjoH0fEsfbclOgfU-NBZ63l7Qb64FLHtK9hsoLMpz76obf5NmnVye8dvf8xVOmGN5fhjMVOQ>

Research, A. (25. 04 2025). _LibreEval: The Open-Source Benchmark for RAG Hallucination Detection._ Retrieved from <https://arize.com/llm-hallucination-dataset/>

Sardana, A. (4 2025). _Real-Time Evaluation Models for RAG: Who Detects Hallucinations Best?_ Retrieved from <https://www.researchgate.net/publication/390247766_Real-Time_Evaluation_Models_for_RAG_Who_Detects_Hallucinations_Best>

Shahul Es, J. J. (25. 04 2025). _RAGAs: Automated Evaluation of Retrieval Augmented Generation._ Retrieved from <https://aclanthology.org/2024.eacl-demo.16/>

Shengyu Mao, Y. J. (23. 5 2024). _RaFe: Ranking Feedback Improves Query Rewriting for RAG._ Retrieved from <https://arxiv.org/abs/2405.14431>

Takeshi Kojima, S. S. (25. 04 2025). _Large Language Models are Zero-Shot Reasoners._ Retrieved from <https://arxiv.org/abs/2205.11916>

Vipula Rawte, S. T. (27. 4 2024). _"Sorry, Come Again?" Prompting -- Enhancing Comprehension and Diminishing Hallucination with \[PAUSE\]-injected Optimal Paraphrasing._ Retrieved from <https://arxiv.org/abs/2403.18976>

Wan Zhang, J. Z. (17. 04 2025). _Hallucination Mitigation for Retrieval-Augmented Large Language Models: A Review._ Retrieved from <https://www.mdpi.com/2227-7390/13/5/856>

Yu Bai, Y. M. (21. 6 2024). _Pistis-RAG: Enhancing Retrieval-Augmented Generation with Human Feedback._ Retrieved from <https://arxiv.org/abs/2407.00072>

Yunianto, I., Permanasari, A. E., & Widyawan, W. (1. 12 2020). _Domain-Specific Contextualized Embedding: A Systematic Literature Review._ Retrieved from <https://ieeexplore.ieee.org/abstract/document/9271752?casa_token=SpIZDtY_vkQAAAAA:mlX3j-xotQTG0Q8nkdMh7Me_Nvg8jXZ5O1CeSU0M_rdLAXvWX96p6QerkENs8Zq1WrsxexQEmQ>

Zhongxiang Sun, X. Z. (15. 10 2024). _ReDeEP: Detecting Hallucination in Retrieval-Augmented Generation via Mechanistic Interpretability._ Retrieved from <https://arxiv.org/abs/2410.11414>

1. <https://www.hamburg.de/service> (Last accessed: 04/17/2025) [↑](#footnote-ref-1)

2. Hallucination in the context of LLMs usually refers to a situation where the model generates content that is not based on factual or accurate information \[...\]. The occasional generation of outputs that appear plausible but are factually incorrect significantly undermine the reliability of LLMs \[...\]. [↑](#footnote-ref-2)

3. <https://www.hamburg.de/service> (Last accessed: 04/17/2025) [↑](#footnote-ref-3)
