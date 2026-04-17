# DeskGenie MCP Servers

Standalone MCP (Model Context Protocol) server processes that expose DeskGenie
tools to any MCP-compatible client.

---

## `file_ops_server.py` — deskgenie-files

Exposes 18 file operation tools over stdio MCP transport:

| Category | Tools |
|----------|-------|
| PDF | `pdf_extract_pages`, `pdf_delete_pages`, `pdf_merge`, `pdf_split`, `pdf_to_images` |
| Image | `process_image` (convert/resize/compress), `images_to_pdf`, `batch_convert_images` |
| File management | `batch_rename_files`, `organize_files_by_type`, `find_duplicate_files` |
| Document | `word_to_pdf`, `extract_text_from_pdf`, `ocr_image` |
| Media | `video_to_audio`, `compress_video`, `get_media_info` |
| Directory | `list_directory` |

### Running standalone

```bash
# From the DeskGenie project root (venv activated)
python mcp_servers/file_ops_server.py
```

The server communicates over stdin/stdout (stdio transport). It is designed to
be launched as a subprocess by an MCP client — not to be run interactively.

### Using with DeskGenie

Add the following entry to the `mcpServers` section of your `config.json`:

```json
"deskgenie-files": {
  "transport": "stdio",
  "command": "python",
  "args": ["mcp_servers/file_ops_server.py"]
}
```

If you launch DeskGenie from outside the project root, use the absolute path:

```json
"deskgenie-files": {
  "transport": "stdio",
  "command": "C:/path/to/DeskGenie/venv/Scripts/python.exe",
  "args": ["C:/path/to/DeskGenie/mcp_servers/file_ops_server.py"]
}
```

### Using with Claude Desktop / other MCP clients

Same config structure — add the entry to your client's MCP settings file
(e.g. `claude_desktop_config.json`).

### Architecture

```
MCP client (DeskGenie agent / Claude Desktop)
    ↓ JSON-RPC over stdio
file_ops_server.py   (FastMCP thin wrappers)
    ↓ direct Python call
tools/core/files.py  (pure business logic, no LangChain)
```

`tools/core/files.py` is the single source of truth — both the LangChain
wrappers in `tools/desktop_tools.py` and this MCP server delegate to it.

### Dependencies

- `fastmcp` — MCP server framework
- All `tools/core/files.py` dependencies (PIL, PyMuPDF, pypdf, etc.) must be
  installed in the same Python environment.

Install everything with:

```bash
pip install -r requirements.txt
```
