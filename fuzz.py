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


def discover(args, test=False):
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

    # Initialize Test variables

    if test:
        global vectors
        global sanitized
        global sensitive
        global slow
        global unsanitized_inputs
        global sensitive_data
        global delayed_responses
        global http_errors

        vectors = [c.strip() for c in open(args.vectors).readlines()]
        sanitized = [c.strip() for c in open(args.sanitized_chars).readlines()] if args.sanitized_chars else ['<','>']
        sensitive = [c.strip() for c in open(args.sensitive).readlines()]
        slow = args.slow if args.slow else 500
        unsanitized_inputs = []
        sensitive_data = []
        delayed_responses = []
        http_errors = []

    if args.common_words: combs = utils.get_combinations(args.common_words)

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

    # If Test, print Sensitive Data, Unsanitized Inputs, Delayed Responses and HTTP Errors
    if test:
        print("*"*48 + "\nTest Results\n" + "*"*48)
        print("*"*48 + "\nSENSITIVE DATA\n" + "*"*48)
        for d in sensitive_data:
            print("URL: " + d[0])
            print("Input Tag: " + d[1])
            print("Input Vector: " + d[2])
            print("Sensitive Data Found: " + d[3] + "\n")
        print("*"*48 + "\n\n")

        print("*"*48 + "\nUNSANITIZED INPUTS\n" + "*"*48)
        for d in unsanitized_inputs:
            print("URL: " + d[0])
            print("Input Tag: " + d[1])
            print("Unsanitized Input Found: " + d[2] + "\n")
        print("*"*48 + "\n\n")

        print("*"*48 + "\nDELAYED RESPONSES\n" + "*"*48)
        for d in delayed_responses:
            print("URL: " + d[0])
            print("Response Time: " + str(d[1]) + "ms\n")
        print("*"*48 + "\n\n")

        print("*"*48 + "\nHTTP ERRORS\n" + "*"*48)
        for d in http_errors:
            print("URL: " + d[0])
            print("HTTP Status Code: " + str(d[1]))
            print("HTTP Status Code Description: " + d[2] + "\n")
        print("*"*48 + "\n\n")

        print("*"*48 + "\nTOTALS\n" + "*"*48)
        print("Total Sensitive Data Found: " + str(len(sensitive_data)))
        print("Total Unsanitized Inputs Found: " + str(len(unsanitized_inputs)))
        print("Total Delayed Responses Found: " + str(len(delayed_responses)))
        print("Total HTTP Errors Found: " + str(len(http_errors)))
        print("*"*48 + "\n\n")


def crawl(url):
    """
    Crawl a URL to parse and search for inputs. Can be Called Recursively
    """
    url = browser.absolute_url(url)
    if url in visited: return

    try:
        page = browser.open(url)

        if page.status_code != 200:
                    http_errors.append([page.url, page.status_code, get_status_code(page.status_code)])
        if page.elapsed.total_seconds() * 1000 > float(slow):
            delayed_responses.append([page.url, page.elapsed.total_seconds() * 1000])

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
        
        if args.command == 'test':
            test(browser.url,inputs)

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


def test(url, inputs):
    """
    Discover all inputs, then attempt a list of exploit vectors on those inputs. Report anomalies that could be vulnerabilities.
    """

    # Check all inputs
    for input_tag in inputs:
        name = input_tag.get('name')
        if name == 'submit' or name == 'Submit' or name == 'SUBMIT': continue
        # Check for sensitive data
        for vector in vectors:
            try:
                # submit each vector in the input field and check the response page for sensitive data
                browser.open(url)
                browser.select_form('form')
                browser[name] = vector
                page = browser.submit_selected()
                # check for sensitive data, delayed response or non 200 http response codes
                for s in sensitive:
                    if s in page.text:
                        sensitive_data.append([page.url, input_tag.prettify(), vector, s])
                if page.status_code != 200:
                    http_errors.append([page.url, page.status_code, get_status_code(page.status_code)])
                if page.elapsed.total_seconds() * 1000 > float(slow):
                    delayed_responses.append([page.url, page.elapsed.total_seconds() * 1000])
            except Exception as e:
                if args.verbose: print(e)
                continue
        # Check for unsanitized data
        for vector in sanitized:
            try:
                browser.open(url)
                browser.select_form('form')
                browser[name] = vector
                page = browser.submit_selected()
                if vector in page.text:
                    unsanitized_inputs.append([page.url, input_tag.prettify(),vector])
                if page.status_code != 200:
                    http_errors.append([page.url, page.status_code, get_status_code(page.status_code)])

                if page.elapsed.total_seconds() * 1000 > float(slow):
                    delayed_responses.append([page.url, page.elapsed.total_seconds() * 1000])
            except Exception as e:
                if args.verbose: print(e)
                continue


def get_status_code(code):
    """
    Get the status code information from the code.
    """
    if code == 200:
        return "Success (OK)"
    elif code == 301:
        return "Moved Permanently"
    elif code == 302:
        return "Found (Redirect)"
    elif code == 303:
        return "See Other (Redirect)"
    elif code == 400:
        return "Bad Request"
    elif code == 401:
        return "Unauthorized"
    elif code == 403:
        return "Forbidden"
    elif code == 404:
        return "Not Found"
    elif code >= 500 and code <= 599:
        return "Server Error"
    else:
        return "Unknown"

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

    # Vectors argument
    parser.add_argument("--vectors", type=str)

    # Sanitized Chars argument
    parser.add_argument("--sanitized-chars", type=str)

    # Sensitive argument
    parser.add_argument("--sensitive", type=str)

    # Slow argument
    parser.add_argument("--slow", type=str)

    global args
    args = parser.parse_args()


    # Go to Functions according to command selected
    if args.command == "discover":
        discover(args, test=False)
    elif args.command == "test":
        discover(args, test=True)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()