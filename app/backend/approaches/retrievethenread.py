import openai
from approaches.approach import Approach
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from text import nonewlines

# Simple retrieve-then-read implementation, using the Cognitive Search and OpenAI APIs directly. It first retrieves
# top documents from search, then constructs a prompt with them, and then uses OpenAI to generate an completion 
# (answer) with that prompt.
class RetrieveThenReadApproach(Approach):

    template = \
"You are an intelligent assistant helping Accenture employees with their Microsoft Azure questions. " + \
"Use 'you' to refer to the individual asking the questions even if they ask with 'I'. " + \
"Answer the following question using only the data provided in the sources below. " + \
"For tabular information return it as an html table. Do not return markdown format. "  + \
"Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. " + \
"If you cannot answer using the sources below, say you don't know. " + \
"""

###
Question: 'Is Azure HDInsight GA in Poland?'

Sources:
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
"source12.txt" : "data\General availability_ Poland Central region added to Azure HDInsight _ Azure updates _ Microsoft Azure.html",

Answer:
Yes, Poland Central Region is added to Azure HDInsight and is generally available [source12.txt].

###
Question: '{q}'?

Sources:
{retrieved}

Answer:
"""

    def __init__(self, search_client: SearchClient, openai_deployment: str, sourcepage_field: str, content_field: str):
        self.search_client = search_client
        self.openai_deployment = openai_deployment
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field

    def run(self, q: str, overrides: dict) -> any:
        use_semantic_captions = True if overrides.get("semantic_captions") else False
        top = overrides.get("top") or 3
        exclude_category = overrides.get("exclude_category") or None
        filter = "category ne '{}'".format(exclude_category.replace("'", "''")) if exclude_category else None

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

        prompt = (overrides.get("prompt_template") or self.template).format(q=q, retrieved=content)
        completion = openai.Completion.create(
            engine=self.openai_deployment, 
            prompt=prompt, 
            temperature=overrides.get("temperature") or 0.3, 
            max_tokens=1024, 
            n=1, 
            stop=["\n"])

        return {"data_points": results, "answer": completion.choices[0].text, "thoughts": f"Question:<br>{q}<br><br>Prompt:<br>" + prompt.replace('\n', '<br>')}
