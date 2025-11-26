import random
import datetime

SOURCES = ["CNN", "BBC", "Fox News", "EuroNews", "Al Jazeera", "CCTV"]
TOPICS = ["Politics", "Economy", "Technology", "Health", "Environment", "Military"]
KEYWORDS = ["Cybersecurity", "AI Regulation", "Global Warming", "Trade War", "Election", "Pandemic"]

NEWS_TEMPLATES = [
    "Breaking news: {topic} update from {source}.",
    "Live report: Major development in {topic} sector.",
    "Exclusive: Inside the {topic} crisis.",
    "Global impact of recent {topic} decisions.",
    "Expert analysis on the future of {topic}.",
]

SUBTITLES = [
    "The situation is developing rapidly.",
    "We are receiving reports from the ground.",
    "Officials have declined to comment.",
    "This is a significant turning point.",
    "Experts warn of potential consequences.",
    "Stay tuned for more updates.",
    "Live coverage continues...",
    "We will bring you the latest as it happens.",
]

def generate_news():
    source = random.choice(SOURCES)
    topic = random.choice(TOPICS)
    title = random.choice(NEWS_TEMPLATES).format(topic=topic, source=source)
    return {
        "id": str(random.randint(1000, 9999)),
        "source": source,
        "title": title,
        "summary": f"Detailed report about {topic} from {source}. Key stakeholders are involved...",
        "timestamp": datetime.datetime.now().isoformat(),
        "sentiment": random.choice(["Positive", "Negative", "Neutral"]),
    }

def generate_analytics():
    return {
        "sentiment_score": round(random.uniform(-1, 1), 2),
        "trending_keywords": random.sample(KEYWORDS, 3),
        "active_sources": random.randint(3, 6),
        "total_mentions": random.randint(100, 5000),
    }

def generate_subtitle():
    return {
        "text": random.choice(SUBTITLES),
        "lang": "vi", # Simulated translation
        "timestamp": datetime.datetime.now().isoformat(),
    }
