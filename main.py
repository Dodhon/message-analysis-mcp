#!/usr/bin/env python3

from message_analyzer import MessageAnalyzer
import json
import sys

def print_stats(stats):
    """Pretty print statistics"""
    print("\n" + "="*50)
    print("📱 iMessage Analysis Results")
    print("="*50)
    
    basic = stats.get('basic_stats', {})
    print(f"Total Messages: {basic.get('total_messages', 0)}")
    print(f"Unique Senders: {basic.get('unique_senders', 0)}")
    print(f"Avg Message Length: {basic.get('avg_message_length', 0):.1f} characters")
    print(f"Longest Message: {basic.get('longest_message', 0)} characters")
    
    print("\n🏆 Top Senders:")
    top_senders = basic.get('top_senders', {})
    for sender, count in top_senders.items():
        print(f"  • {sender}: {count} messages")
    
    print("\n🔤 Most Common Words:")
    word_freq = stats.get('word_frequency', {})
    for word, count in word_freq.items():
        print(f"  • {word}: {count} times")
    
    #  conversation analysis
    conv_stats = stats.get('conversation_stats', {})
    if conv_stats and 'top_conversations' in conv_stats:
        print("\n" + "="*50)
        print("Conversation Analysis")
        print("="*50)
        print(f"Total Conversations: {conv_stats.get('total_conversations', 0)}")
        
        print("\nTop Conversations (Who talks more?):")
        for conv in conv_stats['top_conversations']:
            contact = conv['contact']
            total = conv['total_messages']
            my_pct = conv['my_percentage']
            their_pct = conv['their_percentage']
            who_talks = conv['who_talks_more']
            avg_len = conv['avg_message_length']
            
            print(f"\n  {contact}")
            print(f"     Total: {total} messages")
            print(f"     Me: {my_pct}% ({conv['my_messages']} msgs) | Them: {their_pct}% ({conv['their_messages']} msgs)")
            print(f"     Who talks more: {who_talks} | Avg length: {avg_len:.1f} chars")

def main():
    """Main function to run iMessage analysis"""
    print("Starting iMessage Analysis...")
    
    # Initialize analyzer and fetch messages
    analyzer = MessageAnalyzer()
    if not analyzer.fetch_messages():
        print("Failed to fetch messages. Make sure you have proper permissions.")
        print("   Go to: System Settings → Privacy & Security → Full Disk Access")
        print("   Add Terminal (or Python) to the allowed applications.")
        sys.exit(1)
    
    # Generate and display stats
    stats = {
        'basic_stats': analyzer.basic_stats(),
        'word_frequency': analyzer.word_frequency(),
        'conversation_stats': analyzer.conversation_stats(top_n=5)
    }
    
    print_stats(stats)
    
    # Export results
    analyzer.export_stats()
    
    print("\nAnalysis complete!")
    print("Results have been exported to message_stats.json")

if __name__ == "__main__":
    main() 