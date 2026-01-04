def enforce_strict_paths(steps: list[dict], tree: list[str]) -> list[dict]:
    tree_set = set(tree)

    for step in steps:
        file_path = step.get("file", "").strip()

        if not file_path:
            continue

        if file_path not in tree_set:
            step["explanation"] += (
                " File does not exist in repository. "
                "You must CREATE this file."
            )
            step["verification"] = (
                "File created at specified path and project builds successfully."
            )

    return steps