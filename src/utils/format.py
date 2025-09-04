import re

def clean_text(text):
    """Remove links from Reddit post text."""
    return re.sub(r"http\S+|www\S+", "", text).strip()

def clean_format(text):
    return re.sub(r"\*\*(.*?)\*\*", r"\1", text)

if __name__ == "__main__":
    print(clean_text(
        """Perplexity AI has launched a new browser called *Comet*. Read more here: https://www.techradar.com/pro/the-surveillance-browser-trap-ai-companies-are-copying-big-techs-worst-privacy-mistakes?utm_source=chatgpt.com 
         """))