import re

import mistune
from bs4 import BeautifulSoup


def split_text_by_emoji(text: str) -> list[str]:
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags (iOS)
        "\U00002500-\U00002bef"  # chinese char
        "\U00002702-\U000027b0"
        "\U00002702-\U000027b0"
        "\U000024c2-\U0001f251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2b55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\u3030"
        "\u303d"
        "\ufe0f"  # dingbats
        "\u2069"
        "\u2066"
        "\u2068"
        "\u2067"
        "]+",
        flags=re.UNICODE,
    )
    parts = emoji_pattern.split(text)
    emojis = emoji_pattern.findall(text)
    result = []
    for part, em in zip(parts, emojis + [""]):
        result.append((part, em if em else None))
    return result


def markdown_to_plain_text(markdown_text: str) -> str:
    # Convert Markdown to HTML
    html = mistune.markdown(markdown_text)

    # Parse the HTML and extract plain text
    soup = BeautifulSoup(html, "html.parser")
    plain_text = soup.get_text()

    return plain_text.strip()
