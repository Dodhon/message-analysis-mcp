#!/usr/bin/env python3

"""
iMessage Analysis MCP Server
Provides tools for analyzing iMessage data on macOS
"""

from mcp.server.fastmcp import FastMCP
from message_analyzer import MessageAnalyzer

# Create the MCP server
mcp = FastMCP("iMessage Analysis Server")

# Global analyzer instance
analyzer = None

def get_analyzer():
    """Get or create the message analyzer instance"""
    global analyzer
    if analyzer is None:
        analyzer = MessageAnalyzer()
        success = analyzer.fetch_messages()
        if not success:
            # The fetch_messages method already includes fallback logic
            # If it still fails, check if we have any messages loaded
            if not analyzer.messages:
                raise Exception("Failed to fetch messages. Check Full Disk Access permissions.")
    return analyzer

@mcp.tool()
def get_basic_statistics() -> dict:
    """
    Get basic statistics about your iMessage conversations.
    
    Returns:
        Dictionary containing total messages, unique senders, average message length, etc.
    """
    try:
        analyzer = get_analyzer()
        return analyzer.basic_stats()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_word_frequency(top_n: int = 10) -> dict:
    """
    Get the most frequently used words in your messages.
    
    Args:
        top_n: Number of top words to return (default: 10)
    
    Returns:
        Dictionary of word frequencies
    """
    try:
        analyzer = get_analyzer()
        return dict(list(analyzer.word_frequency().items())[:top_n])
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_conversation_analysis(top_n: int = 5) -> dict:
    """
    Analyze conversation patterns and who talks more with each contact.
    
    Args:
        top_n: Number of top conversations to analyze (default: 5)
    
    Returns:
        Dictionary containing conversation statistics and patterns
    """
    try:
        analyzer = get_analyzer()
        return analyzer.conversation_stats(top_n=top_n)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def list_contacts(limit: int = 20) -> list:
    """
    List all your contacts with message counts.
    
    Args:
        limit: Maximum number of contacts to return (default: 20)
    
    Returns:
        List of contacts with their message counts
    """
    try:
        analyzer = get_analyzer()
        
        # Count messages by contact
        contact_counts = {}
        for msg in analyzer.messages:
            contact = analyzer._format_phone_number(msg.get('handle_id', 'Unknown'))
            contact_counts[contact] = contact_counts.get(contact, 0) + 1
        
        # Sort by message count
        sorted_contacts = sorted(contact_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"contact": contact, "message_count": count}
            for contact, count in sorted_contacts[:limit]
        ]
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def search_messages(query: str, limit: int = 10) -> list:
    """
    Search through your messages for specific content.
    
    Args:
        query: Text to search for in messages
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        List of matching messages with sender and content
    """
    try:
        analyzer = get_analyzer()
        
        results = []
        query_lower = query.lower()
        
        for msg in analyzer.messages:
            text = msg.get('text', '')
            if text and query_lower in text.lower():
                results.append({
                    'sender': analyzer._format_phone_number(msg.get('handle_id', 'Unknown')),
                    'text': text,
                    'date': msg.get('date', ''),
                    'is_from_me': msg.get('is_from_me', False)
                })
                
                if len(results) >= limit:
                    break
        
        return results
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_contact_statistics(contact: str) -> dict:
    """
    Get detailed statistics for a specific contact.
    
    Args:
        contact: Phone number or handle of the contact
    
    Returns:
        Dictionary with message count, average length, and conversation ratio
    """
    try:
        analyzer = get_analyzer()
        
        # Find messages for this contact
        contact_messages = [
            msg for msg in analyzer.messages
            if analyzer._format_phone_number(msg.get('handle_id', '')) == contact
        ]
        
        if not contact_messages:
            return {"error": f"No messages found for contact: {contact}"}
        
        # Calculate statistics
        total_messages = len(contact_messages)
        my_messages = sum(1 for msg in contact_messages if msg.get('is_from_me', False))
        their_messages = total_messages - my_messages
        
        avg_length = sum(len(msg.get('text', '')) for msg in contact_messages) / total_messages
        
        return {
            'contact': contact,
            'total_messages': total_messages,
            'my_messages': my_messages,
            'their_messages': their_messages,
            'my_percentage': round((my_messages / total_messages) * 100, 1),
            'their_percentage': round((their_messages / total_messages) * 100, 1),
            'average_message_length': round(avg_length, 1),
            'who_talks_more': 'Me' if my_messages > their_messages else 'Them' if their_messages > my_messages else 'Equal'
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_conversation(contact: str, limit: int = 100, days_back: int = None) -> dict:
    """
    Retrieve full conversation history with a specific contact.
    
    ⚠️ PRIVACY WARNING: This tool returns actual message content. 
    All data is processed locally and never sent over the network.
    
    Args:
        contact: Contact name, phone number, or email to get conversation with
        limit: Maximum number of messages to return (default: 100, max recommended: 500)
        days_back: Only include messages from last N days (optional)
    
    Returns:
        Dictionary containing conversation messages, metadata, and statistics
    """
    try:
        analyzer = get_analyzer()
        
        # Validate limit to prevent overwhelming output
        if limit > 1000:
            return {"error": "Limit too high. Maximum recommended: 1000 messages"}
        
        conversation = analyzer.get_conversation(contact, limit, days_back)
        
        # Add privacy notice to the response
        if 'messages' in conversation:
            conversation['privacy_notice'] = "This conversation data is processed locally and contains personal information."
            conversation['data_source'] = "Local iMessage database"
        
        return conversation
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run() 