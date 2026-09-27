from backend.app.tools.browser import BrowserTool


browser = BrowserTool()


print("\n========== BROWSER TOOL TEST ==========")


result = browser.execute(
    "https://fastapi.tiangolo.com/"
)


print("Success:", result["success"])
print("URL:", result.get("url"))
print("Status:", result.get("status_code"))
print("Title:", result.get("title"))
print("Text length:", result.get("text_length"))
print("Links:", len(result.get("links", [])))


print("\n========== TEST RESULT ==========")


if (
    result["success"]
    and result["status_code"] == 200
    and result["title"]
    and result["text_length"] > 0
    and len(result["links"]) > 0
):
    print("BROWSER TOOL TEST PASSED")
else:
    print("BROWSER TOOL TEST FAILED")