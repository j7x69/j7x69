import os
import json
import urllib.request
import html

USERNAME = os.getenv("GITHUB_REPOSITORY_OWNER", "j7x69")
TOKEN = os.getenv("GITHUB_TOKEN", "")
FEATURED_REPO = "PreservesPitchYT"  # Đổi tên repo bạn muốn làm nổi bật ở đây

def fetch_api(url):
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "GitHub-Profile-SVG-Generator")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def get_github_stats():
    repos = fetch_api(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner")
    
    total_stars = 0
    total_forks = 0
    total_downloads = 0
    public_repos = 0
    
    featured_info = {
        "name": FEATURED_REPO,
        "desc": "Chrome extension that unlocks custom audio pitch shifting on YouTube HTML5 videos.",
        "stars": 0,
        "forks": 0,
        "downloads": 0
    }

    if not isinstance(repos, list):
        return total_stars, total_forks, total_downloads, public_repos, featured_info

    for r in repos:
        if r.get("fork"):
            continue
        public_repos += 1
        stars = r.get("stargazers_count", 0)
        forks = r.get("forks_count", 0)
        total_stars += stars
        total_forks += forks

        repo_name = r.get("name")
        # Đếm lượt tải từ Releases của từng repo
        releases = fetch_api(f"https://api.github.com/repos/{USERNAME}/{repo_name}/releases")
        repo_dl = 0
        if isinstance(releases, list):
            for rel in releases:
                for asset in rel.get("assets", []):
                    repo_dl += asset.get("download_count", 0)
        total_downloads += repo_dl

        if repo_name.lower() == FEATURED_REPO.lower():
            featured_info["name"] = repo_name
            featured_info["desc"] = r.get("description") or featured_info["desc"]
            featured_info["stars"] = stars
            featured_info["forks"] = forks
            featured_info["downloads"] = repo_dl

    return total_stars, total_forks, total_downloads, public_repos, featured_info

def generate_banner_svg(stars, repos):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="850" height="170" viewBox="0 0 850 170" fill="none">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="50%" stop-color="#111927"/>
      <stop offset="100%" stop-color="#0d1f2d"/>
    </linearGradient>
    <radialGradient id="glow" cx="80%" cy="50%" r="45%">
      <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#00e5ff" stop-opacity="0"/>
    </radialGradient>
  </defs>
  
  <rect width="848" height="168" x="1" y="1" rx="12" fill="url(#bg)" stroke="#30363d" stroke-width="1.5"/>
  <rect width="848" height="168" x="1" y="1" rx="12" fill="url(#glow)"/>

  <!-- Đồ họa mạng lưới chấm bi & đường nối bên phải -->
  <g stroke="#00e5ff" stroke-opacity="0.25" stroke-width="1">
    <line x1="620" y1="45" x2="680" y2="80"/>
    <line x1="680" y1="80" x2="750" y2="50"/>
    <line x1="680" y1="80" x2="710" y2="130"/>
    <line x1="750" y1="50" x2="790" y2="110"/>
    <line x1="710" y1="130" x2="790" y2="110"/>
    <line x1="580" y1="115" x2="680" y2="80"/>
  </g>
  <g fill="#00e5ff">
    <circle cx="620" cy="45" r="3.5" opacity="0.7"/>
    <circle cx="680" cy="80" r="5" opacity="0.9"/>
    <circle cx="750" cy="50" r="4" opacity="0.6"/>
    <circle cx="710" cy="130" r="3.5" opacity="0.7"/>
    <circle cx="790" cy="110" r="4.5" opacity="0.8"/>
    <circle cx="580" cy="115" r="3" opacity="0.5"/>
  </g>

  <text x="36" y="62" fill="#f0f6fc" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="28" font-weight="700">Vũ Anh Đức <tspan fill="#00e5ff" font-size="18" font-weight="500">Jax</tspan></text>
  <text x="36" y="96" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="14">Python &amp; C# Developer  ·  Automation &amp; Media Tools  ·  Hardware Modder</text>
  <text x="36" y="130" fill="#6e7681" font-family="ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace" font-size="12">★ {stars:,} stars   ·   📦 {repos} public repos   ·   📍 Czechia</text>
</svg>'''
    with open("assets/banner.svg", "w", encoding="utf-8") as f:
        f.write(svg)

def generate_stats_svg(stars, forks, downloads, repos):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="850" height="110" viewBox="0 0 850 110" fill="none">
  <style>
    .card {{ fill: #0d1117; stroke: #30363d; stroke-width: 1.5; }}
    .num {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 26px; font-weight: 700; text-anchor: middle; }}
    .lbl {{ fill: #8b949e; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 10px; font-weight: 600; letter-spacing: 1px; text-anchor: middle; }}
    .ico {{ font-family: sans-serif; font-size: 14px; text-anchor: middle; }}
  </style>

  <!-- Card 1: Stars -->
  <rect x="1" y="5" width="200" height="100" rx="10" class="card"/>
  <text x="101" y="30" fill="#e3b341" class="ico">★</text>
  <text x="101" y="64" fill="#e3b341" class="num">{stars:,}</text>
  <text x="101" y="88" class="lbl">TOTAL STARS</text>

  <!-- Card 2: Forks -->
  <rect x="217" y="5" width="200" height="100" rx="10" class="card"/>
  <text x="317" y="30" fill="#58a6ff" class="ico">⑂</text>
  <text x="317" y="64" fill="#58a6ff" class="num">{forks:,}</text>
  <text x="317" y="88" class="lbl">FORKS</text>

  <!-- Card 3: Downloads -->
  <rect x="433" y="5" width="200" height="100" rx="10" class="card"/>
  <text x="533" y="30" fill="#3fb950" class="ico">↓</text>
  <text x="533" y="64" fill="#3fb950" class="num">{downloads:,}</text>
  <text x="533" y="88" class="lbl">DOWNLOADS</text>

  <!-- Card 4: Public Repos -->
  <rect x="649" y="5" width="200" height="100" rx="10" class="card"/>
  <text x="749" y="30" fill="#a371f7" class="ico">▣</text>
  <text x="749" y="64" fill="#a371f7" class="num">{repos:,}</text>
  <text x="749" y="88" class="lbl">PUBLIC REPOS</text>
</svg>'''
    with open("assets/stats.svg", "w", encoding="utf-8") as f:
        f.write(svg)

def generate_featured_svg(info):
    raw_desc = info.get("desc") or ""
    desc_trimmed = raw_desc[:75] + ("..." if len(raw_desc) > 75 else "")
    desc = html.escape(desc_trimmed)
    name = html.escape(str(info.get("name", "")))
    stars = info.get("stars", 0)
    forks = info.get("forks", 0)
    downloads = info.get("downloads", 0)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="850" height="105" viewBox="0 0 850 105" fill="none">
  <rect width="848" height="103" x="1" y="1" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1.5"/>
  <rect width="4" height="103" x="1" y="1" rx="2" fill="#00e5ff"/>
  
  <text x="28" y="35" fill="#8b949e" font-family="ui-monospace, SFMono-Regular, monospace" font-size="11" letter-spacing="1">FEATURED REPOSITORY</text>
  <text x="28" y="62" fill="#f0f6fc" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="20" font-weight="700">{name}</text>
  <text x="28" y="86" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="13">{desc}</text>

  <!-- Số liệu bên phải -->
  <text x="610" y="55" fill="#e3b341" font-family="-apple-system, sans-serif" font-size="18" font-weight="700" text-anchor="middle">{stars:,}</text>
  <text x="610" y="75" fill="#8b949e" font-family="ui-monospace, monospace" font-size="10" text-anchor="middle">STARS</text>

  <text x="700" y="55" fill="#58a6ff" font-family="-apple-system, sans-serif" font-size="18" font-weight="700" text-anchor="middle">{forks:,}</text>
  <text x="700" y="75" fill="#8b949e" font-family="ui-monospace, monospace" font-size="10" text-anchor="middle">FORKS</text>

  <text x="790" y="55" fill="#3fb950" font-family="-apple-system, sans-serif" font-size="18" font-weight="700" text-anchor="middle">{downloads:,}</text>
  <text x="790" y="75" fill="#8b949e" font-family="ui-monospace, monospace" font-size="10" text-anchor="middle">DOWNLOADS</text>
</svg>'''
    with open("assets/featured.svg", "w", encoding="utf-8") as f:
        f.write(svg)

if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    stars, forks, downloads, repos, featured = get_github_stats()
    generate_banner_svg(stars, repos)
    generate_stats_svg(stars, forks, downloads, repos)
    generate_featured_svg(featured)
    print("Generated all SVG assets successfully!")
