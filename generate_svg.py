import html
import json
import math
import os
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CACHE_PATH = os.path.join(BASE_DIR, ".metrics_cache.json")

USERNAME = os.getenv("GITHUB_REPOSITORY_OWNER", "j7x69")
TOKEN = os.getenv("GITHUB_TOKEN", "")

TOKENS = {
    "bg_canvas": "#09090B",
    "bg_card": "#0D0D10",
    "bg_elevated": "#141419",
    "bg_pill": "#16161C",
    "border": "#27272A",
    "border_subtle": "#1C1C21",
    "text_primary": "#FAFAFA",
    "text_secondary": "#A1A1AA",
    "text_muted": "#71717A",
    "accent_red": "#DC2626",
    "accent_crimson": "#E11D48",
    "accent_gold": "#F59E0B",
    "accent_amber": "#FBBF24",
    "accent_emerald": "#10B981",
    "font_sans": "'SF Pro Display', 'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
    "font_mono": "'JetBrains Mono', 'Geist Mono', 'SF Mono', Menlo, Consolas, monospace",
}

DEFAULT_METRICS = {
    "total_stars": 4,
    "total_downloads": 7,
    "public_repos": 4,
    "preserves_pitch": {
        "stars": 1,
        "downloads": 0,
        "version": "MV3",
    },
    "recompress_bypass": {
        "stars": 3,
        "downloads": 7,
        "version": "v1.2.5",
    },
}


def fetch_api(url):
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", f"GitHub-Profile-Bento-{USERNAME}")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"[warn] API fetch skipped ({url}): {exc}")
        return None


def normalize_version(raw_tag, fallback="v1.2.5"):
    if not raw_tag or not isinstance(raw_tag, str):
        return fallback
    tag = raw_tag.strip()
    if not tag:
        return fallback
    if tag[0].isdigit():
        return f"v{tag}"
    return tag


def sum_release_downloads(releases):
    if not isinstance(releases, list):
        return 0
    total = 0
    for rel in releases:
        if not isinstance(rel, dict) or rel.get("draft"):
            continue
        for asset in rel.get("assets", []):
            total += int(asset.get("download_count", 0))
    return total


def resolve_repo_version(owner, repo_name, releases=None, fallback="v1.2.5"):
    latest = fetch_api(f"https://api.github.com/repos/{owner}/{repo_name}/releases/latest")
    if isinstance(latest, dict) and latest.get("tag_name"):
        return normalize_version(latest["tag_name"], fallback)

    if isinstance(releases, list):
        for rel in releases:
            if isinstance(rel, dict) and not rel.get("draft") and rel.get("tag_name"):
                return normalize_version(rel["tag_name"], fallback)

    tags = fetch_api(f"https://api.github.com/repos/{owner}/{repo_name}/tags?per_page=10")
    if isinstance(tags, list) and tags:
        first_tag = tags[0].get("name") if isinstance(tags[0], dict) else None
        if first_tag:
            return normalize_version(first_tag, fallback)

    return fallback


def load_cached_metrics():
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as handle:
                cached = json.load(handle)
                if isinstance(cached, dict) and "recompress_bypass" in cached:
                    return cached
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_METRICS))


def save_cached_metrics(metrics):
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as handle:
            json.dump(metrics, handle, indent=2)
    except Exception as exc:
        print(f"[warn] Could not write metrics cache: {exc}")


