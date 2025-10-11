import os, requests
from collections import Counter

# Ambil token & username dari environment (otomatis dari workflow)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("GITHUB_USERNAME")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def get_repos(user):
    """Ambil semua repository milik user"""
    repos = []
    page = 1
    while True:
        r = requests.get(f"https://api.github.com/users/{user}/repos?per_page=100&page={page}", headers=HEADERS)
        data = r.json()
        if not data or "message" in data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_langs_for_repo(owner, repo):
    """Ambil statistik bahasa dari tiap repo"""
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/languages", headers=HEADERS)
    return r.json() if r.status_code == 200 else {}

def make_md_table(lang_counter):
    """Buat tabel markdown"""
    total = sum(lang_counter.values()) or 1
    lines = [
        "<div align=\"center\">\n",
        "| Language | Bytes | % |",
        "|---:|---:|---:|",
    ]
    for lang, b in lang_counter.most_common():
        pct = b / total * 100
        bar = '█' * int(pct // 4)
        lines.append(f"| {lang} | {b:,} | {pct:.1f}% {bar} |")
    lines.append("\n</div>")
    return "\n".join(lines)

def update_readme(user, repo_name="README.md"):
    """Update tabel di antara tag <!--START_SECTION:top-langs--> dan <!--END_SECTION:top-langs-->"""
    repos = get_repos(user)
    counter = Counter()
    for r in repos:
        langs = get_langs_for_repo(user, r["name"])
        counter.update(langs)

    md_table = make_md_table(counter)

    with open(repo_name, "r", encoding="utf-8") as f:
        content = f.read()

    start_tag = "<!--START_SECTION:top-langs-->"
    end_tag = "<!--END_SECTION:top-langs-->"
    start = content.find(start_tag)
    end = content.find(end_tag)

    if start == -1 or end == -1:
        print("❌ Tag pembatas tidak ditemukan di README.md — tidak ada perubahan.")
        return

    new_content = (
        content[: start + len(start_tag)]
        + "\n"
        + md_table
        + "\n"
        + content[end:]
    )

    with open(repo_name, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✅ README berhasil diperbarui.")

if __name__ == "__main__":
    user = USERNAME or "elnaxy12"
    update_readme(user)
