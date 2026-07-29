import re
import urllib.request

html = urllib.request.urlopen(
    urllib.request.Request(
        "https://byshumail.my.canva.site/",
        headers={"User-Agent": "Mozilla/5.0"},
    ),
    timeout=40,
).read().decode("utf-8", "replace")
print("len", len(html))

urls = set(
    re.findall(
        r"https?://[^\"\\'\s<>]+(?:mp4|webm|m3u8)[^\"\\'\s<>]*",
        html,
        re.I,
    )
)
print("video urls", len(urls))
for u in list(urls)[:30]:
    print(u[:250])

for pat in [
    "video/mp4",
    "application/vnd.apple.mpegurl",
    "playback",
    "transcode",
    ".mp4",
    "CFStream",
    "videoUri",
    "video_url",
]:
    print(pat, html.count(pat))

# any media CDN
cdn = set(
    re.findall(
        r"https?://media[^\"\\'\s<>]{10,180}",
        html,
        re.I,
    )
)
print("media cdn", len(cdn))
for u in list(cdn)[:20]:
    print(u[:220])