def fetch_profile_metrics():
    baseline = load_cached_metrics()
    repos = fetch_api(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner")
    if not isinstance(repos, list):
        print("[info] Using cached/baseline metrics (offline or API unavailable).")
        return baseline

    total_stars = 0
    total_downloads = 0
    public_repos = 0
    preserves_info = dict(baseline["preserves_pitch"])
    recompress_info = dict(baseline["recompress_bypass"])
    found_recompress = False

    for repo in repos:
        if not isinstance(repo, dict) or repo.get("fork"):
            continue
        public_repos += 1
        repo_name = repo.get("name", "")
        stars = int(repo.get("stargazers_count", 0))
        total_stars += stars

        releases = fetch_api(f"https://api.github.com/repos/{USERNAME}/{repo_name}/releases?per_page=100")
        repo_dl = sum_release_downloads(releases)
        total_downloads += repo_dl

        lower_name = repo_name.lower()
        if lower_name == "preservespitchyt":
            preserves_info["stars"] = stars
            preserves_info["downloads"] = repo_dl
        elif lower_name in ("recompress-bypass", "recompressbypass"):
            found_recompress = True
            recompress_info["stars"] = stars
            recompress_info["downloads"] = repo_dl
            recompress_info["version"] = resolve_repo_version(
                USERNAME,
                repo_name,
                releases=releases,
                fallback=recompress_info.get("version", "v1.2.5"),
            )

    if not found_recompress:
        direct_repo = fetch_api(f"https://api.github.com/repos/{USERNAME}/Recompress-Bypass")
        if isinstance(direct_repo, dict) and "stargazers_count" in direct_repo:
            releases = fetch_api(f"https://api.github.com/repos/{USERNAME}/Recompress-Bypass/releases?per_page=100")
            recompress_info["stars"] = int(direct_repo.get("stargazers_count", 0))
            recompress_info["downloads"] = sum_release_downloads(releases)
            recompress_info["version"] = resolve_repo_version(
                USERNAME,
                "Recompress-Bypass",
                releases=releases,
                fallback=recompress_info.get("version", "v1.2.5"),
            )

    metrics = {
        "total_stars": total_stars,
        "total_downloads": total_downloads,
        "public_repos": public_repos,
        "preserves_pitch": preserves_info,
        "recompress_bypass": recompress_info,
    }
    save_cached_metrics(metrics)
    return metrics


def build_star_points(cx, cy, r_out, r_in=None):
    if r_in is None:
        r_in = r_out * 0.381966
    pts = []
    angle = -math.pi / 2
    step = math.pi / 5
    for idx in range(10):
        radius = r_out if idx % 2 == 0 else r_in
        pts.append(f"{cx + radius * math.cos(angle):.2f},{cy + radius * math.sin(angle):.2f}")
        angle += step
    return " ".join(pts)


def write_svg(filename, content):
    os.makedirs(ASSETS_DIR, exist_ok=True)
    target = os.path.join(ASSETS_DIR, filename)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content.strip() + "\n")


