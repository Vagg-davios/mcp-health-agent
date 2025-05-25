import sys
from search import search_exa
import os
from dotenv import load_dotenv
import openai

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def final_summary(summaries):
    combined = "\n\n".join([f"{title}: {summary}" for title, summary in summaries])
    prompt = (
        "Combine the summaries given to you. Provide recommendations for a diet based on those. "
        "Meaning that usually the original query will be for 'high cholesterol' for example. If the summaries are unrelated to health, don't both summarizing them."
        "Read the summaries and recommend ways to combat this. Regarding the context of the health issue, "
        "you will be able to extract that from the article.\n" + combined
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=350,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error during final summarization: {e}]"

def is_health_related(query):
    health_keywords = [
        "cholesterol", "testosterone", "diet", "blood pressure", "diabetes", "nutrition",
        "heart", "cancer", "vitamin", "exercise", "obesity", "weight", "food", "fat",
        "protein", "carbohydrate", "disease", "health", "wellness", "fitness", "calorie",
        "sugar", "insulin", "metabolism", "immune", "allergy", "asthma", "arthritis",
        "depression", "anxiety", "mental health", "sleep", "hydration", "supplement"
    ]
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in health_keywords)

def is_safe_and_health_query(query):
    prompt = (
        "You are an expert classifier. "
        "Is the following query strictly about health, wellness, nutrition, disease, or medical advice, "
        "and NOT about illegal, dangerous, or harmful activities (such as weapons, explosives, hacking, or crime)? "
        "If the query is about illegal, dangerous, or non-health topics, answer 'no'. "
        "Answer only 'yes' or 'no'.\n"
        f"Query: {query}"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1,
            temperature=0,
        )
        answer = response.choices[0].message.content.strip().lower()
        return answer == "yes"
    except Exception as e:
        print(f"[Error during health/safety validation: {e}]")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python mcp_agent.py <your health-related query>")
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    if not is_health_related(query):
        print("Keyword check failed, running AI validation...")
        if not is_safe_and_health_query(query):
            print("Sorry, this tool only supports safe, health-related queries.")
            sys.exit(1)
    print(f"Searching for: {query}\n")
    search_results = search_exa(
        query,
        num_results=5,
        category="research paper",
        type="keyword",
        exclude_text=["pdf"],
        summary=True
    )
    summaries = []
    for url, title, summary in search_results:
        print(f"- {title}: {url}")
        summaries.append((title, summary))
    print("\n\n=== Individual Summaries ===\n")
    for title, summary in summaries:
        print(f"{title}\nSummary: {summary}\n")
    print("\n=== Final Summary & Tips ===\n")
    print(final_summary(summaries))

if __name__ == "__main__":
    main()