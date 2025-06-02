from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient


def google_search(query: str, num_results: int = 2, max_chars: int = 500) -> list:  # type: ignore[type-arg]
    import os
    import time

    import requests
    from bs4 import BeautifulSoup
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        raise ValueError("API key or Search Engine ID not found in environment variables")

    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": search_engine_id, "q": query, "num": num_results}

    response = requests.get(url, params=params)  # type: ignore[arg-type]

    if response.status_code != 200:
        print(response.json())
        raise Exception(f"Error in API request: {response.status_code}")

    results = response.json().get("items", [])

    def get_page_content(url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            words = text.split()
            content = ""
            for word in words:
                if len(content) + len(word) + 1 > max_chars:
                    break
                content += " " + word
            return content.strip()
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return ""

    enriched_results = []
    for item in results:
        body = get_page_content(item["link"])
        enriched_results.append(
            {"title": item["title"], "link": item["link"], "snippet": item["snippet"], "body": body}
        )
        time.sleep(1)  # Be respectful to the servers

    return enriched_results

def arxiv_search(query: str, max_results: int = 2) -> list:  # type: ignore[type-arg]
    """
    Search Arxiv for papers and return the results including abstracts.
    """
    import arxiv

    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)

    results = []
    for paper in client.results(search):
        results.append(
            {
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "published": paper.published.strftime("%Y-%m-%d"),
                "abstract": paper.summary,
                "pdf_url": paper.pdf_url,
            }
        )

    # # Write results to a file
    # with open('arxiv_search_results.json', 'w') as f:
    #     json.dump(results, f, indent=2)

    return results

async def main():
    
    google_search_tool = FunctionTool(
        google_search, description="Search Google for information, returns results with a snippet and body content"
    )
    arxiv_search_tool = FunctionTool(
        arxiv_search, description="Search Arxiv for papers related to a given topic, including abstracts"
    )

    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    google_search_agent = AssistantAgent(
        name="Google_Search_Agent",
        tools=[google_search_tool],
        model_client=model_client,
        description="An agent that can search Google for information, returns results with a snippet and body content",
        system_message="You are a helpful AI assistant. Solve tasks using your tools.",
    )

    arxiv_search_agent = AssistantAgent(
        name="Arxiv_Search_Agent",
        tools=[arxiv_search_tool],
        model_client=model_client,
        description="An agent that can search Arxiv for papers related to a given topic, including abstracts",
        system_message="You are a helpful AI assistant. Solve tasks using your tools. Specifically, you can take into consideration the user's request and craft a search query that is most likely to return relevant academi papers.",
    )


    report_agent = AssistantAgent(
        name="Report_Agent",
        model_client=model_client,
        description="Generate a report based on a given topic",
        system_message="You are a helpful assistant. Your task is to synthesize data extracted into a high quality literature review including CORRECT references. You MUST write a final report that is formatted as a literature review with CORRECT references.  Your response should end with the word 'TERMINATE'",
    )

    termination = TextMentionTermination("TERMINATE")
    team = RoundRobinGroupChat(
        participants=[google_search_agent, arxiv_search_agent, report_agent], termination_condition=termination
    )

    await Console(
        team.run_stream(
            task="Write a literature review on no code tools for building multi agent ai systems",
        )
    )

    await model_client.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())