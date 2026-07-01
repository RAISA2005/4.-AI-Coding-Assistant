"""
🤖 AI LIBRARY ASSISTANT - FINAL VERSION
Combines Hugging Face AI with real-time web scraping
"""

import streamlit as st
import os
import requests
import random
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from transformers import pipeline

# Load environment
load_dotenv()
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "AI Library Assistant"

# Page configuration
st.set_page_config(
    page_title="AI Library Assistant",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'user_info' not in st.session_state:
    st.session_state.user_info = {'age': 25, 'student': False, 'saved': False}
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'selected_book' not in st.session_state:
    st.session_state.selected_book = None
if 'ai_summary' not in st.session_state:
    st.session_state.ai_summary = ""

# Get Hugging Face token
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN or HF_TOKEN == "your_token_here":
    st.error("❌ HF_TOKEN not found in .env file!")
    st.info("Create a .env file with: HF_TOKEN=your_huggingface_token")
    st.stop()

# Load AI model
@st.cache_resource
def load_ai_model():
    try:
        return pipeline(
            "text-generation",
            model="distilgpt2",
            token=HF_TOKEN,
            max_length=200
        )
    except:
        return None

ai_model = load_ai_model()

# --------------------------------------------------
# WEB SCRAPING FUNCTIONS
# --------------------------------------------------

def scrape_books_from_web(query):
    """Scrape book data from multiple sources"""
    books = []
    
    # Try Open Library
    try:
        url = f"https://openlibrary.org/search.json?q={query.replace(' ', '+')}&limit=8"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for doc in data.get("docs", [])[:6]:
                title = doc.get("title", "")
                authors = doc.get("author_name", [])
                
                if title and len(title) > 2:
                    author = authors[0] if authors else "Unknown Author"
                    
                    # Get book details
                    book_key = doc.get("key", "")
                    description = get_book_description(book_key)
                    
                    # Get price
                    price = estimate_book_price(title)
                    
                    books.append({
                        'title': title,
                        'author': author,
                        'description': description[:250] + "..." if len(description) > 250 else description,
                        'price': price,
                        'year': doc.get("first_publish_year", "Unknown"),
                        'subjects': doc.get("subject", [])[:3],
                        'source': 'Open Library'
                    })
    except:
        pass
    
    return books

def get_book_description(book_key):
    """Get book description from Open Library"""
    try:
        if book_key:
            url = f"https://openlibrary.org{book_key}.json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                desc = data.get("description", {})
                
                if isinstance(desc, dict):
                    return desc.get("value", "No description available")
                elif isinstance(desc, str):
                    return desc
    except:
        pass
    return "No description available"

def estimate_book_price(title):
    """Estimate book price with student discount"""
    title_lower = title.lower()
    
    # Base price based on book type
    if any(word in title_lower for word in ['textbook', 'handbook', 'manual', 'guide']):
        base = random.uniform(25.99, 79.99)
    elif any(word in title_lower for word in ['novel', 'fiction', 'story']):
        base = random.uniform(8.99, 16.99)
    elif any(word in title_lower for word in ['biography', 'history', 'science']):
        base = random.uniform(12.99, 24.99)
    else:
        base = random.uniform(9.99, 29.99)
    
    # Apply student discount
    if st.session_state.user_info.get('student'):
        base *= 0.75  # 25% student discount
    
    return round(base, 2)

def get_student_recommendations(age):
    """Get book recommendations for students"""
    recommendations = []
    
    # Different recommendations based on age
    if age < 18:  # High school
        recommendations = [
            {"title": "SAT Prep Guide", "reason": "Essential for college admissions"},
            {"title": "To Kill a Mockingbird", "reason": "High school literature classic"},
            {"title": "High School Biology", "reason": "Comprehensive textbook"}
        ]
    else:  # College/University
        recommendations = [
            {"title": "Introduction to Algorithms", "reason": "Standard CS textbook"},
            {"title": "Calculus Textbook", "reason": "Essential math resource"},
            {"title": "Academic Writing Guide", "reason": "Improve research papers"}
        ]
    
    return recommendations

def get_related_suggestions(book_title):
    """Get related book suggestions"""
    # Simple keyword-based suggestions
    title_lower = book_title.lower()
    
    if any(word in title_lower for word in ['python', 'programming', 'code']):
        return [
            "Clean Code by Robert Martin",
            "The Pragmatic Programmer",
            "Python Crash Course"
        ]
    elif any(word in title_lower for word in ['fiction', 'novel', 'story']):
        return [
            "The Great Gatsby",
            "To Kill a Mockingbird", 
            "1984 by George Orwell"
        ]
    elif any(word in title_lower for word in ['science', 'physics', 'biology']):
        return [
            "A Brief History of Time",
            "The Selfish Gene",
            "Cosmos by Carl Sagan"
        ]
    else:
        return [
            "Popular Fiction Books",
            "Non-Fiction Bestsellers",
            "Self-Help Classics"
        ]

# --------------------------------------------------
# AI FUNCTIONS
# --------------------------------------------------

def generate_ai_summary(book_title, book_author):
    """Generate AI summary using Hugging Face"""
    if not ai_model:
        return "AI model not available"
    
    try:
        prompt = f"Write a brief summary of the book '{book_title}' by {book_author}:"
        response = ai_model(prompt, max_length=150, num_return_sequences=1)
        summary = response[0]['generated_text'].replace(prompt, "").strip()
        return summary[:200] + "..." if len(summary) > 200 else summary
    except:
        return "Could not generate AI summary"

def get_ai_suggestions(book_title, is_student):
    """Get AI-powered suggestions"""
    if not ai_model:
        return get_related_suggestions(book_title)
    
    try:
        context = "similar books"
        if is_student:
            context = "similar books suitable for students"
        
        prompt = f"Recommend 3 {context} to '{book_title}':"
        response = ai_model(prompt, max_length=100, num_return_sequences=1)
        suggestions = response[0]['generated_text'].replace(prompt, "").strip()
        
        # Parse into list
        lines = [line.strip() for line in suggestions.split('\n') if line.strip()]
        return lines[:3] if lines else get_related_suggestions(book_title)
    except:
        return get_related_suggestions(book_title)

# --------------------------------------------------
# MAIN APPLICATION
# --------------------------------------------------

def main():
    # App Header
    st.title("🤖 AI Library Assistant")
    st.markdown("### Find, Discover & Explore Books")
    st.markdown("---")
    
    # Main layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # User Profile
        st.subheader("👤 Your Profile")
        
        age = st.number_input(
            "Your Age",
            min_value=5,
            max_value=100,
            value=st.session_state.user_info['age']
        )
        
        student = st.radio(
            "Are you a student?",
            ["No", "Yes"],
            index=1 if st.session_state.user_info['student'] else 0
        )
        
        if st.button("💾 Save Profile", type="primary", use_container_width=True):
            st.session_state.user_info = {
                'age': age,
                'student': student == "Yes",
                'saved': True
            }
            st.success("Profile saved!")
            st.rerun()
        
        # Display profile
        st.divider()
        if st.session_state.user_info['saved']:
            st.write("**Current Profile:**")
            st.write(f"• Age: {st.session_state.user_info['age']}")
            st.write(f"• Student: {'🎓 Yes' if st.session_state.user_info['student'] else '❌ No'}")
        
        # Student recommendations
        if st.session_state.user_info.get('student'):
            st.divider()
            st.subheader("🎓 Student Picks")
            
            recommendations = get_student_recommendations(st.session_state.user_info['age'])
            for rec in recommendations:
                st.write(f"• {rec['title']}")
                st.caption(f"  {rec['reason']}")
    
    with col2:
        # Main Search Area
        st.subheader("🔍 Search Any Book")
        
        # Search input
        search_query = st.text_input(
            "Enter book title, author, or topic:",
            placeholder="e.g., 'Harry Potter', 'science books', 'Stephen King'",
            key="search_input"
        )
        
        # Search button
        col_search, col_clear = st.columns([3, 1])
        with col_search:
            if st.button("🚀 Search Web", type="primary", use_container_width=True) and search_query:
                with st.spinner("Searching across book databases..."):
                    results = scrape_books_from_web(search_query)
                    st.session_state.search_results = results
                    st.session_state.selected_book = None
                    st.rerun()
        
        with col_clear:
            if st.button("🗑️ Clear", type="secondary", use_container_width=True):
                st.session_state.search_results = []
                st.session_state.selected_book = None
                st.rerun()
        
        # Display Search Results
        if st.session_state.search_results:
            st.divider()
            st.subheader(f"📚 Found {len(st.session_state.search_results)} Books")
            
            # Show all books
            for i, book in enumerate(st.session_state.search_results):
                with st.expander(f"{i+1}. {book['title'][:50]}..."):
                    st.write(f"**Author:** {book['author']}")
                    st.write(f"**Year:** {book.get('year', 'Unknown')}")
                    st.write(f"**Description:** {book['description']}")
                    
                    # Price
                    price_text = f"**Price:** ${book['price']}"
                    if st.session_state.user_info.get('student'):
                        price_text += " 🎓 (25% student discount applied)"
                    st.write(price_text)
                    
                    # Select button
                    if st.button("Select This Book", key=f"select_{i}"):
                        st.session_state.selected_book = book
                        st.rerun()
            
            # Show Selected Book Details
            if st.session_state.selected_book:
                st.divider()
                st.subheader("📖 Selected Book Details")
                
                book = st.session_state.selected_book
                
                # Book info
                st.write(f"### {book['title']}")
                st.write(f"**Author:** {book['author']}")
                st.write(f"**Source:** {book['source']}")
                
                # Description
                st.write("**Description:**")
                st.info(book['description'])
                
                # Price section
                col_price, col_discount = st.columns(2)
                with col_price:
                    st.metric("Price", f"${book['price']}")
                
                with col_discount:
                    if st.session_state.user_info.get('student'):
                        student_price = book['price'] * 0.75
                        st.metric("Student Price", f"${student_price:.2f}")
                
                # AI Summary
                if st.button("🤖 Generate AI Summary"):
                    with st.spinner("AI is writing summary..."):
                        summary = generate_ai_summary(book['title'], book['author'])
                        st.session_state.ai_summary = summary
                        st.rerun()
                
                if st.session_state.ai_summary:
                    st.success("**AI Summary:**")
                    st.write(st.session_state.ai_summary)
                
                # Related Suggestions
                st.subheader("💡 You Might Also Like:")
                
                suggestions = get_ai_suggestions(
                    book['title'],
                    st.session_state.user_info.get('student', False)
                )
                
                for j, suggestion in enumerate(suggestions, 1):
                    st.write(f"{j}. {suggestion}")
                    
                    # Search for this suggestion
                    if st.button(f"Search '{suggestion[:20]}...'", key=f"sug_{j}"):
                        st.session_state.search_results = scrape_books_from_web(suggestion)
                        st.session_state.selected_book = None
                        st.rerun()
                
                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔍 Search New Book"):
                        st.session_state.selected_book = None
                        st.session_state.ai_summary = ""
                        st.rerun()
                
                with col2:
                    if st.button("📋 View All Results"):
                        st.session_state.selected_book = None
                        st.rerun()
        
        # Initial state - no search yet
        elif not search_query:
            st.divider()
            st.info("💡 **How to use:**")
            st.write("1. Enter your age and student status")
            st.write("2. Click 'Save Profile'")
            st.write("3. Search for any book in the box above")
            st.write("4. Select a book to see details and suggestions")
            
            # Example searches
            st.write("\n**Try searching for:**")
            examples = ["Python", "Science fiction", "History", "Biography"]
            cols = st.columns(2)
            for i, example in enumerate(examples):
                with cols[i % 2]:
                    if st.button(f"🔍 {example}", key=f"ex_{i}"):
                        st.session_state.search_results = scrape_books_from_web(example)
                        st.rerun()
    
    # Footer
    st.markdown("---")
    if ai_model:
        st.caption("🤖 AI Enabled | 📚 Real-time Search | 🎓 Student Features")
    else:
        st.caption("📚 Basic Search | 🎓 Student Features | ⚠️ AI Not Available")

# --------------------------------------------------
# RUN APP
# --------------------------------------------------

if __name__ == "__main__":
    main()