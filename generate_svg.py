import os
import json
import urllib.request
import html
import math

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

USERNAME = os.getenv("GITHUB_REPOSITORY_OWNER", "j7x69")
TOKEN = os.getenv("GITHUB_TOKEN", "")
FEATURED_REPO = "PreservesPitchYT"  # Repo được ghim làm tâm điểm

# ---------------------------------------------------------
# GitHub Data Fetcher
# ---------------------------------------------------------
def fetch_api(url):
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "GitHub-Profile-SVG-Generator-Jax")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
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
        "desc": "Chrome extension unlocking custom audio pitch shifting on YouTube HTML5 videos.",
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

        repo_name = r.get("name", "")
        # Lấy số lượt tải từ Releases của từng repo
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

# ---------------------------------------------------------
# Pixel Art Generator for 'JAX' (3D Extruded Vector Blocks)
# ---------------------------------------------------------
PIXEL_LETTERS = {
    'J': [
        '111111',
        '000110',
        '000110',
        '000110',
        '000110',
        '110110',
        '110110',
        '011110'
    ],
    'A': [
        '011110',
        '110011',
        '110011',
        '111111',
        '110011',
        '110011',
        '110011',
        '110011'
    ],
    'X': [
        '110011',
        '110011',
        '011110',
        '001100',
        '001100',
        '011110',
        '110011',
        '110011'
    ]
}

def generate_pixel_jax(start_x, start_y, px_size=8, depth=5):
    spacing = 16
    elements = []
    
    # Layer 1: Khối bóng đổ đáy sâu 3D (Deep Bronze / Dark Amber)
    curr_x = start_x
    for char in ['J', 'A', 'X']:
        matrix = PIXEL_LETTERS[char]
        for r_idx, row in enumerate(matrix):
            for c_idx, val in enumerate(row):
                if val == '1':
                    x = curr_x + c_idx * px_size + depth
                    y = start_y + r_idx * px_size + depth
                    elements.append(f'<rect x="{x}" y="{y}" width="{px_size}" height="{px_size}" fill="#422000" rx="1"/>')
        curr_x += len(matrix[0]) * px_size + spacing

    # Layer 2: Khối vát đồng 3D chuyển tiếp (#7A4600)
    curr_x = start_x
    for char in ['J', 'A', 'X']:
        matrix = PIXEL_LETTERS[char]
        for r_idx, row in enumerate(matrix):
            for c_idx, val in enumerate(row):
                if val == '1':
                    x = curr_x + c_idx * px_size + int(depth * 0.5)
                    y = start_y + r_idx * px_size + int(depth * 0.5)
                    elements.append(f'<rect x="{x}" y="{y}" width="{px_size}" height="{px_size}" fill="#7a4600" rx="1"/>')
        curr_x += len(matrix[0]) * px_size + spacing

    # Layer 3: Viền vàng kim hoàng gia (#FFDD00)
    curr_x = start_x
    for char in ['J', 'A', 'X']:
        matrix = PIXEL_LETTERS[char]
        for r_idx, row in enumerate(matrix):
            for c_idx, val in enumerate(row):
                if val == '1':
                    x = curr_x + c_idx * px_size
                    y = start_y + r_idx * px_size
                    elements.append(f'<rect x="{x}" y="{y}" width="{px_size}" height="{px_size}" fill="#ffdd00" rx="1.2"/>')
        curr_x += len(matrix[0]) * px_size + spacing

    # Layer 4: Mặt trước đỏ cờ Tổ Quốc (#DA251D)
    curr_x = start_x
    for char in ['J', 'A', 'X']:
        matrix = PIXEL_LETTERS[char]
        for r_idx, row in enumerate(matrix):
            for c_idx, val in enumerate(row):
                if val == '1':
                    x = curr_x + c_idx * px_size + 1.2
                    y = start_y + r_idx * px_size + 1.2
                    elements.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{px_size-2.4:.1f}" height="{px_size-2.4:.1f}" fill="#da251d" rx="0.6"/>')
        curr_x += len(matrix[0]) * px_size + spacing

    # Layer 5: Điểm sáng lấp lánh góc trên (#FFF5A6)
    curr_x = start_x
    for char in ['J', 'A', 'X']:
        matrix = PIXEL_LETTERS[char]
        for r_idx, row in enumerate(matrix):
            for c_idx, val in enumerate(row):
                if val == '1':
                    x = curr_x + c_idx * px_size + 1.5
                    y = start_y + r_idx * px_size + 1.5
                    elements.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="2" height="2" fill="#fff5a6" opacity="0.9"/>')
        curr_x += len(matrix[0]) * px_size + spacing

    return '\n    '.join(elements)

