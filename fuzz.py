import argparse
import mechanicalsoup
import utils
import requests

def setup():
    # Setup Database
        print("SETTING UP DATABASE")
        browser.open(args.url + "/setup.php")
        browser.select_form('form[action="#"]')
        browser.submit_selected()

        # Login
        print("LOGGING IN")
        browser.open(args.url)
        browser.select_form('form[action="login.php"]')
        browser['username'] = 'admin'
        browser['password'] = 'password'
        browser.submit_selected()

        # Set Security to Low
        print("CHANGING SECURITY TO LOW")
        browser.open(args.url + "/security.php")
        browser.follow_link('security.php')
        browser.select_form('form[action="#"]')
        browser['security'] = 'low'
        browser.submit_selected()

        # Set Logout Link
        skiplinks.append("logout.php")


def discover(args):
    """
    Output a comprehensive, human-readable list of all discovered inputs to the system. Techniques include both crawling and guessing.
    """
    global browser
    global visited
    global parse_urls
    global form_inputs
    global cookies
    global combs
    global skiplinks

    browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')

    # Initialize visited links and data
    visited = []
    parse_urls = []
    form_inputs = []
    skiplinks = ["."]

    if args.common_words: combs = utils.get_combinations(args.common_words)

    if args.custom_auth: setup()

    # Print browser page
    # browser.open(args.url)
    # print(browser.page)

    # Get cookies
    browser.open(args.url)
    cookies = browser.get_cookiejar()
    print(cookies)

    # Start crawling from base link
    crawl(args.url)

def crawl(url):
    browser.absolute_url(url)
    print("Current Page: " + url)
    if url in visited: return
    visited.append(url)

    try:
        res = browser.open(url)
        print(res.status_code)
        if res.status_code // 100 not in (2,3): return
        for link in browser.links():
            href = link["href"]
            if href.startswith("http://") or href.startswith("https://") or href in url: continue
            href = browser.absolute_url(href)
            if href in skiplinks or href in visited or href == url: continue
            print("Current Page: " + url + "\tCrawling link: " + href)
            crawl(href)
    except:
        return

    if args.common_words:
        for comb in combs:
            try:
                comb = browser.absolute_url(comb)
                print("Testing combination: " + comb)
                res = browser.open(comb)
                if res.status_code // 100 not in (2,3): continue
                crawl(url + comb + "/")
            except:
                continue


def test(args):
    """
    Discover all inputs, then attempt a list of exploit vectors on those inputs. Report anomalies that could be vulnerabilities.
    """
    pass
    

def main():
    """
    Main program.
    """
    parser = argparse.ArgumentParser(description="A command line fuzz-testing tool")

    # Choice for the 'discover' and 'test' commands
    parser.add_argument("command", choices=['discover', 'test'])

    # Enter URL to scan
    parser.add_argument("url", type=str)

    # Custom Auth argument
    parser.add_argument("--custom-auth", type=str)

    # Common words argument    
    parser.add_argument("--common-words", type=str)

    global args
    args = parser.parse_args()


    # Go to Functions according to command selected
    if args.command == "discover":
        discover(args)
        print(visited)
    elif args.command == "test":
        test(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()