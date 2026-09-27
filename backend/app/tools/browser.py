from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from backend.app.tools.tool import Tool


class BrowserTool(Tool):
    name = "browser"

    description = (
        "Opens webpages, extracts page text, returns links, "
        "and can follow links from a webpage."
    )

    def execute(
        self,
        url: str,
        max_text_length: int = 5000,
        link_text: str | None = None,
        link_index: int | None = None
    ):
        try:
            url = url.strip()

            if not url:
                return {
                    "success": False,
                    "error": "URL cannot be empty."
                }

            if not (
                url.startswith("http://")
                or url.startswith("https://")
            ):
                return {
                    "success": False,
                    "error": (
                        "URL must start with "
                        "http:// or https://."
                    )
                }

            max_text_length = max(
                500,
                min(int(max_text_length), 20000)
            )

            response = self._request_page(url)

            soup = self._parse_page(
                response.text
            )

            title = (
                soup.title.get_text(strip=True)
                if soup.title
                else None
            )

            text = soup.get_text(
                separator=" ",
                strip=True
            )

            text = " ".join(text.split())

            links = self._extract_links(
                soup,
                response.url
            )

            # ---------------------------------------------
            # Follow a requested link
            # ---------------------------------------------

            selected_link = None

            if link_index is not None:

                if (
                    link_index < 0
                    or link_index >= len(links)
                ):
                    return {
                        "success": False,
                        "url": response.url,
                        "error": (
                            f"Invalid link_index: "
                            f"{link_index}"
                        ),
                        "available_links": len(links)
                    }

                selected_link = links[link_index]

            elif link_text:

                search_text = (
                    link_text.strip().lower()
                )

                for link in links:
                    if search_text in (
                        link["text"].lower()
                    ):
                        selected_link = link
                        break

                if selected_link is None:
                    return {
                        "success": False,
                        "url": response.url,
                        "error": (
                            f"Link containing "
                            f"'{link_text}' was not found."
                        ),
                        "available_links": len(links)
                    }

            # ---------------------------------------------
            # Open selected link
            # ---------------------------------------------

            followed_page = None

            if selected_link:

                followed_response = self._request_page(
                    selected_link["url"]
                )

                followed_soup = self._parse_page(
                    followed_response.text
                )

                followed_title = (
                    followed_soup.title.get_text(
                        strip=True
                    )
                    if followed_soup.title
                    else None
                )

                followed_text = followed_soup.get_text(
                    separator=" ",
                    strip=True
                )

                followed_text = " ".join(
                    followed_text.split()
                )

                followed_links = self._extract_links(
                    followed_soup,
                    followed_response.url
                )

                followed_page = {
                    "url": followed_response.url,
                    "status_code":
                        followed_response.status_code,
                    "title": followed_title,
                    "text":
                        followed_text[:max_text_length],
                    "text_length":
                        len(followed_text),
                    "links":
                        followed_links[:100]
                }

            result = {
                "success": True,
                "url": response.url,
                "status_code": response.status_code,
                "title": title,
                "text": text[:max_text_length],
                "text_length": len(text),
                "links": links[:100]
            }

            if selected_link:
                result["selected_link"] = selected_link

            if followed_page:
                result["followed_page"] = followed_page

            return result

        except requests.RequestException as error:
            return {
                "success": False,
                "url": url,
                "error": (
                    f"Browser request failed: {error}"
                )
            }

        except Exception as error:
            return {
                "success": False,
                "url": url,
                "error": str(error)
            }

    def _request_page(self, url: str):
        return requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "Chrome/153.0 Safari/537.36"
                )
            }
        )

    def _parse_page(self, html: str):
        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for element in soup(
            ["script", "style", "noscript"]
        ):
            element.decompose()

        return soup

    def _extract_links(
        self,
        soup,
        base_url: str
    ):
        links = []

        for link in soup.find_all(
            "a",
            href=True
        ):
            href = link.get("href")

            if not href:
                continue

            link_text = link.get_text(
                " ",
                strip=True
            )

            absolute_url = urljoin(
                base_url,
                href
            )

            links.append({
                "text": link_text,
                "url": absolute_url
            })

        return links


browser_tool = BrowserTool()