# ---------------------------------------------------------
# 3D Faceted Golden Star Generator (Ngôi sao vàng 5 cánh)
# ---------------------------------------------------------
def generate_star_facets(cx, cy, r_out):
    r_in = r_out * 0.381966  # Tỉ lệ vàng chuẩn của ngôi sao 5 cánh
    pts = []
    angle = -math.pi / 2
    step = math.pi / 5
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        angle += step

    elements = []
    # 10 đa giác tam giác tạo hiệu ứng 3D khối vát ánh sáng
    for i in range(10):
        p1 = pts[i]
        p2 = pts[(i + 1) % 10]
        col = "#ffe55c" if i % 2 == 0 else "#d48800"
        elements.append(f'<polygon points="{cx:.1f},{cy:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{col}"/>')

    # Viền chu vi vàng kim sắc nét
    outer_pts_str = " ".join([f"{p[0]:.1f},{p[1]:.1f}" for p in pts])
    elements.append(f'<polygon points="{outer_pts_str}" fill="none" stroke="#fff9d2" stroke-width="1.2" stroke-linejoin="round"/>')

    # Lõi ngọc phát quang trung tâm
    elements.append(f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="#fff9d2" opacity="0.9"/>')
    elements.append(f'<circle cx="{cx}" cy="{cy}" r="1.5" fill="#ffffff"/>')

    return '\n      '.join(elements)

# ---------------------------------------------------------
# 1. Main Banner SVG (Vietnam Flag + Retro Cyberpunk Arcade)
# ---------------------------------------------------------
def generate_banner_svg(stars, repos):
    star_cx, star_cy = 715, 90
    star_r = 50
    star_facets = generate_star_facets(star_cx, star_cy, star_r)
    jax_pixel_blocks = generate_pixel_jax(40, 50, px_size=8, depth=5)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="850" height="180" viewBox="0 0 850 180" fill="none">
  <defs>
    <!-- Background Gradient: Obsidian Crimson Đỏ thẫm -->
    <linearGradient id="bgObsidian" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#120204"/>
      <stop offset="50%" stop-color="#1f0508"/>
      <stop offset="100%" stop-color="#2a070c"/>
    </linearGradient>

    <!-- Star Radiant Ambient Glow (Hào quang sao vàng) -->
    <radialGradient id="starAmbient" cx="{star_cx}" cy="{star_cy}" r="160" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#ffdd00" stop-opacity="0.32"/>
      <stop offset="35%" stop-color="#da251d" stop-opacity="0.22"/>
      <stop offset="70%" stop-color="#da251d" stop-opacity="0.06"/>
      <stop offset="100%" stop-color="#120204" stop-opacity="0"/>
    </radialGradient>

    <!-- Animated Border Laser Gradient -->
    <linearGradient id="borderLaser" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ffdd00" stop-opacity="1"/>
      <stop offset="50%" stop-color="#da251d" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#ffdd00" stop-opacity="1"/>
    </linearGradient>

    <!-- Scanline Sweep Gradient -->
    <linearGradient id="scanlineGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ffdd00" stop-opacity="0"/>
      <stop offset="50%" stop-color="#ffdd00" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="#ffdd00" stop-opacity="0"/>
    </linearGradient>

    <!-- Retro Cyber Grid Pattern -->
    <pattern id="grid" width="18" height="18" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="0.85" fill="#da251d" fill-opacity="0.18"/>
    </pattern>
  </defs>

  <style>
    /* Animated Laser Border Ray - Viền chạy tia sáng */
    .laser-border {{
      stroke-dasharray: 140 1888;
      stroke-dashoffset: 0;
      animation: laserTravel 9s linear infinite;
    }}
    @keyframes laserTravel {{
      from {{ stroke-dashoffset: 2028; }}
      to {{ stroke-dashoffset: 0; }}
    }}

    /* Floating Bobbing Motion for 3D Pixel JAX */
    .jax-group {{
      animation: jaxBob 3.5s ease-in-out infinite;
    }}
    @keyframes jaxBob {{
      0%, 100% {{ transform: translateY(0px); }}
      50% {{ transform: translateY(-4px); }}
    }}

    /* Breathing Golden Star Animation - Sao vàng thở &amp; phát quang */
    .star-pulse {{
      transform-origin: {star_cx}px {star_cy}px;
      animation: starBreath 3s ease-in-out infinite;
    }}
    @keyframes starBreath {{
      0%, 100% {{
        transform: scale(1);
        filter: drop-shadow(0 0 10px rgba(255, 221, 0, 0.65)) drop-shadow(0 0 25px rgba(218, 37, 29, 0.45));
      }}
      50% {{
        transform: scale(1.05);
        filter: drop-shadow(0 0 22px rgba(255, 221, 0, 0.95)) drop-shadow(0 0 45px rgba(218, 37, 29, 0.7));
      }}
    }}

    /* Rotating Celestial Orbit Ring */
    .spin-ring {{
      transform-origin: {star_cx}px {star_cy}px;
      animation: orbitSpin 25s linear infinite;
    }}
    @keyframes orbitSpin {{
      from {{ transform: rotate(0deg); }}
      to {{ transform: rotate(360deg); }}
    }}

    /* Sweeping CRT Scanline - Quét tia sáng mềm mại */
    .scan-beam {{
      animation: scanMove 4s linear infinite;
    }}
    @keyframes scanMove {{
      0% {{ transform: translateY(-30px); }}
      100% {{ transform: translateY(190px); }}
    }}

    /* Blinking Terminal Cursor - Nhấp nháy terminal */
    .cursor-blink {{
      animation: cursorPulse 1s step-start infinite;
    }}
    @keyframes cursorPulse {{
      0%, 49% {{ opacity: 1; }}
      50%, 100% {{ opacity: 0; }}
    }}

    /* Particle Twinkle - Bụi sao lấp lánh */
    .twinkle-1 {{ animation: pTwinkle 2.5s ease-in-out infinite; }}
    .twinkle-2 {{ animation: pTwinkle 3.2s ease-in-out infinite 0.8s; }}
    .twinkle-3 {{ animation: pTwinkle 2.8s ease-in-out infinite 1.5s; }}
    .twinkle-4 {{ animation: pTwinkle 3.6s ease-in-out infinite 2.1s; }}
    @keyframes pTwinkle {{
      0%, 100% {{ opacity: 0.25; transform: scale(0.85); }}
      50% {{ opacity: 0.95; transform: scale(1.2); }}
    }}
  </style>

  <!-- Base Card Background -->
  <rect width="848" height="178" x="1" y="1" rx="14" fill="url(#bgObsidian)" stroke="#3d0e13" stroke-width="1.5"/>
  
  <!-- Subtle Grid Texture -->
  <rect width="848" height="178" x="1" y="1" rx="14" fill="url(#grid)"/>

  <!-- Star Radiant Ambient Halo -->
  <circle cx="{star_cx}" cy="{star_cy}" r="150" fill="url(#starAmbient)"/>

  <!-- CRT Scanline Light Beam -->
  <g clip-path="url(#cardClip)">
    <clipPath id="cardClip">
      <rect width="848" height="178" x="1" y="1" rx="14"/>
    </clipPath>
    <rect x="1" y="0" width="848" height="30" fill="url(#scanlineGrad)" class="scan-beam" pointer-events="none"/>
  </g>

  <!-- Tactical HUD Corner Brackets in Imperial Gold -->
  <g stroke="#ffdd00" stroke-width="1.8" opacity="0.85">
    <path d="M 8 18 L 8 8 L 18 8"/>
    <path d="M 840 18 L 840 8 L 830 8"/>
    <path d="M 8 162 L 8 172 L 18 172"/>
    <path d="M 840 162 L 840 172 L 830 172"/>
  </g>

  <!-- Animated Border Laser Ray -->
  <rect width="848" height="178" x="1" y="1" rx="14" fill="none" stroke="url(#borderLaser)" stroke-width="2" class="laser-border"/>

  <!-- Terminal HUD Tag Above JAX -->
  <g>
    <rect x="40" y="22" width="225" height="20" rx="3" fill="#200609" stroke="#7a1c24" stroke-width="1"/>
    <circle cx="50" cy="32" r="3" fill="#da251d"/>
    <text x="60" y="36" fill="#ffdd00" font-family="'JetBrains Mono', 'Fira Code', Menlo, Consolas, monospace" font-size="10.5" font-weight="700" letter-spacing="1.2">
      [ 🇻🇳 VN_DEV_HUD // JAX<tspan class="cursor-blink">_</tspan> ]
    </text>
  </g>

  <!-- 3D Pixel Art Typography JAX with Floating Bobbing Motion -->
  <g class="jax-group">
    {jax_pixel_blocks}
  </g>

  <!-- Role Tagline -->
  <text x="40" y="132" fill="#f0d5d7" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="13" font-weight="600" letter-spacing="0.4">
    <tspan fill="#ffdd00">SYSTEMS &amp; AUTOMATION</tspan>  <tspan fill="#7a1c24">·</tspan>  <tspan fill="#ffffff">MEDIA PIPELINES</tspan>  <tspan fill="#7a1c24">·</tspan>  <tspan fill="#ff6b6b">HARDWARE MODS</tspan>
  </text>

  <!-- Telemetry Row / Specs (Location 🇻🇳 VIETNAM) -->
  <text x="40" y="157" fill="#c49b9e" font-family="'JetBrains Mono', Menlo, Consolas, monospace" font-size="11" letter-spacing="0.6">
    <tspan fill="#ffdd00" font-weight="700">★ {stars:,} STARS</tspan>  <tspan fill="#7a1c24">│</tspan>  <tspan fill="#ffdd00" font-weight="700">📦 {repos} REPOS</tspan>  <tspan fill="#7a1c24">│</tspan>  <tspan fill="#ff6b6b">⚡ PYTHON / C# / ASM</tspan>  <tspan fill="#7a1c24">│</tspan>  <tspan fill="#ffd700">📍 🇻🇳 VIETNAM</tspan>
  </text>

  <!-- Celestial Orbit Rings around Golden Star -->
  <g>
    <circle cx="{star_cx}" cy="{star_cy}" r="74" fill="none" stroke="#ffdd00" stroke-width="1" stroke-dasharray="4 8" opacity="0.32" class="spin-ring"/>
    <circle cx="{star_cx}" cy="{star_cy}" r="62" fill="none" stroke="#da251d" stroke-width="1.2" opacity="0.45"/>
    <g stroke="#ffdd00" stroke-width="1.5" opacity="0.6">
      <line x1="{star_cx}" y1="{star_cy - 78}" x2="{star_cx}" y2="{star_cy - 70}"/>
      <line x1="{star_cx}" y1="{star_cy + 70}" x2="{star_cx}" y2="{star_cy + 78}"/>
      <line x1="{star_cx - 78}" y1="{star_cy}" x2="{star_cx - 70}" y2="{star_cy}"/>
      <line x1="{star_cx + 70}" y1="{star_cy}" x2="{star_cx + 78}" y2="{star_cy}"/>
    </g>
  </g>

  <!-- Floating Twinkling Pixel Stars in the Cosmic Sky -->
  <g fill="#ffdd00">
    <g class="twinkle-1" transform="translate(615, 38)">
      <polygon points="0,-4 1,-1 4,0 1,1 0,4 -1,1 -4,0 -1,-1" fill="#fff9d2"/>
    </g>
    <g class="twinkle-2" transform="translate(805, 42)">
      <polygon points="0,-5 1.2,-1.2 5,0 1.2,1.2 0,5 -1.2,1.2 -5,0 -1.2,-1.2" fill="#ffdd00"/>
    </g>
    <g class="twinkle-3" transform="translate(635, 142)">
      <polygon points="0,-3.5 1,-1 3.5,0 1,1 0,3.5 -1,1 -3.5,0 -1,-1" fill="#ffdd00"/>
    </g>
    <g class="twinkle-4" transform="translate(812, 138)">
      <polygon points="0,-4 1,-1 4,0 1,1 0,4 -1,1 -4,0 -1,-1" fill="#fff9d2"/>
    </g>
  </g>

  <!-- Majestic Faceted Golden Star (Vietnam Flag) with Breathing Animation -->
  <g class="star-pulse">
    {star_facets}
  </g>
</svg>'''
    with open("assets/banner.svg", "w", encoding="utf-8") as f:
        f.write(svg)

# ---------------------------------------------------------
# 2. Stats Cards SVG (4 Cards in Red & Imperial Gold Theme)
# ---------------------------------------------------------
def generate_stats_svg(stars, forks, downloads, repos):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="850" height="115" viewBox="0 0 850 115" fill="none">
  <defs>
    <!-- Card Gradient -->
    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#140305"/>
      <stop offset="50%" stop-color="#1d0508"/>
      <stop offset="100%" stop-color="#26070b"/>
    </linearGradient>

    <!-- Glowing Accent Beams -->
    <linearGradient id="goldBeam" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#da251d"/>
      <stop offset="50%" stop-color="#ffdd00"/>
      <stop offset="100%" stop-color="#da251d"/>
    </linearGradient>

    <linearGradient id="amberBeam" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#da251d"/>
      <stop offset="50%" stop-color="#ffaa00"/>
      <stop offset="100%" stop-color="#da251d"/>
    </linearGradient>

    <linearGradient id="greenBeam" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#da251d"/>
      <stop offset="50%" stop-color="#4ade80"/>
      <stop offset="100%" stop-color="#da251d"/>
    </linearGradient>

    <linearGradient id="redBeam" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ffdd00"/>
      <stop offset="50%" stop-color="#da251d"/>
      <stop offset="100%" stop-color="#ffdd00"/>
    </linearGradient>
  </defs>

  <style>
    .stat-card {{
      fill: url(#cardBg);
      stroke: #3d0e13;
      stroke-width: 1.5;
    }}
    .accent-beam {{
      animation: beamPulse 3s ease-in-out infinite;
    }}
    @keyframes beamPulse {{
      0%, 100% {{ opacity: 0.75; }}
      50% {{ opacity: 1; filter: drop-shadow(0 0 4px #ffdd00); }}
    }}
    .stat-num {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 26px;
      font-weight: 700;
      text-anchor: middle;
    }}
    .stat-lbl {{
      fill: #c49b9e;
      font-family: 'JetBrains Mono', Menlo, Consolas, monospace;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 1.2px;
      text-anchor: middle;
    }}
    .stat-tag {{
      fill: #80222b;
      font-family: 'JetBrains Mono', Menlo, monospace;
      font-size: 8.5px;
      font-weight: 600;
      letter-spacing: 0.8px;
    }}
    .bracket {{
      stroke: #ffdd00;
      stroke-width: 1.2;
      opacity: 0.65;
    }}
  </style>

  <!-- Card 1: TOTAL STARS -->
  <g transform="translate(1, 5)">
    <rect width="200" height="104" rx="10" class="stat-card"/>
    <rect width="200" height="3" rx="1.5" fill="url(#goldBeam)" class="accent-beam"/>
    <path d="M 6 14 L 6 8 L 12 8" class="bracket"/>
    <path d="M 194 14 L 194 8 L 188 8" class="bracket"/>
    <text x="14" y="24" class="stat-tag">// 01_STAR</text>
    <text x="101" y="44" fill="#ffdd00" font-size="16" font-family="sans-serif" text-anchor="middle">★</text>
    <text x="101" y="73" fill="#ffdd00" class="stat-num">{stars:,}</text>
    <text x="101" y="93" class="stat-lbl">TOTAL STARS</text>
  </g>

  <!-- Card 2: FORKS -->
  <g transform="translate(217, 5)">
    <rect width="200" height="104" rx="10" class="stat-card"/>
    <rect width="200" height="3" rx="1.5" fill="url(#amberBeam)" class="accent-beam"/>
    <path d="M 6 14 L 6 8 L 12 8" class="bracket"/>
    <path d="M 194 14 L 194 8 L 188 8" class="bracket"/>
    <text x="14" y="24" class="stat-tag">// 02_FORK</text>
    <text x="101" y="44" fill="#ffaa00" font-size="16" font-family="sans-serif" text-anchor="middle">⑂</text>
    <text x="101" y="73" fill="#ffaa00" class="stat-num">{forks:,}</text>
    <text x="101" y="93" class="stat-lbl">TOTAL FORKS</text>
  </g>

  <!-- Card 3: DOWNLOADS -->
  <g transform="translate(433, 5)">
    <rect width="200" height="104" rx="10" class="stat-card"/>
    <rect width="200" height="3" rx="1.5" fill="url(#greenBeam)" class="accent-beam"/>
    <path d="M 6 14 L 6 8 L 12 8" class="bracket"/>
    <path d="M 194 14 L 194 8 L 188 8" class="bracket"/>
    <text x="14" y="24" class="stat-tag">// 03_LOAD</text>
    <text x="101" y="44" fill="#4ade80" font-size="16" font-family="sans-serif" text-anchor="middle">↓</text>
    <text x="101" y="73" fill="#4ade80" class="stat-num">{downloads:,}</text>
    <text x="101" y="93" class="stat-lbl">RELEASES DL</text>
  </g>

  <!-- Card 4: PUBLIC REPOS -->
  <g transform="translate(649, 5)">
    <rect width="200" height="104" rx="10" class="stat-card"/>
    <rect width="200" height="3" rx="1.5" fill="url(#redBeam)" class="accent-beam"/>
    <path d="M 6 14 L 6 8 L 12 8" class="bracket"/>
    <path d="M 194 14 L 194 8 L 188 8" class="bracket"/>
    <text x="14" y="24" class="stat-tag">// 04_REPO</text>
    <text x="101" y="44" fill="#ff4d4d" font-size="16" font-family="sans-serif" text-anchor="middle">▣</text>
    <text x="101" y="73" fill="#ff4d4d" class="stat-num">{repos:,}</text>
    <text x="101" y="93" class="stat-lbl">PUBLIC REPOS</text>
  </g>
</svg>'''
    with open("assets/stats.svg", "w", encoding="utf-8") as f:
        f.write(svg)

# ---------------------------------------------------------
# 3. Featured Repo SVG (Cyberpunk Card with Laser & Capsules)
# ---------------------------------------------------------
def generate_featured_svg(info):
    raw_desc = info.get("desc") or ""
    # Cắt gọn theo ranh giới từ để tránh gãy chữ
    if len(raw_desc) > 75:
        desc_trimmed = raw_desc[:75].rsplit(' ', 1)[0] + '...'
    else:
        desc_trimmed = raw_desc
    desc = html.escape(desc_trimmed)
    name = html.escape(str(info.get("name", "")))
    stars = info.get("stars", 0)
    forks = info.get("forks", 0)
    downloads = info.get("downloads", 0)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="850" height="115" viewBox="0 0 850 115" fill="none">
  <defs>
    <linearGradient id="featBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#140305"/>
      <stop offset="50%" stop-color="#1f0508"/>
      <stop offset="100%" stop-color="#2a070c"/>
    </linearGradient>

    <linearGradient id="featLaser" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ffdd00"/>
      <stop offset="50%" stop-color="#da251d"/>
      <stop offset="100%" stop-color="#ffdd00"/>
    </linearGradient>
  </defs>

  <style>
    .feat-border {{
      stroke-dasharray: 100 1820;
      animation: featTravel 8s linear infinite;
    }}
    @keyframes featTravel {{
      from {{ stroke-dashoffset: 1920; }}
      to {{ stroke-dashoffset: 0; }}
    }}
    .stat-box {{
      fill: #190407;
      stroke: #420f14;
      stroke-width: 1;
    }}
    .corner-mark {{
      stroke: #ffdd00;
      stroke-width: 1.5;
      opacity: 0.7;
    }}
  </style>

  <!-- Card Background -->
  <rect width="848" height="113" x="1" y="1" rx="12" fill="url(#featBg)" stroke="#3d0e13" stroke-width="1.5"/>

  <!-- Tactical Corners -->
  <path d="M 8 16 L 8 8 L 16 8" class="corner-mark"/>
  <path d="M 840 16 L 840 8 L 832 8" class="corner-mark"/>
  <path d="M 8 98 L 8 106 L 16 106" class="corner-mark"/>
  <path d="M 840 98 L 840 106 L 832 106" class="corner-mark"/>

  <!-- Left Accent Dual Stripe: Flag Red + Imperial Gold -->
  <rect x="1" y="1" width="4" height="113" rx="2" fill="#da251d"/>
  <rect x="5" y="1" width="2.5" height="113" rx="1" fill="#ffdd00"/>

  <!-- Animated Laser Ray -->
  <rect width="848" height="113" x="1" y="1" rx="12" fill="none" stroke="url(#featLaser)" stroke-width="1.8" class="feat-border"/>

  <!-- Header Badge -->
  <g>
    <rect x="30" y="16" width="220" height="18" rx="3" fill="#200609" stroke="#7a1c24" stroke-width="1"/>
    <circle cx="40" cy="25" r="2.5" fill="#da251d"/>
    <text x="49" y="28.5" fill="#ffdd00" font-family="'JetBrains Mono', Menlo, Consolas, monospace" font-size="9.5" font-weight="700" letter-spacing="1.2">
      [ 🇻🇳 FEATURED_SYSTEM // CORE_BUILD ]
    </text>
  </g>

  <!-- Repo Title -->
  <text x="30" y="58" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="700">
    {name}
  </text>

  <!-- Description -->
  <text x="30" y="85" fill="#c49b9e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12.5" font-weight="400">
    {desc}
  </text>

  <!-- Right Side Stat Capsules -->
  <!-- Capsule 1: Stars -->
  <g transform="translate(595, 26)">
    <rect width="72" height="62" rx="8" class="stat-box"/>
    <rect width="72" height="2" rx="1" fill="#ffdd00"/>
    <text x="36" y="22" fill="#ffdd00" font-size="12" font-family="sans-serif" text-anchor="middle">★</text>
    <text x="36" y="42" fill="#ffdd00" font-family="-apple-system, sans-serif" font-size="17" font-weight="700" text-anchor="middle">{stars:,}</text>
    <text x="36" y="55" fill="#c49b9e" font-family="'JetBrains Mono', monospace" font-size="8.5" font-weight="600" text-anchor="middle">STARS</text>
  </g>

  <!-- Capsule 2: Forks -->
  <g transform="translate(675, 26)">
    <rect width="72" height="62" rx="8" class="stat-box"/>
    <rect width="72" height="2" rx="1" fill="#ffaa00"/>
    <text x="36" y="22" fill="#ffaa00" font-size="12" font-family="sans-serif" text-anchor="middle">⑂</text>
    <text x="36" y="42" fill="#ffaa00" font-family="-apple-system, sans-serif" font-size="17" font-weight="700" text-anchor="middle">{forks:,}</text>
    <text x="36" y="55" fill="#c49b9e" font-family="'JetBrains Mono', monospace" font-size="8.5" font-weight="600" text-anchor="middle">FORKS</text>
  </g>

  <!-- Capsule 3: Downloads -->
  <g transform="translate(755, 26)">
    <rect width="72" height="62" rx="8" class="stat-box"/>
    <rect width="72" height="2" rx="1" fill="#4ade80"/>
    <text x="36" y="22" fill="#4ade80" font-size="12" font-family="sans-serif" text-anchor="middle">↓</text>
    <text x="36" y="42" fill="#4ade80" font-family="-apple-system, sans-serif" font-size="17" font-weight="700" text-anchor="middle">{downloads:,}</text>
    <text x="36" y="55" fill="#c49b9e" font-family="'JetBrains Mono', monospace" font-size="8.5" font-weight="600" text-anchor="middle">RELEASES</text>
  </g>
</svg>'''
    with open("assets/featured.svg", "w", encoding="utf-8") as f:
        f.write(svg)

# ---------------------------------------------------------
# Entrypoint Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    print("Fetching GitHub metrics for user:", USERNAME)
    stars, forks, downloads, repos, featured = get_github_stats()
    print(f"Stats fetched: Stars={stars}, Forks={forks}, Downloads={downloads}, Repos={repos}")
    
    generate_banner_svg(stars, repos)
    generate_stats_svg(stars, forks, downloads, repos)
    generate_featured_svg(featured)
    print("Successfully generated all Vietnam Flag + Retro Cyberpunk SVG assets!")
