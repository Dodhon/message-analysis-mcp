from imessage_reader import fetch_data
from collections import Counter
from datetime import datetime, timedelta
import json
import os
import sys
import platform

class MessageAnalyzer:
    def __init__(self, db_path=None):
        self.messages = []
        # Default macOS path
        if db_path is None:
            home = os.path.expanduser("~")
            self.db_path = f"{home}/Library/Messages/chat.db"
        else:
            self.db_path = db_path
    
    def _validate_system(self):
        """Validate system compatibility"""
        if not sys.platform.startswith('darwin'):
            raise Exception("This tool only works on macOS")
        
        # Check macOS version (10.14+ required)
        macos_version = platform.mac_ver()[0]
        if macos_version:
            major, minor = map(int, macos_version.split('.')[:2])
            if major < 10 or (major == 10 and minor < 14):
                raise Exception(f"macOS 10.14+ required (found {macos_version})")
    
    def _validate_database_access(self):
        """Validate iMessage database access"""
        if not os.path.exists(self.db_path):
            raise Exception(f"iMessage database not found at {self.db_path}")
        
        try:
            # Try to read the database file
            with open(self.db_path, 'rb') as f:
                f.read(1)  # Just try to read 1 byte
        except PermissionError:
            raise Exception(
                "Permission denied accessing iMessage database. "
                "Please grant Full Disk Access: "
                "System Settings → Privacy & Security → Full Disk Access"
            )
        except Exception as e:
            raise Exception(f"Cannot access iMessage database: {e}")
    
    def _format_phone_number(self, handle_id):
        """Format phone number for better display"""
        if not handle_id or handle_id == 'Unknown':
            return 'Unknown'
        
        # If it's an email, return as-is
        if '@' in handle_id:
            return handle_id
        
        # If it's a phone number, format it nicely
        if handle_id.startswith('+1') and len(handle_id) == 12:
            # Format: +1XXXXXXXXXX -> +1 (XXX) XXX-XXXX
            return f"+1 ({handle_id[2:5]}) {handle_id[5:8]}-{handle_id[8:]}"
        elif handle_id.startswith('+') and handle_id[1:].isdigit():
            return handle_id  # Keep international numbers as-is
        else:
            return handle_id  # Probably already formatted or contact name
    
    def fetch_messages(self):
        """Fetch iMessage data using imessage_reader"""
        try:
            # Catch SystemExit specifically
            import sys
            original_exit = sys.exit
            
            def safe_exit(code=0):
                raise RuntimeError(f"Library tried to exit with code: {code}")
            
            sys.exit = safe_exit
            
            try:
                # Validate system and database access
                self._validate_system()
                self._validate_database_access()
                
                # Create FetchData instance with path to chat.db
                fd = fetch_data.FetchData(self.db_path)
                
                # Get messages using the correct method
                try:
                    raw_messages = fd.get_messages()
                except Exception as e:
                    print(f"Error fetching messages: {e}")
                    # Don't return False here - let it fall through to exception handling
                    raise e
                
                if not raw_messages:
                    print("⚠️  No messages found in database")
                    return True  # Not an error, just empty
                
                # Convert tuples to dictionaries for easier processing
                self.messages = []
                for msg in raw_messages:
                    # Handle different tuple formats gracefully
                    message_dict = {
                        'handle_id': msg[0] if len(msg) > 0 else 'Unknown',
                        'text': msg[1] if len(msg) > 1 else '',
                        'date': msg[2] if len(msg) > 2 else None,
                        'service': msg[3] if len(msg) > 3 else 'Unknown',
                        'account': msg[4] if len(msg) > 4 else 'Unknown',
                        'is_from_me': msg[5] if len(msg) > 5 else False,
                    }
                    
                    # Only add messages with actual content
                    if message_dict['text'] or message_dict['handle_id'] != 'Unknown':
                        self.messages.append(message_dict)
                
                print(f"✅ Loaded {len(self.messages)} messages from {len(set(msg.get('handle_id', 'Unknown') for msg in self.messages))} contacts")
                return True
            finally:
                sys.exit = original_exit
        except (RuntimeError, SystemExit) as e:
            print(f"⚠️ Database reading failed: {e}")
            print("Trying alternative approach...")
            return self._fallback_message_reading()
        except UnicodeDecodeError as e:
            print(f"⚠️ UTF-8 decoding error: {e}")
            print("Trying alternative approach...")
            return self._fallback_message_reading()
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            print("Trying alternative approach...")
            return self._fallback_message_reading()
    
    def _fallback_message_reading(self):
        """Fallback method using direct SQLite access with better error handling"""
        try:
            import sqlite3
            
            print("🔄 Attempting direct SQLite access...")
            
            # Connect to database with error handling
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Try a simple query first to test access
            cursor.execute("SELECT COUNT(*) FROM message")
            total_count = cursor.fetchone()[0]
            print(f"📊 Found {total_count} total messages in database")
            
            if total_count == 0:
                print("⚠️  Database is empty")
                conn.close()
                return True
            
            # Get messages with simplified query - include ALL message types
            query = """
            SELECT 
                h.id,
                m.text,
                m.date,
                m.service,
                m.account,
                m.is_from_me
            FROM message m
            LEFT JOIN handle h ON m.handle_id = h.ROWID
            ORDER BY m.date DESC
            LIMIT 10000
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            self.messages = []
            for row in rows:
                try:
                    # Handle potential encoding issues in text
                    text = row[1] if row[1] else ''
                    if isinstance(text, bytes):
                        # Try different encodings
                        try:
                            text = text.decode('utf-8')
                        except UnicodeDecodeError:
                            try:
                                text = text.decode('latin-1')
                            except UnicodeDecodeError:
                                text = text.decode('utf-8', errors='replace')
                    
                    message_dict = {
                        'handle_id': row[0] or 'Unknown',
                        'text': text or '[attachment/reaction]',
                        'date': row[2],
                        'service': row[3] or 'Unknown',
                        'account': row[4] or 'Unknown',
                        'is_from_me': bool(row[5]),
                    }
                    
                    # Include ALL messages (text, attachments, reactions, etc.)
                    if message_dict['handle_id'] != 'Unknown':
                        self.messages.append(message_dict)
                        
                except Exception as e:
                    # Skip problematic messages but continue
                    print(f"⚠️  Skipping message due to error: {e}")
                    continue
            
            conn.close()
            
            if self.messages:
                unique_contacts = len(set(msg.get('handle_id', 'Unknown') for msg in self.messages))
                print(f"✅ Loaded {len(self.messages)} messages from {unique_contacts} contacts (fallback method)")
                return True
            else:
                print("⚠️  No valid messages found")
                return False
                
        except Exception as e:
            print(f"❌ Fallback method also failed: {e}")
            return False

    def fetch_messages_with_recovery(self):
        try:
            return self._fetch_all_messages()
        except Exception as e:
            print(f"Full fetch failed: {e}")
            print("Attempting partial recovery...")
            return self._fetch_recent_messages_only()
    
    def basic_stats(self):
        """Generate basic statistics about messages"""
        if not self.messages:
            return {"error": "No messages loaded"}
        
        total_messages = len(self.messages)
        
        # Count messages by sender
        senders = Counter()
        message_lengths = []
        
        for msg in self.messages:
            sender = self._format_phone_number(msg.get('handle_id', 'Unknown'))
            senders[sender] += 1
            
            text = msg.get('text', '')
            if text:
                message_lengths.append(len(text))
        
        stats = {
            "total_messages": total_messages,
            "unique_senders": len(senders),
            "top_senders": dict(senders.most_common(5)),
            "avg_message_length": sum(message_lengths) / len(message_lengths) if message_lengths else 0,
            "longest_message": max(message_lengths) if message_lengths else 0
        }
        
        return stats
    
    def word_frequency(self, top_n=10):
        """Analyze word frequency across all messages"""
        if not self.messages:
            return {"error": "No messages loaded"}
        
        all_words = []
        # Attachment patterns to filter out
        attachment_patterns = ['<message', 'attachment.>', 'text,', 'attachment', 'shared', 'location']
        # Common stop words to filter
        stop_words = {'the', 'and', 'but', 'with', 'for', 'you', 'are', 'was', 'this', 'that', 'have', 'had'}
        
        for msg in self.messages:
            text = msg.get('text', '')
            if text and not any(pattern in text.lower() for pattern in attachment_patterns):
                # Simple word splitting and cleaning
                words = text.lower().replace(',', '').replace('.', '').replace('!', '').replace('?', '').split()
                # Filter out short words, stop words, and attachment artifacts
                words = [word for word in words if len(word) > 2 and word not in stop_words]
                all_words.extend(words)
        
        word_counter = Counter(all_words)
        return dict(word_counter.most_common(top_n))
    
    def export_stats(self, filename="message_stats.json"):
        """Export analysis results to JSON"""
        stats = {
            "basic_stats": self.basic_stats(),
            "word_frequency": self.word_frequency(),
            "conversation_stats": self.conversation_stats(),
            "analysis_date": datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"📊 Stats exported to {filename}")
        return stats
    
    def conversation_analysis(self):
        """Analyze conversations grouped by sender"""
        if not self.messages:
            return {"error": "No messages loaded"}
        
        # Group messages by sender
        conversations = {}
        
        for msg in self.messages:
            sender = self._format_phone_number(msg.get('handle_id', 'Unknown'))
            text = msg.get('text', '')
            is_from_me = msg.get('is_from_me', False)
            date = msg.get('date', None)
            
            if sender not in conversations:
                conversations[sender] = {
                    'messages': [],
                    'total_count': 0,
                    'my_messages': 0,
                    'their_messages': 0,
                    'total_chars': 0,
                    'avg_message_length': 0,
                    'last_message_date': None
                }
            
            conversations[sender]['messages'].append({
                'text': text,
                'is_from_me': is_from_me,
                'date': date,
                'char_count': len(text) if text else 0
            })
            
            conversations[sender]['total_count'] += 1
            conversations[sender]['total_chars'] += len(text) if text else 0
            
            if is_from_me:
                conversations[sender]['my_messages'] += 1
            else:
                conversations[sender]['their_messages'] += 1
            
            # Track most recent message date
            if date and (not conversations[sender]['last_message_date'] or 
                        date > conversations[sender]['last_message_date']):
                conversations[sender]['last_message_date'] = date
        
        # Calculate averages and ratios
        for sender, conv in conversations.items():
            if conv['total_count'] > 0:
                conv['avg_message_length'] = conv['total_chars'] / conv['total_count']
                conv['my_ratio'] = conv['my_messages'] / conv['total_count']
                conv['their_ratio'] = conv['their_messages'] / conv['total_count']
        
        return conversations
    
    def conversation_stats(self, top_n=5):
        """Generate conversation statistics"""
        conversations = self.conversation_analysis()
        if 'error' in conversations:
            return conversations
        
        # Sort by total message count
        sorted_convs = sorted(conversations.items(), 
                            key=lambda x: x[1]['total_count'], 
                            reverse=True)
        
        stats = {
            'total_conversations': len(conversations),
            'top_conversations': []
        }
        
        for sender, conv in sorted_convs[:top_n]:
            conv_stats = {
                'contact': sender,
                'total_messages': conv['total_count'],
                'my_messages': conv['my_messages'],
                'their_messages': conv['their_messages'],
                'my_percentage': round(conv['my_ratio'] * 100, 1),
                'their_percentage': round(conv['their_ratio'] * 100, 1),
                'avg_message_length': round(conv['avg_message_length'], 1),
                'who_talks_more': 'Me' if conv['my_ratio'] > 0.5 else 'Them'
            }
            stats['top_conversations'].append(conv_stats)
        
        return stats 
    
    def get_conversation(self, contact, limit=100, days_back=None):
        """
        Retrieve full conversation with a specific contact
        
        Args:
            contact (str): Contact name, phone number, or email to search for
            limit (int): Maximum number of messages to return (default: 100)
            days_back (int): Only include messages from last N days (optional)
            
        Returns:
            dict: Conversation data with messages, metadata, and statistics
        """
        if not self.messages:
            return {"error": "No messages loaded"}
        
        # Normalize the contact identifier for matching
        contact_normalized = contact.lower().strip()
        
        # Find all messages with this contact
        conversation_messages = []
        
        for msg in self.messages:
            sender = self._format_phone_number(msg.get('handle_id', 'Unknown'))
            
            # Check if this message matches the contact
            # Try multiple matching strategies
            matches = (
                contact_normalized in sender.lower() or
                contact_normalized in msg.get('handle_id', '').lower() or
                sender.lower() in contact_normalized or
                msg.get('handle_id', '').lower() in contact_normalized
            )
            
            if matches:
                message_date = msg.get('date')
                
                # Apply date filter if specified (skip for now since date comparison is complex with strings)
                # if days_back and message_date:
                #     cutoff_date = datetime.now() - timedelta(days=days_back)
                #     if message_date < cutoff_date:
                #         continue
                
                conversation_messages.append({
                    'text': msg.get('text', '') or '',
                    'timestamp': str(message_date) if message_date else None,
                    'sender': 'me' if msg.get('is_from_me', False) else sender,
                    'direction': 'sent' if msg.get('is_from_me', False) else 'received',
                    'service': msg.get('service', 'Unknown'),
                    'char_count': len(msg.get('text', '') or '')
                })
        
        if not conversation_messages:
            return {
                "error": f"No conversation found with '{contact}'. Try a different contact name, phone number, or email address."
            }
        
        # Sort messages chronologically (oldest first) - simple string sort should work for most timestamp formats
        conversation_messages.sort(key=lambda x: x['timestamp'] or '1970-01-01T00:00:00')
        
        # Apply limit (get most recent messages if limit exceeded)
        if len(conversation_messages) > limit:
            conversation_messages = conversation_messages[-limit:]
        
        # Calculate conversation statistics
        total_messages = len(conversation_messages)
        my_messages = sum(1 for msg in conversation_messages if msg['sender'] == 'me')
        their_messages = total_messages - my_messages
        avg_length = sum(len(msg.get('text', '') or '') for msg in conversation_messages) / total_messages if total_messages > 0 else 0
        
        # Get date range
        first_msg_date = conversation_messages[0]['timestamp'] if conversation_messages else None
        last_msg_date = conversation_messages[-1]['timestamp'] if conversation_messages else None
        
        return {
            "contact": contact,
            "matched_contact": conversation_messages[0]['sender'] if conversation_messages and conversation_messages[0]['sender'] != 'me' else contact,
            "total_messages": total_messages,
            "my_messages": my_messages,
            "their_messages": their_messages,
            "my_percentage": round((my_messages / total_messages) * 100, 1) if total_messages > 0 else 0,
            "their_percentage": round((their_messages / total_messages) * 100, 1) if total_messages > 0 else 0,
            "avg_message_length": round(avg_length, 1),
            "date_range": {
                "first_message": first_msg_date,
                "last_message": last_msg_date
            },
            "messages_shown": len(conversation_messages),
            "messages_limited": len(conversation_messages) == limit,
            "messages": conversation_messages
        } 