def generate_banner_svg(metrics):
    t = TOKENS
    vn_star = build_star_points(740.0, 18.5, 3.3)
    total_dl = f"{metrics['total_downloads']:,}"
    total_stars = f"{metrics['total_stars']:,}"
    public_repos = f"{metrics['public_repos']:,}"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="850" height="186" viewBox="0 0 850 186" fill="none">
  <defs>
    <pattern id="dotMatrix" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="0.75" fill="{t['border']}" fill-opacity="0.45"/>
    </pattern>
    <radialGradient id="subtleWarmth" cx="760" cy="30" r="280" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{t['accent_crimson']}" stop-opacity="0.06"/>
      <stop offset="55%" stop-color="{t['accent_gold']}" stop-opacity="0.025"/>
      <stop offset="100%" stop-color="{t['bg_canvas']}" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="bannerClip">
      <rect x="0.5" y="0.5" width="849" height="185" rx="12"/>
    </clipPath>
  </defs>

  <style>
    .cursor-blink {{
      animation: blink 1.1s step-end infinite;
    }}
    @keyframes blink {{
      0%, 50% {{ opacity: 1; }}
      51%, 100% {{ opacity: 0; }}
    }}
    .status-pulse {{
      animation: pulse 3s ease-in-out infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 0.35; }}
      50% {{ opacity: 0.85; }}
    }}
  </style>

  <g clip-path="url(#bannerClip)">
    <rect x="0.5" y="0.5" width="849" height="185" rx="12" fill="{t['bg_canvas']}"/>
    <rect x="37" y="37" width="519" height="148" fill="url(#dotMatrix)" opacity="0.65"/>
    <rect x="0.5" y="0.5" width="849" height="185" fill="url(#subtleWarmth)"/>

    <!-- Top Terminal Bar -->
    <rect x="0.5" y="0.5" width="849" height="36" fill="{t['bg_card']}"/>
    <line x1="0.5" y1="36.5" x2="849.5" y2="36.5" stroke="{t['border_subtle']}" stroke-width="1"/>

    <!-- Minimal Window Controls -->
    <circle cx="22" cy="18.5" r="4" fill="{t['accent_red']}" opacity="0.85"/>
    <circle cx="36" cy="18.5" r="4" fill="{t['border']}"/>
    <circle cx="50" cy="18.5" r="4" fill="{t['border']}"/>

    <!-- Terminal Path -->
    <text x="68" y="22.5" font-family="{t['font_mono']}" font-size="11.5">
      <tspan fill="{t['text_primary']}" font-weight="600">~/j7x69</tspan>
      <tspan fill="{t['text_muted']}"> — systems &amp; media engineering</tspan><tspan fill="{t['accent_gold']}" font-weight="700" class="cursor-blink">_</tspan>
    </text>

    <!-- Geometric Vietnam + Timezone Pill -->
    <rect x="724" y="8.5" width="108" height="20" rx="10" fill="{t['bg_elevated']}" stroke="{t['border']}" stroke-width="1"/>
    <rect x="733" y="13.5" width="14" height="10" rx="1.8" fill="{t['accent_red']}"/>
    <polygon points="{vn_star}" fill="{t['accent_amber']}"/>
    <text x="754" y="22" fill="{t['text_secondary']}" font-family="{t['font_mono']}" font-size="10" font-weight="600" letter-spacing="0.4">VN · UTC+7</text>

    <!-- Bento Structural Dividers -->
    <line x1="556.5" y1="36.5" x2="556.5" y2="185.5" stroke="{t['border_subtle']}" stroke-width="1"/>
    <line x1="556.5" y1="94.5" x2="849.5" y2="94.5" stroke="{t['border_subtle']}" stroke-width="1"/>
    <line x1="654.5" y1="94.5" x2="654.5" y2="185.5" stroke="{t['border_subtle']}" stroke-width="1"/>
    <line x1="752.5" y1="94.5" x2="752.5" y2="185.5" stroke="{t['border_subtle']}" stroke-width="1"/>

    <!-- Left Hero Column -->
    <text x="28" y="63" fill="{t['text_muted']}" font-family="{t['font_mono']}" font-size="10" font-weight="600" letter-spacing="1.2">SOFTWARE ENGINEER  //  CLIENT &amp; MEDIA SYSTEMS</text>

    <text x="28" y="102" fill="{t['text_primary']}" font-family="{t['font_sans']}" font-size="34" font-weight="700" letter-spacing="-0.8">Jax</text>
    <text x="92" y="100" fill="{t['text_muted']}" font-family="{t['font_mono']}" font-size="13.5" font-weight="500">@j7x69</text>

    <text x="28" y="132" fill="{t['text_secondary']}" font-family="{t['font_sans']}" font-size="13.5" font-weight="400">Building zero-bloat media tooling, binary container pipelines,</text>
    <text x="28" y="153" fill="{t['text_secondary']}" font-family="{t['font_sans']}" font-size="13.5" font-weight="400">browser runtime extensions, and native client utilities.</text>

    <!-- Right Bento Top: Active Shipping Status -->
    <circle cx="579" cy="60" r="6.5" fill="{t['accent_emerald']}" class="status-pulse"/>
    <circle cx="579" cy="60" r="3" fill="{t['accent_emerald']}"/>
    <text x="593" y="63.5" fill="{t['text_primary']}" font-family="{t['font_mono']}" font-size="10.5" font-weight="600" letter-spacing="0.7">ACTIVE DISTRIBUTION</text>
    <text x="593" y="80" fill="{t['text_muted']}" font-family="{t['font_mono']}" font-size="10.5">Chrome Web Store · Android APK</text>

    <!-- Right Bento Bottom: 3 Clean Telemetry Cells -->
    <text x="605.5" y="138" fill="{t['text_primary']}" font-family="{t['font_mono']}" font-size="20" font-weight="700" text-anchor="middle">{total_dl}</text>
    <text x="605.5" y="160" fill="{t['text_muted']}" font-family="{t['font_mono']}" font-size="9.5" font-weight="600" letter-spacing="0.8" text-anchor="middle">DOWNLOADS</text>

    <text x="703.5" y="138" fill="{t['accent_amber']}" font-family="{t['font_mono']}" font-size="20" font-weight="700" text-anchor="middle">{total_stars}</text>
    <text x="703.5" y="160" fill="{t['text_muted']}" font-family="{t['font_mono']}" font-size="9.5" font-weight="600" letter-spacing="0.8" text-anchor="middle">STARS</text>

    <text x="801" y="138" fill="{t['text_primary']}" font-family="{t['font_mono']}" font-size="20" font-weight="700" text-anchor="middle">{public_repos}</text>
    <text x="801" y="160" fill="{t['text_muted']}" font-family="{t['font_mono']}" font-size="9.5" font-weight="600" letter-spacing="0.8" text-anchor="middle">REPOS</text>
  </g>

  <rect x="0.5" y="0.5" width="849" height="185" rx="12" stroke="{t['border']}" stroke-width="1"/>
