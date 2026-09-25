from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain
)


def get_message_text(content):
    """Convert LangChain message content into plain text."""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, dict):
                if "text" in item:
                    text_parts.append(item["text"])
            else:
                text_parts.append(str(item))

        return "\n".join(text_parts)

    return str(content)


def run_research_pipeline(topic: str) -> dict:

    state = {}

    # STEP 1: SEARCH AGENT

    print("\n" + "=" * 50)
    print("STEP 1 - Search Agent is working...")
    print("=" * 50)

    search_agent = build_search_agent()

    search_result = search_agent.invoke({
        "messages": [
            (
                "user",
                f"""Search for recent and reliable information about:

{topic}

IMPORTANT:
Use the web_search tool.
Return the search results including the exact URLs.
Do not remove or change the URLs."""
            )
        ]
    })

    state["search_results"] = get_message_text(
        search_result["messages"][-1].content
    )

    print("\nSEARCH RESULTS:\n")
    print(state["search_results"])

    # STEP 2: READER AGENT

    print("\n" + "=" * 50)
    print("STEP 2 - Reader Agent is scraping a source...")
    print("=" * 50)

    reader_agent = build_reader_agent()

    reader_result = reader_agent.invoke({
        "messages": [
            (
                "user",
                f"""You are given search results about:

{topic}

Search Results:
{state["search_results"]}

IMPORTANT:
1. Find one valid URL from the search results.
2. Use the scrape_url tool on that URL.
3. Return the useful information from that webpage.
4. Also mention which URL you scraped."""
            )
        ]
    })

    state["scraped_content"] = get_message_text(
        reader_result["messages"][-1].content
    )

    print("\nSCRAPED CONTENT:\n")
    print(state["scraped_content"])


    # STEP 3: WRITER

    print("\n" + "=" * 50)
    print("STEP 3 - Writer is drafting the report...")
    print("=" * 50)

    research_combined = f"""
SEARCH RESULTS:
{state["search_results"]}

DETAILED SCRAPED CONTENT:
{state["scraped_content"]}
"""

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\nFINAL REPORT:\n")
    print(state["report"])


    # STEP 4: CRITIC

    print("\n" + "=" * 50)
    print("STEP 4 - Critic is reviewing the report...")
    print("=" * 50)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("\nCRITIC FEEDBACK:\n")
    print(state["feedback"])

    return state


if __name__ == "__main__":

    topic = input("\nEnter a research topic: ")

    run_research_pipeline(topic)