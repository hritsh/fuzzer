import argparse
import mechanicalsoup
import utils

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
    global base_url
    global guessed

    browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')

    # Initialize visited links and data
    visited = []
    guessed = set()
    parse_urls = {}
    form_inputs = []
    skiplinks = ["."]
    base_url = args.url

    if args.common_words: combs = utils.get_combinations("./" + args.common_words)

    if args.custom_auth: setup()

    # Print browser page
    # browser.open(args.url)
    # print(browser.page)

    # Get cookies
    browser.open(args.url)
    cookies = browser.get_cookiejar()
    cookies = [{"name": c.name, "value": c.value} for c in cookies]

    # Guess combinations
    guess(args.url)

    # Start crawling from base link
    crawl(args.url)

    # Crawl guessed pages if not already crawled
    for link in guessed: crawl(link)

    # Print Links Discovered
    print("*"*48 + "\nLINKS DISCOVERED\n" + "*"*48)
    for l in visited:
        print(l)
    print("*"*48 + "\n\n")

    # Print Guessed Pages
    print("*"*48 + "\nPAGES SUCCESSFULLY GUESSED\n" + "*"*48)
    if not args.common_words: print("Common Word File Not Specified")
    for l in guessed:
        print(l)
    print("*"*48 + "\n\n")

    # Print Parsed URLs
    print("*"*48 + "\nPARSED URLS\n" + "*"*48)
    for url in parse_urls:
        print(parse_urls[url])
    print("*"*48 + "\n\n")

    # Print Form Inputs
    print("*"*48 + "\nFORM INPUTS\n" + "*"*48)
    # for url in form_inputs:
    #     print(url)
    utils.print_table(form_inputs)

    print("*"*48 + "\n\n")

    # Print Cookies
    print("*"*48 + "\nCOOKIES\n" + "*"*48)
    for c in cookies: print(c["name"] + "=" + c["value"])
    print("*"*48)

def crawl(url):
    """
    Crawl a URL to parse and search for inputs. Can be Called Recursively
    """
    url = browser.absolute_url(url)
    if url in visited: return

    try:
        page = browser.open(url)

        # Check if Page Exists
        if page is None or page.status_code // 100 not in (2,3): return
        visited.append(url)
        
        # Parse URLs
        if '?' in url:
            base_url, query_params = url.split('?', 1)
            query_params = query_params.split('&')
            parse_urls[base_url] = parse_urls.get(base_url, [base_url]) + query_params
        else:
            parse_urls[url] = [url]

        # Find Form Inputs
        inputs = browser.page.find_all('input')
        for input_tag in inputs:
            name = input_tag.get('name')
            value = input_tag.get('value', '')
            input_dict = {"url": page.url, "name": name, "value": value}
            form_inputs.append(input_dict)

        # Traverse Links
        for link in browser.links():
            href = link["href"]
            if href.startswith("http://") or href.startswith("https://"): continue
            if href in skiplinks or href in visited or href == url: continue
            if args.verbose: print("Current Page: " + url + "\tCrawling link: " + href)
            crawl(href)
    except:
        return

def guess(url):
    """
    Guess if Common Words Argument is Provided
    """
    if args.common_words:
        browser.open(url)
        for comb in combs:
            try:
                page = browser.open(url + comb)
                if args.verbose: print("Guessing " + page.url)
                if page is None or page.status_code // 100 not in (2,3): continue
                if args.verbose: print("Found Guess: " + page.url)
                guessed.add(page.url)
                parse_urls[url] = parse_urls.get(url, [url])
            except Exception as e:
                if args.verbose: print(e)
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
    parser.add_argument("--common-words", type=str, required=False)

    # Verbose argument    
    parser.add_argument("--verbose", "-v", action="store_true")

    global args
    args = parser.parse_args()


    # Go to Functions according to command selected
    if args.command == "discover":
        discover(args)
    elif args.command == "test":
        test(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()