</svg>"""
    write_svg("banner.svg", svg)


def generate_preservespitch_card(info):
    t = TOKENS
    stars_str = f"{int(info.get('stars', 0)):,}"
    star_poly = build_star_points(312.0, 154.5, 5.2)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="418" height="176" viewBox="0 0 418 176" fill="none">
  <rect x="0.5" y="0.5" width="417" height="175" rx="10" fill="{t['bg_card']}" stroke="{t['border']}" stroke-width="1"/>

  <!-- Custom Audio Pitch Waveform Icon Box -->
  <rect x="20" y="18" width="32" height="32" rx="7" fill="{t['bg_elevated']}" stroke="{t['border']}" stroke-width="1"/>
  <g stroke="{t['accent_amber']}" stroke-width="1.7" stroke-linecap="round">
    <line x1="28" y1="37" x2="28" y2="31"/>
    <line x1="32" y1="40" x2="32" y2="28"/>
    <line x1="36" y1="42" x2="36" y2="26"/>
    <line x1="40" y1="38" x2="40" y2="30"/>
    <line x1="44" y1="36" x2="44" y2="32"/>
  </g>

  <!-- Status Pill -->
  <rect x="252" y="23" width="146" height="22" rx="11" fill="#0D1F17" stroke="#183D2C" stroke-width="1"/>
  <circle cx="265" cy="34" r="3" fill="{t['accent_emerald']}"/>
  <text x="274" y="37.5" fill="#34D399" font-family="{t['font_mono']}" font-size="9.5" font-weight="600" letter-spacing="0.4">CHROME STORE · LIVE</text>

  <!-- Title & External Arrow -->
  <text x="20" y="76" fill="{t['text_primary']}" font-family="{t['font_sans']}" font-size="18" font-weight="700" letter-spacing="-0.3">PreservesPitchYT</text>
  <path d="M 388 72 L 396 64 M 390 64 L 396 64 L 396 70" stroke="{t['text_muted']}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- Technical Summary -->
  <text x="20" y="100" fill="{t['text_secondary']}" font-family="{t['font_sans']}" font-size="12.5">Manifest V3 extension unlocking proportional analog pitch</text>
  <text x="20" y="119" fill="{t['text_secondary']}" font-family="{t['font_sans']}" font-size="12.5">shifting (preservesPitch = false) on YouTube HTML5 video.</text>

  <!-- Bottom Metadata Bar -->
  <line x1="1" y1="138.5" x2="417" y2="138.5" stroke="{t['border_subtle']}" stroke-width="1"/>
  <circle cx="25" cy="155" r="4" fill="#F7DF1E"/>
  <text x="35" y="159" fill="{t['text_secondary']}" font-family="{t['font_mono']}" font-size="10.5" font-weight="500">JavaScript · Manifest V3</text>

  <!-- Right Stats -->
  <polygon points="{star_poly}" fill="{t['accent_amber']}"/>
  <text x="321" y="159" fill="{t['text_primary']}" font-family="{t['font_mono']}" font-size="11" font-weight="600">{stars_str}</text>
  <line x1="335" y1="149.5" x2="335" y2="160.5" stroke="{t['border']}" stroke-width="1"/>
  <text x="398" y="159" fill="{t['text_muted']}" font-family="{t['font_mono']}" font-size="10.5" text-anchor="end">Web Store</text>
</svg>"""
    write_svg("project_preservespitch.svg", svg)


