from backend.app.tools.tool import Tool


class WebResearchTool(Tool):
    name = "web_research"
    description = (
        "Searches the web for current information and returns "
        "relevant search results."
    )

    def execute(
        self,
        query: str,
        max_results: int = 5
    ):
        try:
            from ddgs import DDGS

            query = query.strip()

            if not query:
                return {
                    "success": False,
                    "error": "Search query cannot be empty."
                }

            max_results = max(
                1,
                min(int(max_results), 10)
            )

            results = []

            with DDGS() as search:
                search_results = search.text(
                    query,
                    max_results=max_results
                )

                for item in search_results:
                    results.append({
                        "title": item.get("title"),
                        "url": item.get("href"),
                        "snippet": item.get("body")
                    })

            return {
                "success": True,
                "query": query,
                "count": len(results),
                "results": results
            }

        except ImportError:
            return {
                "success": False,
                "error": (
                    "The 'ddgs' package is not installed. "
                    "Install it with: pip install ddgs"
                )
            }

        except Exception as error:
            return {
                "success": False,
                "query": query,
                "error": str(error)
            }