import openai
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
#from approaches.approach import Approach
from text import nonewlines


from azure.identity import DefaultAzureCredential

#openai.api_type = "azure"
#openai.api_version = "2023-03-15-preview"
openai.api_base = "https://cog-oaxatpknic6wq.openai.azure.com/"
openai.api_key = "a4afc38d3a6246d3b855a8adcca0d0f1"

endpoint = "https://gptkb-oaxatpknic6wq.search.windows.net"

model_name = "gpt-35-turbo"
deployment_name ="chat"
prompt = "Who is Charles Babbage?"

azure_credential = DefaultAzureCredential()

# Simple retrieve-then-read implementation, using the Cognitive Search and OpenAI APIs directly. It first retrieves
# top documents from search, then constructs a prompt with them, and then uses OpenAI to generate an completion 
# (answer) with that prompt.
class ChatReadRetrieveReadApproach(Approach):
    knowledge_base = {
        "source1.txt" : "data\Azure HDInsight for Apache Spark 3.3 is now available for public preview _ Azure updates _ Microsoft Azure.html",
        "source2.txt" : "data\Azure VMware Solution now available in North Switzerland _ Azure updates _ Microsoft Azure.html",
        "source3.txt" : "data\General availability_ Azure HX Virtual Machines for HPC _ Azure updates _ Microsoft Azure.html",
        "source4.txt" : "data\General availability_ Query performance insights for Azure Database for PostgreSQL – Flexible Server _ Azure updates _ Microsoft Azure.html",
        "source5.txt" : "data\Microsoft Azure Load Testing - additional Azure components for server-side monitoring _ Azure updates _ Microsoft Azure.html",
        "source6.txt" : "data\Public preview_ Add-on and node image in AKS release tracker _ Azure updates _ Microsoft Azure.html",
        "source7.txt" : "data\Public preview_ Assess impact of service retirements workbook template in Azure Advisor _ Azure updates _ Microsoft Azure.html",
        "source8.txt" : "data\Public Preview_ Azure Virtual Desktop Insights Powered by the Azure Monitor Agent _ Azure updates _ Microsoft Azure.html",
        "source9.txt" : "data\Public preview_ Confidential Virtual Machines (VM) support in Azure Virtual Desktop _ Azure updates _ Microsoft Azure.html",
        "source10.txt" : "data\Public preview_ Custom Image Templates for Azure Virtual Desktop _ Azure updates _ Microsoft Azure.html",
        "source11.txt" : "data\Public Preview_ GraphQL resolvers for Azure Cosmos DB, Azure SQL in Azure API Management _ Azure updates _ Microsoft Azure.html",
        }

        # ChatGPT uses a particular set of tokens to indicate turns in conversations
    prompt_prefix = """<|im_start|>system
        Assistant helps the company employees with their Microsoft Azure questions.
        Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below. If asking a clarifying question to the user would help, ask the question. 
        Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brackets to reference the source, e.g. [info1.txt]. Don't combine sources, list each source separately, e.g. [info1.txt][info2.pdf].


        Sources:
        [source1.txt][source2.txt][source3.txt][source4.txt][source5.txt][source6.txt][source7.txt][source8.txt][source9.txt][source10.txt][source11.txt]

        <|im_end|>"""

    turn_prefix = """
        <|im_start|>user
        """

    turn_suffix = """
        <|im_end|>
        <|im_start|>assistant
        """

    prompt_history = turn_prefix

    history = []

    summary_prompt_template = """Below is a summary of the conversation so far, and a new question asked by the user that needs to be answered by searching in a knowledge base. Generate a search query based on the conversation and the new question. Source names are not good search terms to include in the search query.

    Summary:
    {summary}

    Question:
    {question}

    Search query:
    """

    def __init__(self):
        self.search_client = search_client
        self.chatgpt_deployment = chatgpt_deployment
        self.gpt_deployment = gpt_deployment
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field

    def run(self, history: list[dict], overrides: dict) -> any:
        use_semantic_captions = True if overrides.get("semantic_captions") else False
        top = overrides.get("top") or 3
        exclude_category = overrides.get("exclude_category") or None
        filter = "category ne '{}'".format(exclude_category.replace("'", "''")) if exclude_category else None

        # STEP 1: Generate an optimized keyword search query based on the chat history and the last question
        prompt = self.query_prompt_template.format(chat_history=self.get_chat_history_as_text(history, include_last_turn=False), question=history[-1]["user"])
        completion = openai.Completion.create(
            engine=self.gpt_deployment, 
            prompt=prompt, 
            temperature=0.0, 
            max_tokens=32, 
            n=1, 
            stop=["\n"])
        q = completion.choices[0].text

        # STEP 2: Retrieve relevant documents from the search index with the GPT optimized query
    #    q = history[-1]["user"]
        if overrides.get("semantic_ranker"):
            r = self.search_client.search(q, 
                                            filter=filter,
                                            query_type=QueryType.SEMANTIC, 
                                            query_language="en-us", 
                                            query_speller="lexicon", 
                                            semantic_configuration_name="default", 
                                            top=top, 
                                            query_caption="extractive|highlight-false" if use_semantic_captions else None)
        else:
            r = self.search_client.search(q, filter=filter, top=top)
        if use_semantic_captions:
            results = [doc[self.sourcepage_field] + ": " + nonewlines(" . ".join([c.text for c in doc['@search.captions']])) for doc in r]
        else:
            results = [doc[self.sourcepage_field] + ": " + nonewlines(doc[self.content_field]) for doc in r]
        content = "\n".join(results)

        follow_up_questions_prompt = self.follow_up_questions_prompt_content if overrides.get("suggest_followup_questions") else ""
        
        # Allow client to replace the entire prompt, or to inject into the exiting prompt using >>>
        prompt_override = overrides.get("prompt_template")
        if prompt_override is None:
            prompt = self.prompt_prefix.format(injected_prompt="", sources=content, chat_history=self.get_chat_history_as_text(history), follow_up_questions_prompt=follow_up_questions_prompt)
        elif prompt_override.startswith(">>>"):
            prompt = self.prompt_prefix.format(injected_prompt=prompt_override[3:] + "\n", sources=content, chat_history=self.get_chat_history_as_text(history), follow_up_questions_prompt=follow_up_questions_prompt)
        else:
            prompt = prompt_override.format(sources=content, chat_history=self.get_chat_history_as_text(history), follow_up_questions_prompt=follow_up_questions_prompt)

        # STEP 3: Generate a contextual and content specific answer using the search results and chat history
        completion = openai.Completion.create(
            engine=self.chatgpt_deployment, 
            prompt=prompt, 
            temperature=overrides.get("temperature") or 0.7, 
            max_tokens=1024, 
            n=1, 
            stop=["<|im_end|>", "<|im_start|>"])

        return {"data_points": results, "answer": completion.choices[0].text, "thoughts": f"Searched for:<br>{q}<br><br>Prompt:<br>" + prompt.replace('\n', '<br>')}

    def get_chat_history_as_text(self, history, include_last_turn=True, approx_max_tokens=1000) -> str:
        history_text = ""
        for h in reversed(history if include_last_turn else history[:-1]):
            history_text = """<|im_start|>user""" +"\n" + h["user"] + "\n" + """<|im_end|>""" + "\n" + """<|im_start|>assistant""" + "\n" + (h.get("bot") + """<|im_end|>""" if h.get("bot") else "") + "\n" + history_text
            if len(history_text) > approx_max_tokens*4:
                break    
        return history_text 