import yfinance as yf
from datetime import datetime
import feedparser
import newspaper

def get_full_article_text(url: str, max_length: int = 1500):
    """
    Extract full article text from URL
    
    Args:
        url: Article URL
        max_length: Max characters to extract
        
    Returns:
        Full article text or None if failed
    """
    try:
        article = newspaper.article(url)
        article.download()
        article.parse()
        print(f"\n{article.summary}\n")
        
        # Get the full text
        text = article.text
        
        # Truncate if too long (to save API costs)
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
        
    except Exception as e:
        print(f"Error extracting article from {url}: {e}")
        return None

def get_stock_news_with_content(ticker: str, num_articles: int = 3):
    """
    Get news with FULL article content for better analysis
    
    Args:
        ticker: Stock symbol
        num_articles: Number of articles to fetch (default 3 for full content)
        
    Returns:
        List of articles with full content
    """
    try:
        # Get news headlines from Google News RSS
        rss_url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        
        articles = []
        for entry in feed.entries[:num_articles]:
            article_data = {
                'title': entry.get('title', 'N/A'),
                'publisher': entry.get('source', {}).get('title', 'Google News'),
                'link': entry.get('link', ''),
                'summary': entry.get('summary', 'No summary available'),
                'publish_time': entry.get('published', 'Recently')
            }
            
            # Fetch full article content
            print(f"Fetching full article: {article_data['title'][:50]}...")
            full_text = get_full_article_text(article_data['link'], max_length=1500)
            
            if full_text:
                article_data['full_content'] = full_text
            else:
                # Fallback to summary if full text extraction fails
                article_data['full_content'] = article_data['summary']
            
            articles.append(article_data)
        
        return articles
        
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []


def get_stock_summary_context(ticker: str):
    """
    Get comprehensive stock context for LLM analysis with FULL article content
    
    Args:
        ticker: Stock symbol
        
    Returns:
        Formatted string with stock data and full news articles for LLM
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="5d")
        
        if hist.empty:
            return None
        
        # Get basic stock info
        current_price = hist['Close'].iloc[-1]
        prev_close = info.get('previousClose', hist['Close'].iloc[-2])
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
        
        # Get recent performance
        week_ago = hist['Close'].iloc[0]
        week_change = ((current_price - week_ago) / week_ago) * 100
        
        # Get news with FULL CONTENT (only 3 articles to keep context manageable)
        print(f"Fetching news for {ticker}...")
        news_articles = get_stock_news_with_content(ticker, num_articles=3)
        
        # Format context for LLM
        context = f"""
                Stock Analysis Request for {ticker} - {info.get('longName', ticker)}
                Current Market Data:
                - Current Price: ${current_price:.2f}
                - Daily Change: ${change:+.2f} ({change_pct:+.2f}%)
                - 5-Day Performance: {week_change:+.2f}%
                - Market Cap: ${info.get('marketCap', 0):,}
                - P/E Ratio: {info.get('trailingPE', 'N/A')}
                - 52 Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}
                - 52 Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}
                Recent News Articles (Full Content):
                """
        
        if news_articles:
            for i, article in enumerate(news_articles, 1):
                context += f"\n\n--- Article {i} ---"
                context += f"\nTitle: {article['title']}"
                context += f"\nSource: {article['publisher']}"
                context += f"\nPublished: {article['publish_time']}"
                context += f"\n\nContent:\n{article['full_content']}\n"
                context += "-" * 80
        else:
            context += "\nNo recent news articles found."
        
        return context
        
    except Exception as e:
        print(f"Error creating summary context for {ticker}: {e}")
        return None


# Test
if __name__ == "__main__":
    print("Testing full article extraction for AAPL:")
    context = get_stock_news_with_content("AAPL", 1)
    import newspaper
    print(newspaper.__file__)
    if context:
        print(f"\nContext length: {len(context)} characters")
        #print("\nFirst 1000 chars of context:")
        print(context[0].keys())
        print(context[0]["full_content"])
        print("\n...")