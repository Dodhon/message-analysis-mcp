# iMessage Analysis MCP Server

MCP server for analyzing your iMessage data on macOS. Works with Claude Desktop.

## Privacy Notice

This accesses your iMessage database at `~/Library/Messages/chat.db`. Everything stays local - no data leaves your machine.

## Requirements

- macOS 10.14+
- Python 3.8+
- Claude Desktop
- Full Disk Access permission

## Setup

```bash
git clone https://github.com/Dodhon/message-analysis-mcp.git
cd imessage-analysis-mcp
pip install -r requirements.txt
```

Grant Full Disk Access:
1. System Settings → Privacy & Security → Full Disk Access
2. Add Terminal and/or Python
3. Restart Terminal

Configure Claude:
```bash
python3 setup_claude.py
```

Restart Claude Desktop.

## Tools

**Basic Analysis**
- `get_basic_statistics()` - Total messages, senders, averages
- `get_word_frequency()` - Most used words
- `get_conversation_analysis()` - Who talks more with each contact

**Search & Exploration**
- `list_contacts()` - All contacts with message counts
- `search_messages()` - Find messages with specific text
- `get_contact_statistics()` - Stats for specific person
- `get_conversation()` - Full conversation history (actual messages)

## Examples

Ask Claude:
- "What are my basic iMessage stats?"
- "Show my most used words"
- "List my top contacts"
- "Get my last 20 messages with +1 (555) 123-4567"

## Manual Setup

If auto-setup fails:

```bash
which python3  # Get your Python path
```

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "imessage-analysis": {
      "command": "/your/python/path",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

## Troubleshooting

**"Failed to fetch messages"** - Need Full Disk Access  
**"No module named 'mcp'"** - Run `pip install -r requirements.txt`  
**"No messages found for contact"** - Use `list_contacts()` to see exact formats  
**Server not connecting** - Check Python path in config  

## Known Issues

- Shows phone numbers/emails instead of contact names (PRs welcome if you know how to fix this)
- Date filtering not implemented yet

## Sample Output

```json
{
  "total_messages": 15420,
  "unique_senders": 89,
  "top_senders": {
    "+1 (555) 123-4567": 3245
  }
}
```

## 🔒 Data Security

- **Local Processing**: All analysis happens on your Mac
- **No Network Requests**: The MCP server doesn't connect to internet
- **Temporary Storage**: Message data is only held in memory during analysis
- **Reversible**: Uninstall anytime by removing the Claude Desktop config

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Development setup:
```bash
git clone https://github.com/yourusername/imessage-analysis-mcp.git
cd imessage-analysis-mcp
pip install -r requirements.txt
python3 main.py  # Test just to see how it works
```

## License

MIT License - see [LICENSE](LICENSE).

Built for Claude Desktop and MCP. 