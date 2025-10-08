# tools/update_top_langs.py
import os, requests, base64, json
from collections import Counter

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("GITHUB_USERNAME")  # set in action
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def get_repos(user):
    repos = []
    page = 1
    while True:
        r = requests.get(f"https://api.github.com/users/{user}/repos?per_page=100&page={page}", headers=HEADERS)
        data = r.json()
        if not data: break
        repos.extend(data); page += 1
    return repos

def get_langs_for_repo(owner, repo):
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/languages", headers=HEADERS)
    return r.json() if r.status_code == 200 else {}

def make_md_table(lang_counter):
    total = sum(lang_counter.values()) or 1
    lines = ["| Language | Bytes | % |", "|---:|---:|---:|"]
    for lang, b in lang_counter.most_common():
        pct = b / total * 100
        bar = '█' * int(pct // 4)  # simple bar
        lines.append(f"| {lang} | {b:,} | {pct:.1f}% {bar} |")
    return "\n".join(lines)

def update_readme(user, repo_name="README.md", section_title="## Top Languages"):
    repos = get_repos(user)
    counter = Counter()
    for r in repos:
        langs = get_langs_for_repo(user, r["name"])
        counter.update(langs)
    md_table = make_md_table(counter)

    # load README
    with open(repo_name, "r", encoding="utf-8") as f:
        content = f.read()

    start = content.find(section_title)
    if start == -1:
        # append at end
        new_content = content + "\n\n" + section_title + "\n\n" + md_table + "\n"
    else:
        # replace from section_title to next H2/H1 or end
        tail = content[start:]
        # find next header at same or higher level
        import re
        m = re.search(r"\n## |\n# ", tail[1:])  # skip first char to avoid matching same
        if m:
            end_pos = start + 1 + m.start()
            new_content = content[:start] + section_title + "\n\n" + md_table + "\n" + content[end_pos:]
        else:
            new_content = content[:start] + section_title + "\n\n" + md_table + "\n"

    with open(repo_name, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("README updated.")

if __name__ == "__main__":
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME") or "elnaxy12"
    update_readme(GITHUB_USERNAME, repo_name="README.md")