def generate_recompress_card(info):
    t = TOKENS
    version = html.escape(normalize_version(info.get("version"), "v1.2.5"))
    stars_str = f"{int(info.get('stars', 0)):,}"
    dl_str = f"{int(info.get('downloads', 0)):,}"

    pill_label = f"ANDROID · {version}"
    pill_width = max(118, int(len(pill_label) * 6.45 + 26))
    pill_x = 398 - pill_width

    # Right-aligned bottom telemetry coordinates (Stars | Cumulative Downloads)
    dl_text_label = f"{dl_str} DL"
    dl_text_x = 398
    dl_icon_x = dl_text_x - (len(dl_text_label) * 6.65) - 14
    sep_x = dl_icon_x - 9
    star_text_x = sep_x - 9
    star_icon_cx = star_text_x - (len(stars_str) * 6.65) - 8
    star_poly = build_star_points(star_icon_cx, 154.5, 5.2)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="418" height="176" viewBox="0 0 418 176" fill="none">
  <rect x="0.5" y="0.5" width="417" height="175" rx="10" fill="{t['bg_card']}" stroke="{t['border']}" stroke-width="1"/>

  <!-- Custom Binary Container Muxing Icon Box -->
  <rect x="20" y="18" width="32" height="32" rx="7" fill="{t['bg_elevated']}" stroke="{t['border']}" stroke-width="1"/>
  <rect x="27" y="25" width="18" height="18" rx="3" stroke="{t['accent_crimson']}" stroke-width="1.6"/>
  <path d="M 33 31 L 39 34 L 33 37 Z" fill="{t['text_primary']}"/>

  <!-- Dynamic Version Badge (Release / Git Tag) -->
  <rect x="{pill_x}" y="23" width="{pill_width}" height="22" rx="11" fill="#21160A" stroke="#422B11" stroke-width="1"/>
  <circle cx="{pill_x + 12}" cy="34" r="3" fill="{t['accent_amber']}"/>
  <text x="{pill_x + 21}" y="37.5" fill="{t['accent_amber']}" font-family="{t['font_mono']}" font-size="9.5" font-weight="600" letter-spacing="0.4">{pill_label}</text>

  <!-- Title & External Arrow -->
  <text x="20" y="76" fill="{t['text_primary']}" font-family="{t['font_sans']}" font-size="18" font-weight="700" letter-spacing="-0.3">Recompress-Bypass</text>
  <path d="M 388 72 L 396 64 M 390 64 L 396 64 L 396 70" stroke="{t['text_muted']}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- Technical Summary -->
  <text x="20" y="100" fill="{t['text_secondary']}" font-family="{t['font_sans']}" font-size="12.5">Native Android container conditioner remuxing MP4 streams</text>
  <text x="20" y="119" fill="{t['text_secondary']}" font-family="{t['font_sans']}" font-size="12.5">at the binary layer to preserve 2K/4K 60FPS visual fidelity.</text>

  <!-- Bottom Metadata Bar: Language + Live Stars + Cumulative Release Downloads -->
  <line x1="1" y1="138.5" x2="417" y2="138.5" stroke="{t['border_subtle']}" stroke-width="1"/>
  <circle cx="25" cy="155" r="4" fill="#A97BFF"/>
  <text x="35" y="159" fill="{t['text_secondary']}" font-family="{t['font_mono']}" font-size="10.5" font-weight="500">Kotlin · Compose</text>

  <!-- Stars -->
  <polygon points="{star_poly}" fill="{t['accent_amber']}"/>
  <text x="{star_text_x:.1f}" y="159" fill="{t['text_primary']}" font-family="{t['font_mono']}" font-size="11" font-weight="600" text-anchor="end">{stars_str}</text>
  <line x1="{sep_x:.1f}" y1="149.5" x2="{sep_x:.1f}" y2="160.5" stroke="{t['border']}" stroke-width="1"/>

  <!-- Cumulative Downloads -->
  <g transform="translate({dl_icon_x:.1f}, 149)" stroke="{t['accent_emerald']}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
    <path d="M 5 1.5 L 5 8.5 M 2.2 6 L 5 8.8 L 7.8 6"/>
    <line x1="1.5" y1="11" x2="8.5" y2="11"/>
  </g>
  <text x="{dl_text_x}" y="159" fill="{t['text_primary']}" font-family="{t['font_mono']}" font-size="11" font-weight="600" text-anchor="end">{dl_text_label}</text>
