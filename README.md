# Instagram Scraper Python

Scrape Instagram posts with Python. Give a public account such as natgeo and get its recent posts with caption, likes, comments, views, media URLs and hashtags, or fetch single posts by URL. No login, no browser and no proxy: the script sends one request to the EveryInfra API and waits for the result.

Also covers: scrape Instagram posts with Python, Instagram scraper API.

## Quick start

```bash
git clone https://github.com/everyinfra/instagram-scraper-python.git
cd instagram-scraper-python
pip install -r requirements.txt
export EVERYINFRA_API_KEY=your_key   # get one at everyinfra.com
python main.py posts natgeo --limit 30 --out posts.csv
python main.py post https://www.instagram.com/p/<shortcode>/ --out post.json
```

Get an API key: [everyinfra.com/en/docs](https://everyinfra.com/en/docs?utm_source=github&utm_medium=example_repo&utm_campaign=instagram-scraper-python#quickstart). Without `--out`, the script prints the first three rows as JSON.

## Price

| Call | Price per 1,000 calls | Rows per call |
|---|---|---|
| [`instagram/user_posts`](https://everyinfra.com/en/instagram-api/user_posts?utm_source=github&utm_medium=example_repo&utm_campaign=instagram-scraper-python) | $0.56 | 30 in our test |
| [`instagram/post`](https://everyinfra.com/en/instagram-api/post?utm_source=github&utm_medium=example_repo&utm_campaign=instagram-scraper-python) | $0.56 | 1 in our test |

- You pay per call, not per month. Failed calls and empty results are not charged.
- New accounts can claim $1 of trial credit: create an account, star [everyinfra-agent-plugins](https://github.com/everyinfra/everyinfra-agent-plugins) and [seo-skills](https://github.com/everyinfra/seo-skills), then claim it in the console. It is valid for 24 hours and needs no card. See [pricing](https://everyinfra.com/en/pricing?utm_source=github&utm_medium=example_repo&utm_campaign=instagram-scraper-python).

## What you get

### `user_posts`

| Field | Meaning |
|---|---|
| `post_id` | Post ID on the platform. |
| `url` | Link to the record on the platform. |
| `text` | Body text with HTML removed, returned in full and never cut short (on a few platforms the list results themselves carry only an excerpt; the platform's field notes say so). |
| `media_type` | Type of media, such as image or video. |
| `like_count` | Likes. null means the platform or this capability does not disclose it; it is not 0. |
| `comment_count` | Comments. null means not disclosed, not 0. |
| `view_count` | Views or plays. null means not disclosed, not 0. |
| `author_username` | Author's username (@handle), usually usable in URLs. |
| `author_name` | Author's display name. |
| `posted_at` | Publish time in ISO 8601, UTC (for example 2026-08-07T12:34:56+00:00). Non-standard strings from the platform are passed through as is, so parse defensively. null means the platform does not disclose it. |
| `location` | Location description passed through as is; the format varies by platform. |
| `id` | The record's unique ID on the platform. Unique only within one platform; IDs can repeat across platforms. |
| `image_url` | Image link. Capabilities with several images may return an image_urls array. |
| `video_url` | Video file link. |
| `author_id` | Author's unique ID on the platform. |
| `author_follower_count` | Author's follower count. null means not disclosed. |
| `hashtags` | Hashtags in the text, in order of appearance; absent when there are none. |

Also returned, named as on the platform: `width`, `height`, `is_comments_disabled`, `top_comments`.

Full parameter list: [Instagram user posts API](https://everyinfra.com/en/instagram-api/user_posts?utm_source=github&utm_medium=example_repo&utm_campaign=instagram-scraper-python).

### `post`

| Field | Meaning |
|---|---|
| `post_id` | Post ID on the platform. |
| `url` | Link to the record on the platform. |
| `text` | Body text with HTML removed, returned in full and never cut short (on a few platforms the list results themselves carry only an excerpt; the platform's field notes say so). |
| `media_type` | Type of media, such as image or video. |
| `like_count` | Likes. null means the platform or this capability does not disclose it; it is not 0. |
| `comment_count` | Comments. null means not disclosed, not 0. |
| `view_count` | Views or plays. null means not disclosed, not 0. |
| `author_username` | Author's username (@handle), usually usable in URLs. |
| `author_name` | Author's display name. |
| `posted_at` | Publish time in ISO 8601, UTC (for example 2026-08-07T12:34:56+00:00). Non-standard strings from the platform are passed through as is, so parse defensively. null means the platform does not disclose it. |
| `location` | Location description passed through as is; the format varies by platform. |
| `id` | The record's unique ID on the platform. Unique only within one platform; IDs can repeat across platforms. |
| `image_url` | Image link. Capabilities with several images may return an image_urls array. |
| `video_url` | Video file link. |
| `author_id` | Author's unique ID on the platform. |
| `author_follower_count` | Author's follower count. null means not disclosed. |
| `hashtags` | Hashtags in the text, in order of appearance; absent when there are none. |

Also returned, named as on the platform: `width`, `height`, `is_comments_disabled`, `top_comments`.

Full parameter list: [Instagram post API](https://everyinfra.com/en/instagram-api/post?utm_source=github&utm_medium=example_repo&utm_campaign=instagram-scraper-python).

## Tested

We ran both commands against the live API before publishing this repository (times in Singapore time, UTC+8).

| Command | Run at (SGT) | Rows | Charged |
|---|---|---|---|
| `posts natgeo --limit 30` | 2026-11-08 03:36 | 30 | $0.000556 |
| `post https://www.instagram.com/p/<shortcode>/` | 2026-11-08 03:37 | 1 | $0.000556 |

First row of the `user_posts` result (long text cut, author fields left out of this sample):

```json
{
  "post_id": "DfbPDC4krJI",
  "url": "https://www.instagram.com/p/DfbPDC4krJI/",
  "text": "Presented by National Geographic Society in partnership with @Rolex. \n\nOur oceans cover more than 70% of ou...",
  "media_type": "video",
  "like_count": 15811,
  "comment_count": 33,
  "posted_at": "2026-11-07T17:00:03+00:00",
  "id": "4024876871938388552_18091046",
  "width": 1080,
  "height": 1920
}
```

## How it works

Every call is one request. `everyinfra.py` wraps it in about 60 lines of `requests`:

```bash
curl -X POST https://api.everyinfra.com/api/v1/social \
  -H "Authorization: Bearer $EVERYINFRA_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"platform": "instagram", "action": "user_posts", "params": {"username": "natgeo"}}'
```

- Slow actions (Instagram `user_posts`, for example) answer with a `job_id`. The script polls `GET /api/v1/jobs/{job_id}` every 5 seconds; polling is free.
- Errors come back as JSON with a code, a message and whether you were charged. A missing parameter returns 422 before any charge.
- The same key also works over MCP for Claude, Cursor and other AI agents: [docs](https://everyinfra.com/en/docs?utm_source=github&utm_medium=example_repo&utm_campaign=instagram-scraper-python).

## More

- [Instagram API on EveryInfra](https://everyinfra.com/en/instagram-api?utm_source=github&utm_medium=example_repo&utm_campaign=instagram-scraper-python): every Instagram action, with prices and live health
- Other examples: [google-maps-scraper](https://github.com/everyinfra/google-maps-scraper) · [tiktok-trends-api](https://github.com/everyinfra/tiktok-trends-api) · [tiktok-scraper-python](https://github.com/everyinfra/tiktok-scraper-python) · [douyin-api-python](https://github.com/everyinfra/douyin-api-python)

## License

MIT
