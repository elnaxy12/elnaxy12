def update_readme(user, repo_name="README.md"):
    repos = get_repos(user)
    counter = Counter()
    for r in repos:
        langs = get_langs_for_repo(user, r["name"])
        counter.update(langs)

    md_table = make_md_table(counter)

    start_tag = "<!--START_SECTION:langs-->"
    end_tag = "<!--END_SECTION:langs-->"

    with open(repo_name, "r", encoding="utf-8") as f:
        content = f.read()

    if start_tag in content and end_tag in content:
        new_content = re.sub(
            rf"{start_tag}.*?{end_tag}",
            f"{start_tag}\n{md_table}\n{end_tag}",
            content,
            flags=re.DOTALL
        )
    else:
        if "## Top Languages" in content:
            new_content = content.replace(
                "## Top Languages",
                f"## Top Languages\n\n{start_tag}\n{md_table}\n{end_tag}"
            )
        else:
            new_content = content.strip() + f"\n\n## Top Languages\n\n{start_tag}\n{md_table}\n{end_tag}"

    with open(repo_name, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("✅ README updated safely (markers used).")
