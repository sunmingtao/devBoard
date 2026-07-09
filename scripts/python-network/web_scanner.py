import argparse
import asyncio
import httpx
from urllib.parse import urljoin


DEFAULT_PATHS = [
    # Common
    "robots.txt",
    "sitemap.xml",
    "admin",
    "login",
    "api",
    "health",
    "metrics",

    # Swagger / OpenAPI
    "swagger-ui",
    "swagger-ui/index.html",
    "swagger",
    "v3/api-docs",
    "api-docs",
    "openapi.json",

    # Spring Boot
    "actuator",
    "actuator/health",
    "actuator/env",
    "actuator/metrics",
    "actuator/configprops",

    # Git / config leaks
    ".git/HEAD",
    ".git/config",
    ".env",

    # Backups
    "backup.zip",
    "backup.tar.gz",
    "db.sql",
    "dump.sql",

    # GraphQL
    "graphql",
    "graphiql",
    "graphql/playground",
]


INTERESTING_STATUS = {200, 204, 301, 302, 307, 308, 401, 403}

async def scan_paths(client: httpx.AsyncClient, base_url: str, path: str):
    url = urljoin(base_url.rstrip("/") + "/", path)

    try:
        response = await client.get(url, follow_redirects=False)
    except httpx.RequestError as e:
        print(f"[ERROR] Request failed for {url}: {e}")
        return None
    
    status = response.status_code
    length = len(response.content)
    content_type = response.headers.get("Content-Type", "-")
    location = response.headers.get("Location")
    
    if status in INTERESTING_STATUS:
        return {
            "url": url,
            "status": status,
            "length": length,
            "content_type": content_type,
            "location": location
        }    
    return None 


async def run_scan(base_url: str, paths: list[str], concurrency: int, timeout: float):
    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)
    timeout_config = httpx.Timeout(timeout)

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WebScanner/1.0; +https://example.com/webscanner)"
    }

    async with httpx.AsyncClient(limits=limits, timeout=timeout_config, headers=headers) as client:
        semaphore = asyncio.Semaphore(concurrency)

        async def worker(path: str):
            async with semaphore:
                return await scan_paths(client, base_url, path)
            
        tasks = [worker(path) for path in paths]

        results = []

        for task in asyncio.as_completed(tasks):
            result = await task
            if result:
                results.append(result)
                print_result(result)

        return results
    
def print_result(result: dict):
    status = result["status"]
    url = result["url"]
    length = result["length"]
    content_type = result["content_type"]
    location = result["location"]
    
    line = f"[{status}] {url} (Length: {length}, Content-Type: {content_type}"
    if location:
        line += f" -> Location: {location}"

    print(line)

def load_wordlist(path: str | None):
    if not path:
        return DEFAULT_PATHS
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip().lstrip("/") 
                for line in f 
                if line.strip() and not line.startswith("#")]

def main():
    parser = argparse.ArgumentParser(description="Scan a web server for common paths.")
    parser.add_argument("url", help="The base URL of the web server to scan.")
    parser.add_argument("-w", "--wordlist", help="Path to a file containing a list of paths to scan.", default=None)
    parser.add_argument("-c", "--concurrency", type=int, help="Number of concurrent requests to make.", default=10)
    parser.add_argument("-t", "--timeout", type=float, help="Timeout for each request in seconds.", default=5.0)
    args = parser.parse_args()

    paths = load_wordlist(args.wordlist)
    print(f"Target: {args.url}")
    print(f"Paths to scan: {len(paths)}")
    print(f"Concurrency: {args.concurrency}")
    print()

    asyncio.run(run_scan(args.url, paths, args.concurrency, args.timeout))


if __name__ == "__main__":
    main()


# python web_scanner.py http://localhost:8080