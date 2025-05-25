import sys
from search import search_exa
import os
from dotenv import load_dotenv
import openai

HEALTH_KEYWORDS = [
    "cholesterol", "testosterone", "diet", "blood pressure", "diabetes", "nutrition",
    "heart", "cancer", "vitamin", "exercise", "obesity", "weight", "food", "fat",
    "protein", "carbohydrate", "disease", "health", "wellness", "fitness", "calorie",
    "sugar", "insulin", "metabolism", "immune", "allergy", "asthma", "arthritis",
    "depression", "anxiety", "mental health", "sleep", "hydration", "supplement"
]

class HealthQueryProcessor:
    def __init__(self):
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_final_summary(self, summaries):
        """Combine individual summaries and generate health recommendations."""
        combined = "\n\n".join([f"{title}: {summary}" for title, summary in summaries])
        prompt = (
            "Combine these summaries and provide dietary recommendations. "
            "Focus on health-related content only. Extract health context from the articles "
            "and suggest practical ways to address the issues mentioned.\n" + combined
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=350,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error during summarization: {str(e)}]"

    def is_health_related(self, query):
        """Check if query contains health-related keywords."""
        query_lower = query.lower()
        query_words = query_lower.split()
        return any(keyword in query_words or keyword in query_lower for keyword in HEALTH_KEYWORDS)

    def is_safe_query(self, query):
        """Validate query is safe and health-related using AI."""
        prompt = (
            "Classify if this query is strictly about health/wellness and safe. "
            "Answer only 'yes' or 'no'.\n"
            f"Query: {query}"
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1,
                temperature=0,
            )
            return response.choices[0].message.content.strip().lower() == "yes"
        except Exception as e:
            print(f"[Validation error: {str(e)}]")
            return False

    def process_query(self, query):
        """Main processing pipeline for health queries."""
        if not self.is_health_related(query):
            print("Running AI validation...")
            if not self.is_safe_query(query):
                raise ValueError("Only safe, health-related queries are supported")

        print(f"Searching for: {query}\n")
        search_results = search_exa(
            query,
            num_results=5,
            category="research paper",
            type="keyword",
            exclude_text=["pdf"],
            summary=True
        )

        summaries = [(title, summary) for url, title, summary in search_results]
        
        print("\n=== Search Results ===")
        for title, summary in summaries:
            print(f"\n- {title}\n  Summary: {summary[:150]}...")

        print("\n=== Final Recommendations ===")
        print(self.generate_final_summary(summaries))

def main():
    if len(sys.argv) < 2:
        print("Usage: python mcp_agent.py <health-related query>")
        sys.exit(1)

    processor = HealthQueryProcessor()
    
    try:
        query = " ".join(sys.argv[1:])
        processor.process_query(query)
    except ValueError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()