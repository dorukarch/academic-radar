def is_open_access(title, link):
    keywords = [
        "open access", "open-access", "free access",
        "/open", "/oa", ".pdf", "openresearch"
    ]
    text = (title + " " + link).lower()
    return any(k in text for k in keywords)
