
#pip install langchain-google-genai google-generativeai langchain-community langchain-core python-dotenv langgraph --quiet
#pip install -qU "langchain-community>=0.2.11" tavily-python --quiet

# Imports required libraries
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
import streamlit as st

from dotenv import load_dotenv
load_dotenv()

# Get the keys from environment
gemini_ai_key = os.getenv("GOOGLE_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

os.environ["GOOGLE_API_KEY"]=gemini_ai_key
os.environ["TAVILY_API_KEY"]=tavily_key

# Initialize the tool
tool = TavilySearchResults(
    max_results=100,
    search_depth='advanced',
    include_answer=True,
    include_raw_content=True,
    include_images=True,
)

# Initialize Gemini Pro model
model = ChatGoogleGenerativeAI(model="gemini-pro")

# Create a LangGraph agent
agent=create_react_agent(model=model, tools=[tool])

# Create system-level guidance (sets context for the tool)
system_msg = SystemMessage(
    content="You are a research assistant specializing in climate and insurance data. "
            "Always include the source and publication date if available."
)

# Create a human-level prompt (what the user is actually asking)
human_msg = HumanMessage(
    content="Search for current trends in Climate Risk Insurance for 2025, and include source and publish date in the result."
)

# Combine messages into a single search query
combined_query = f"{system_msg.content}\n{human_msg.content}"

# Invoke the search tool
response = tool.invoke({"query": combined_query})

# Extract and structure the response
structured_results = []
for result in response:
    structured_results.append({
        "title": result.get("title"),
        "url": result.get("url"),
        "content": result.get("content"),

    })

    
# Define your keywords
keywords = ['climate risk','parametric insurance', 'climate change', 'Catastrophic weather','flood insurance','climate resilience']

# Create a list to store filtered results
filtered_results = []

# Loop through structured results and filter based on keywords in title
for item in structured_results:
    content = item.get('content', '').lower()

    # Find matching tags
    tags = [kw for kw in keywords if kw.lower() in content]

    # If any tags match, store the item with tags
    if tags:
      filtered_results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "date": item.get("date"),
            "content": item.get("content", ""),
            "tags": tags
        })






# Streamlit UI
st.title("Climate Risk Insurance Dashboard")

# Sidebar for Tag Selection
st.sidebar.header("Filter by Tag")

#selected_tag = st.sidebar.selectbox("Select a tag", all_tags)
selected_tag = st.sidebar.selectbox("Select a tag", keywords)

# Display Filtered News Articles
st.header(f"News Articles Tagged: {selected_tag}")
#selected_tag="climate risk"

def filter_by_tag(data, selected_tag):
  return [item for item in data if selected_tag in item['tags']]


filtered_news = filter_by_tag(filtered_results, selected_tag)
if filtered_news:
    for article in filtered_news:
        st.subheader(article["title"])
        st.caption(f"{article['url']} | {article['date']}")
        st.write(article["content"])
        st.markdown("---")
else:
    st.write("No news articles match this tag.")


st.sidebar.markdown("### About")
st.sidebar.info(
    "This dashboard integrates news and academic research on climate risk insurance. "
    "Select a tag to see related items from both news and research sources."
)
