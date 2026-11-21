# content-site

Public homepage, privacy policy and terms of service for the studio's five channels and the private **Content Engine** app. Google's OAuth consent screen, TikTok's developer app review and Meta's app settings all ask for these three URLs.

The site is plain HTML with one CSS file. There is no build step, no tracking, no cookies, and no external fonts or scripts. It works from the repo root on GitHub Pages or any static host.

```
index.html        homepage: studio, five channel cards, "About the Content Engine app", contact
privacy.html      privacy policy (website + Content Engine app)
terms.html        terms of service
404.html          not-found page (uses absolute {{BASE_URL}} links, so it works at any depth)
robots.txt        allow all, points to the sitemap
sitemap.xml       3 URLs under {{BASE_URL}}
assets/style.css  the only stylesheet
assets/icons/     the five channel icons (256 px, from content-engine/assets/channels/*/icon-FINAL.png)
favicon.svg, favicon.ico, apple-touch-icon.png
fill.py           fills the placeholders
.nojekyll         tells GitHub Pages to serve files as-is
```

## 1. Fill the placeholders (one command)

| Token | Meaning |
|---|---|
| `{{STUDIO_NAME}}` | studio name (defaults to "Content Engine") |
| `{{CONTACT_EMAIL}}` | public contact email (shown on every page, used for privacy and deletion requests) |
| `{{BASE_URL}}` | site root, no trailing slash, e.g. `https://USER.github.io/content-site` |
| `{{HANDLE_scale}}` `{{HANDLE_survive}}` `{{HANDLE_torah}}` `{{HANDLE_lantern}}` `{{HANDLE_ranked}}` | YouTube handles without `@` (defaults: ScaleOfWhat, SurviveTheDays, TorahUnrolled, TheBronzeLantern, ClearlyRanked) |

```bash
python3 fill.py --studio "Content Engine" --email "you@yourdomain.com" \
  --base-url "https://USER.github.io/content-site" \
  --handles scale=ScaleOfWhat survive=SurviveTheDays torah=TorahUnrolled lantern=TheBronzeLantern ranked=ClearlyRanked
```

- The command edits the files in place and prints what it replaced. It exits with an error if any `{{…}}` token is left.
- To start over: `git checkout -- .`
- To preview without touching the originals, add `--out _preview/site`. `_preview/` is git-ignored.
- For a custom domain, add `--cname www.yourdomain.com` (this writes a `CNAME` file) and use `--base-url https://www.yourdomain.com`.

Before publishing, read `privacy.html` and confirm every statement is true of how Content Engine actually behaves. The draft is not legal advice.

## 2. Publish on GitHub Pages

Run these from this folder, after filling the placeholders. Replace `USER` with your GitHub username.

```bash
gh repo create content-site --public --source=. --remote=origin --push
gh api -X POST repos/USER/content-site/pages -f "source[branch]=main" -f "source[path]=/"
gh api repos/USER/content-site/pages --jq .html_url     # the live URL, about a minute after publishing
```

To do it in the browser instead, open the repo's **Settings → Pages**. Under **Build and deployment**, set **Source** to "Deploy from a branch", **Branch** to `main`, and **Folder** to `/ (root)`, then click **Save**. Once the site is live, tick **Enforce HTTPS**.

The repo must be **public** for Pages on a free GitHub plan.

The site URL is `https://USER.github.io/content-site`. That is the `--base-url` to use. If you name the repo `USER.github.io`, the URL is `https://USER.github.io` instead.

To serve the site from `/docs`, move every site file into `docs/` and use `-f "source[path]=/docs"`.

## 3. Custom domain (later)

1. Run `python3 fill.py ... --base-url https://www.yourdomain.com --cname www.yourdomain.com`. If the site was already filled, run `git checkout -- .` first. Then commit and push.
2. At your DNS provider:
   - For `www`: add a `CNAME` record pointing to `USER.github.io`.
   - For the bare domain: add `A` records to `185.199.108.153`, `185.199.109.153`, `185.199.110.153` and `185.199.111.153`.
3. In the repo's **Settings → Pages → Custom domain**, enter the domain, wait for the DNS check to pass, then tick **Enforce HTTPS**.
4. Update the URLs in Google, TikTok and Meta (below). On Google, add the new domain under **Authorized domains** and verify it in Search Console.

## 4. Which URLs to paste where

In this section, `BASE` is your `--base-url`, for example `https://USER.github.io/content-site`.

### Google Cloud Console → Google Auth Platform → Branding (OAuth consent screen)

| Field | Value |
|---|---|
| App name | `Content Engine` |
| User support email / Developer contact | your contact email |
| Application home page | `BASE/` |
| Application privacy policy link | `BASE/privacy.html` |
| Application terms of service link | `BASE/terms.html` |
| Authorized domains | the registrable domain of BASE: `USER.github.io` (or `yourdomain.com`) |

- The homepage and privacy policy must be on an authorized domain, and Google asks you to verify that domain in [Google Search Console](https://search.google.com/search-console). You can only verify a `github.io` domain if it's your own `USER.github.io` site, so a custom domain makes verification easier.
- The scopes you request on the **Data Access** page must match the scope table in `privacy.html`, section 3. Remove the rows you don't use.

### TikTok for Developers → your app → App details

| Field | Value |
|---|---|
| Web/Desktop URL (website) | `BASE/` |
| Terms of Service URL | `BASE/terms.html` |
| Privacy Policy URL | `BASE/privacy.html` |

Content Posting API → URL properties / domain verification (needed only if you pull videos from a URL): verify `BASE`'s domain or URL prefix.

### Meta for Developers → your app → App settings → Basic

| Field | Value |
|---|---|
| App domains | the domain of BASE |
| Privacy Policy URL | `BASE/privacy.html` |
| Terms of Service URL | `BASE/terms.html` |
| User data deletion → Data deletion instructions URL | `BASE/privacy.html#data-deletion` |
| Website (Add platform → Website) → Site URL | `BASE/` |

## Checks before publishing

- `grep -rn "{{" *.html robots.txt sitemap.xml` should print nothing after filling.
- Open `index.html`, `privacy.html` and `terms.html` in a browser at phone and desktop widths.
- Every YouTube link on the homepage should open the right channel.
