def select_relevant_files(tree: list[str], issue_text: str, max_files=5) -> list[str]:
    keywords = issue_text.lower().split()
    candidates = []

    for path in tree:
        for word in keywords:
            if word in path.lower():
                candidates.append(path.rstrip("/"))
                break

        if len(candidates) >= max_files:
            break

    return candidates
