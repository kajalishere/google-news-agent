#!/usr/bin/env python3
"""
Google News Agent - Fetch and display latest news
Built for Antigravity agent framework
Kaggle 5-Day AI Agents Course
"""

import urllib
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import webbrowser
from typing import List, Dict
from datetime import datetime
from urllib.parse import quote

class GoogleNewsAgent:
    """
    Agent to fetch and display Google News headlines
    Features: news categories, search, browser integration
    Zero external dependencies - uses only built-in Python modules
    """
    
    def __init__(self):
        """Initialize the agent with categories and configuration"""
        self.base_url = "https://news.google.com/rss"
        self.categories = {
            "top": "?hl=en-US&gl=US&ceid=US:en",
            "technology": "?topic=TECHNOLOGY&hl=en-US&gl=US&ceid=US:en",
            "business": "?topic=BUSINESS&hl=en-US&gl=US&ceid=US:en",
            "science": "?topic=SCIENCE&hl=en-US&gl=US&ceid=US:en",
            "health": "?topic=HEALTH&hl=en-US&gl=US&ceid=US:en",
            "sports": "?topic=SPORTS&hl=en-US&gl=US&ceid=US:en",
        }
        self.articles = []
        self.current_category = "top"
    
    def print_header(self):
        """Print welcome banner and instructions"""
        print("\n" + "="*70)
        print("🗞️  GOOGLE NEWS AGENT - Powered by Antigravity")
        print("="*70)
        print("\n📖 HOW TO USE:")
        print("  [1-N]      Open article by number")
        print("  [c]        Show available categories")
        print("  [s]        Search for news")
        print("  [r]        Reload current category")
        print("  [q]        Quit")
        print("\n" + "="*70 + "\n")
    
    def parse_feed(self, url: str) -> List[Dict]:
        """
        Parse RSS feed from Google News
        Extracts: title, link, published date, source
        
        Args:
            url: Full RSS feed URL
            
        Returns:
            List of dictionaries with article data
        """
        try:
            # Fetch the RSS feed with user-agent header
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            print(f"📡 Fetching news from: {self.current_category}...")
            
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()
            
            # Parse XML feed
            root = ET.fromstring(xml_data)
            
            articles = []
            # Get top 20 articles from feed
            for item in root.findall('.//item')[:20]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                pub_date_elem = item.find('pubDate')
                
                if title_elem is not None and link_elem is not None:
                    articles.append({
                        'title': title_elem.text or 'Untitled',
                        'link': link_elem.text or '',
                        'published': pub_date_elem.text if pub_date_elem is not None else 'Recently',
                        'source': self.extract_source(title_elem.text or '')
                    })
            
            print(f"✅ Found {len(articles)} articles\n")
            return articles
            
        except urllib.error.URLError as e:
            print(f"❌ Network error: {e}\n")
            return []
        except ET.ParseError as e:
            print(f"❌ Parse error: {e}\n")
            return []
        except Exception as e:
            print(f"❌ Error: {e}\n")
            return []
    
    def extract_source(self, title: str) -> str:
        """
        Extract news source from article title
        Google News format: "Title - Source"
        
        Args:
            title: Full article title
            
        Returns:
            News source name
        """
        if " - " in title:
            parts = title.split(" - ")
            return parts[-1]
        return "Google News"
    
    def display_articles(self, articles: List[Dict]):
        """
        Display articles in formatted numbered list
        
        Args:
            articles: List of article dictionaries
        """
        self.articles = articles
        
        if not articles:
            print("❌ No articles found. Try a different search or category.\n")
            return
        
        print(f"\n📰 ARTICLES ({len(articles)} found):\n")
        print("-" * 80)
        
        for idx, article in enumerate(articles, 1):
            # Truncate title to fit display
            title = article['title']
            if len(title) > 70:
                title = title[:67] + "..."
            
            source = article['source']
            if len(source) > 25:
                source = source[:22] + "..."
            
            print(f"\n{idx:2d}. {title}")
            print(f"    📍 Source: {source}")
        
        print("\n" + "-" * 80 + "\n")
    
    def show_categories(self):
        """Display available news categories"""
        print("\n📂 AVAILABLE CATEGORIES:\n")
        categories_list = [
            ("top", "Top Headlines"),
            ("technology", "Technology News"),
            ("business", "Business News"),
            ("science", "Science News"),
            ("health", "Health News"),
            ("sports", "Sports News"),
        ]
        
        for cat_key, cat_name in categories_list:
            marker = "✓" if cat_key == self.current_category else " "
            print(f"  [{marker}] {cat_key:12} - {cat_name}")
        
        print()
    
    def fetch_category(self, category: str):
        """
        Fetch news from specific category
        
        Args:
            category: Category key (top, technology, business, etc.)
        """

        # Make case-insensitive and extract just the key part
        category = category.strip().lower()
    
        # Extract first word if user enters "top headlines" instead of "top"
        category = category.split()[0]
    
        if category not in self.categories:
            print(f"❌ Unknown category: '{category}'")
            self.show_categories()
            return
    
        self.current_category = category
        url = self.base_url + self.categories[category]
        articles = self.parse_feed(url)
        self.display_articles(articles)

    
    def search_news(self, query: str):
        """
        Search news for specific query
        
        Args:
            query: Search terms
        """
        if not query.strip():
            print("❌ Please enter a search query.\n")
            return

        # URL encode the query to handle spaces and special characters
        encoded_query = quote(query)
        
        # Google News search URL
        search_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        articles = self.parse_feed(search_url)
        
        if articles:
            print(f"🔍 Search results for: '{query}'\n")
        
        self.display_articles(articles)
    
    def open_article(self, number: int):
        """
        Open article in default web browser
        
        Args:
            number: Article number (1-based)
        """
        if not self.articles:
            print("❌ No articles loaded. Load a category or search first.\n")
            return
        
        if 1 <= number <= len(self.articles):
            article = self.articles[number - 1]
            link = article['link']
            title = article['title'][:50]
            
            print(f"\n🌐 Opening article: {title}...")
            try:
                webbrowser.open(link)
                print("✅ Opened in default browser\n")
            except Exception as e:
                print(f"⚠️  Could not open browser: {e}")
                print(f"📎 Copy this link: {link}\n")
        else:
            print(f"❌ Invalid article number. Please enter 1-{len(self.articles)}\n")
    
    def print_help(self):
        """Display help information"""
        print("\n" + "="*70)
        print("ℹ️  HELP & COMMANDS")
        print("="*70)
        print("\n[1-N]  - Open article number (e.g., '1' opens first article)")
        print("[c]    - Show categories and switch categories")
        print("[s]    - Search news by keyword")
        print("[r]    - Reload/refresh current category")
        print("[h]    - Show this help")
        print("[q]    - Quit the agent")
        print("\n" + "="*70 + "\n")
    
    def run(self):
        """
        Main agent loop - interactive command handling
        Loads top headlines on startup
        """
        self.print_header()
        
        # Load top headlines on startup
        print("Loading top headlines...\n")
        self.fetch_category("top")
        
        # Interactive command loop
        while True:
            try:
                user_input = input("📌 Enter command: ").strip().lower()
                
                # Quit
                if user_input == 'q':
                    print("\n👋 Thank you for using Google News Agent. Goodbye!\n")
                    break
                
                # Show categories
                elif user_input == 'c':
                    self.show_categories()
                    category = input("Enter category name: ").strip().lower()
                    if category:
                        self.fetch_category(category)
                
                # Search
                elif user_input == 's':
                    query = input("Enter search query: ").strip()
                    if query:
                        self.search_news(query)
                    else:
                        print("❌ Empty search query.\n")
                
                # Reload
                elif user_input == 'r':
                    print(f"\nReloading {self.current_category} category...\n")
                    self.fetch_category(self.current_category)
                
                # Help
                elif user_input == 'h':
                    self.print_help()
                
                # Open article by number
                elif user_input.isdigit():
                    self.open_article(int(user_input))
                
                else:
                    print("❌ Unknown command. Type 'h' for help.\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 Agent interrupted. Goodbye!\n")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")


def main():
    """Entry point for the application"""
    agent = GoogleNewsAgent()
    agent.run()


if __name__ == "__main__":
    main()