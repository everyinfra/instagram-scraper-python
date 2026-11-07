"""Instagram scraper in Python: scrape the posts of a public account, or single posts by URL.

  python main.py posts natgeo --limit 30 --out posts.csv
  python main.py post https://www.instagram.com/p/<shortcode>/ --out post.json
"""
import argparse

from everyinfra import call, report


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("posts", help="recent posts of a public account")
    s.add_argument("username", help="handle without @, or the profile URL")
    s.add_argument("--limit", type=int, default=30, help="1-200 posts")
    one = sub.add_parser("post", help="one or more posts by URL")
    one.add_argument("urls", nargs="+")
    for x in (s, one):
        x.add_argument("--out", help="write .csv or .json")
    a = p.parse_args()

    if a.cmd == "posts":
        # user_posts runs as an async job; call() polls it until it finishes
        data = call("instagram", "user_posts", {"username": a.username, "limit": a.limit})
    else:
        data = call("instagram", "post", {"urls": a.urls})
    report(data, a.out)


if __name__ == "__main__":
    main()
