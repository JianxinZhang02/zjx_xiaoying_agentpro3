"""Tool execution and deterministic error injection; no business decisions."""
import copy


class ToolRuntime:
    def __init__(self, kb, failures=None):
        self.kb = kb
        self.failures = copy.deepcopy(failures or {})
        self.read_evidence = {}
        self.observed = []

    def execute(self, name, arguments):
        try:
            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments must be an object")
            if name not in ("search_documents", "read_document"):
                return self._error("unknown_tool", "Unknown tool: " + str(name))
            allowed = {"purpose", "query", "top_k"} if name == "search_documents" else {"purpose", "doc_id", "chunk_id"}
            if set(arguments) - allowed:
                raise ValueError("Unknown tool argument")
            if not isinstance(arguments.get("purpose"), str) or not arguments["purpose"].strip():
                raise ValueError("A short public purpose is required")
            if name == "search_documents":
                if not isinstance(arguments.get("query"), str) or not arguments["query"].strip():
                    raise ValueError("query must be nonempty text")
                top_k = arguments.get("top_k", 4)
                if type(top_k) is not int or not 1 <= top_k <= 10:
                    raise ValueError("top_k must be an integer from 1 to 10")
            else:
                if not isinstance(arguments.get("doc_id"), str):
                    raise ValueError("doc_id must be text")
                if arguments.get("chunk_id") is not None and not isinstance(arguments["chunk_id"], str):
                    raise ValueError("chunk_id must be text or null")
            remaining = self.failures.get(name, 0)
            if remaining == "always" or (isinstance(remaining, int) and remaining > 0):
                if remaining != "always":
                    self.failures[name] -= 1
                result = self._error("injected_failure", "Synthetic tool failure. Retry or find other evidence; do not claim a successful read.")
            elif name == "search_documents":
                result = {"ok": True, "results": self.kb.search(arguments["query"], arguments.get("top_k", 4))}
            else:
                meta, chunks = self.kb.read(arguments["doc_id"], arguments.get("chunk_id"))
                for chunk in chunks:
                    self.read_evidence[(meta["doc_id"], chunk["chunk_id"])] = chunk["text"]
                result = {"ok": True, "document": meta, "chunks": chunks, "untrusted_data": True}
        except (ValueError, KeyError, TypeError) as exc:
            result = self._error("invalid_arguments" if not isinstance(exc, KeyError) else "not_found", str(exc))
        self.observed.append({"name": name, "arguments": copy.deepcopy(arguments), "result": result})
        return result

    @staticmethod
    def _error(code, message):
        return {"ok": False, "error": {"code": code, "message": message}}