</svg>"""
    write_svg("project_recompress.svg", svg)


def generate_stack_svg():
    t = TOKENS
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="850" height="96" viewBox="0 0 850 96" fill="none">
  <rect x="0.5" y="0.5" width="849" height="95" rx="10" fill="{t['bg_canvas']}" stroke="{t['border']}" stroke-width="1"/>

  <line x1="283.5" y1="1" x2="283.5" y2="95" stroke="{t['border_subtle']}" stroke-width="1"/>
  <line x1="566.5" y1="1" x2="566.5" y2="95" stroke="{t['border_subtle']}" stroke-width="1"/>

  <!-- Domain 01 -->
  <text x="22" y="27" fill="{t['text_muted']}" font-family="{t['font_mono']}" font-size="9.5" font-weight="600" letter-spacing="1">01 // LANGUAGES</text>
  <text x="22" y="53" fill="{t['text_primary']}" font-family="{t['font_sans']}" font-size="13.5" font-weight="600">Rust · Kotlin · C++ · C#</text>
  <text x="22" y="74" fill="{t['text_secondary']}" font-family="{t['font_mono']}" font-size="11">JavaScript · Python · PowerShell</text>

  <!-- Domain 02 -->
  <text x="305" y="27" fill="{t['text_muted']}" font-family="{t['font_mono']}" font-size="9.5" font-weight="600" letter-spacing="1">02 // MEDIA &amp; RUNTIME</text>
  <text x="305" y="53" fill="{t['text_primary']}" font-family="{t['font_sans']}" font-size="13.5" font-weight="600">MP4 Binary Muxing · FFmpeg</text>
  <text x="305" y="74" fill="{t['text_secondary']}" font-family="{t['font_mono']}" font-size="11">HTML5 Web Audio · Manifest V3</text>

  <!-- Domain 03 -->
  <text x="588" y="27" fill="{t['text_muted']}" font-family="{t['font_mono']}" font-size="9.5" font-weight="600" letter-spacing="1">03 // PLATFORMS &amp; INFRA</text>
  <text x="588" y="53" fill="{t['text_primary']}" font-family="{t['font_sans']}" font-size="13.5" font-weight="600">Android (Jetpack Compose)</text>
  <text x="588" y="74" fill="{t['text_secondary']}" font-family="{t['font_mono']}" font-size="11">Win32 Native · Linux · GitHub CI</text>
</svg>"""
    write_svg("stack.svg", svg)


def generate_action_badges(recompress_version):
    t = TOKENS
    ver = html.escape(normalize_version(recompress_version, "v1.2.5"))

    def calc_pill_width(prefix, strong=""):
        return int(28 + (len(prefix) + len(strong)) * 6.45 + 14)

    # 1. Chrome Web Store Badge
    s_prefix, s_strong = "Chrome Store · ", "PreservesPitchYT"
    s_width = calc_pill_width(s_prefix, s_strong)
    store_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{s_width}" height="30" viewBox="0 0 {s_width} 30" fill="none">
  <rect x="0.5" y="0.5" width="{s_width - 1}" height="29" rx="6" fill="{t['bg_card']}" stroke="{t['border']}" stroke-width="1"/>
  <circle cx="16" cy="15" r="5" stroke="{t['accent_emerald']}" stroke-width="1.5"/>
  <circle cx="16" cy="15" r="1.8" fill="{t['accent_emerald']}"/>
  <text x="28" y="19" fill="{t['text_secondary']}" font-family="{t['font_mono']}" font-size="10.5" font-weight="500">{s_prefix}<tspan fill="{t['text_primary']}" font-weight="600">{s_strong}</tspan></text>
</svg>"""
    write_svg("badge_store.svg", store_svg)

    # 2. Recompress-Bypass APK Release Badge (with dynamic tag version)
    apk_label_prefix = "Android APK · "
    apk_label_strong = f"Recompress {ver}"
    apk_width = calc_pill_width(apk_label_prefix, apk_label_strong)
    apk_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{apk_width}" height="30" viewBox="0 0 {apk_width} 30" fill="none">
  <rect x="0.5" y="0.5" width="{apk_width - 1}" height="29" rx="6" fill="{t['bg_card']}" stroke="{t['border']}" stroke-width="1"/>
  <g transform="translate(11, 9)" stroke="{t['accent_amber']}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M 5 1 L 5 8 M 2.3 5.5 L 5 8.3 L 7.7 5.5"/>
    <line x1="1.5" y1="11" x2="8.5" y2="11"/>
  </g>
  <text x="28" y="19" fill="{t['text_secondary']}" font-family="{t['font_mono']}" font-size="10.5" font-weight="500">{apk_label_prefix}<tspan fill="{t['text_primary']}" font-weight="600">{apk_label_strong}</tspan></text>
</svg>"""
    write_svg("badge_apk.svg", apk_svg)

    # 3. Discord Server Badge
    d_prefix, d_strong = "Discord · ", "Join Server"
    d_width = calc_pill_width(d_prefix, d_strong)
    discord_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{d_width}" height="30" viewBox="0 0 {d_width} 30" fill="none">
  <rect x="0.5" y="0.5" width="{d_width - 1}" height="29" rx="6" fill="{t['bg_card']}" stroke="{t['border']}" stroke-width="1"/>
  <path d="M 12.2 11.2 C 13.5 10.6 14.8 10.4 16 10.4 C 17.2 10.4 18.5 10.6 19.8 11.2 C 20.8 13.3 21.1 15.6 20.8 17.9 C 19.7 18.8 18.5 19.3 17.3 19.6 L 16.7 18.5 C 16.2 18.6 15.8 18.6 15.3 18.5 L 14.7 19.6 C 13.5 19.3 12.3 18.8 11.2 17.9 C 10.9 15.6 11.2 13.3 12.2 11.2 Z" stroke="#818CF8" stroke-width="1.35" stroke-linejoin="round"/>
  <circle cx="14.4" cy="14.8" r="1" fill="#818CF8"/>
  <circle cx="17.6" cy="14.8" r="1" fill="#818CF8"/>
  <text x="28" y="19" fill="{t['text_secondary']}" font-family="{t['font_mono']}" font-size="10.5" font-weight="500">{d_prefix}<tspan fill="{t['text_primary']}" font-weight="600">{d_strong}</tspan></text>
</svg>"""
    write_svg("badge_discord.svg", discord_svg)


def ensure_snake_placeholder():
    snake_path = os.path.join(ASSETS_DIR, "snake.svg")
    if os.path.exists(snake_path):
        with open(snake_path, "r", encoding="utf-8") as handle:
            existing = handle.read()
        # Preserve real Platane/snk output if already generated by GitHub Actions
        if "Contribution animation generating" not in existing and len(existing) > 1500:
            return

    t = TOKENS
    cells = []
    palette = ["#131317", "#18181E", "#3F131D", "#881337", "#E11D48", "#F59E0B"]
    for col in range(52):
        for row in range(7):
            seed = (col * 17 + row * 31) % 29
            if seed == 0:
                fill = palette[5]
            elif seed < 3:
                fill = palette[4]
            elif seed < 6:
                fill = palette[3]
            elif seed < 10:
                fill = palette[2]
            elif seed < 16:
                fill = palette[1]
            else:
                fill = palette[0]
            x = 23 + col * 15.5
            y = 32 + row * 13.5
            cells.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="10.5" height="10.5" rx="2" fill="{fill}"/>')

    grid_markup = "\n    ".join(cells)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="850" height="142" viewBox="0 0 850 142" fill="none">
  <rect x="0.5" y="0.5" width="849" height="141" rx="10" fill="{t['bg_canvas']}" stroke="{t['border']}" stroke-width="1"/>
  <text x="23" y="21" fill="{t['text_muted']}" font-family="{t['font_mono']}" font-size="9.5" font-weight="600" letter-spacing="1">04 // CONTRIBUTION ACTIVITY</text>
  <text x="827" y="21" fill="{t['text_muted']}" font-family="{t['font_mono']}" font-size="9.5" text-anchor="end">SYNCED VIA GITHUB ACTIONS</text>
  <g>
    {grid_markup}
  </g>
</svg>"""
    write_svg("snake.svg", svg)


def build_all(metrics=None):
    active_metrics = metrics if metrics is not None else fetch_profile_metrics()
    generate_banner_svg(active_metrics)
    generate_preservespitch_card(active_metrics["preserves_pitch"])
    generate_recompress_card(active_metrics["recompress_bypass"])
    generate_stack_svg()
    generate_action_badges(active_metrics["recompress_bypass"].get("version", "v1.2.5"))
    ensure_snake_placeholder()
    return active_metrics


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    resolved = build_all()
    print(
        "Generated Minimalist Bento SVGs -> "
        f"Stars={resolved['total_stars']}, "
        f"Downloads={resolved['total_downloads']}, "
        f"Repos={resolved['public_repos']}, "
        f"Recompress={resolved['recompress_bypass']}"
    )
