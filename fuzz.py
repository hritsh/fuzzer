import argparse
import mechanicalsoup

def discover(args):
    """
    Output a comprehensive, human-readable list of all discovered inputs to the system. Techniques include both crawling and guessing.
    """
    browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')
    if args.custom_auth:
        # Setup Database
        browser.open(args.url + "/setup.php")
        browser.select_form('form[action="#"]')
        response = browser.submit_selected()

        # Login
        browser.open(args.url)
        browser.select_form('form[action="login.php"]')
        browser['username'] = 'admin'
        browser['password'] = 'password'
        response = browser.submit_selected()

        # Set Security to Low
        browser.open(args.url + "/security.php")
        browser.follow_link('security.php')
        browser.select_form('form[action="#"]')
        browser['security'] = 'low'
        response = browser.submit_selected()

        browser.open(args.url)
        print(browser.page)

def test(args):
    """
    Discover all inputs, then attempt a list of exploit vectors on those inputs. Report anomalies that could be vulnerabilities.
    """
    pass
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A command line fuzz-testing tool")

    # Choice for the 'discover' and 'test' commands
    parser.add_argument("command", choices=['discover', 'test'])

    # Enter URL to scan
    parser.add_argument("url", type=str)

    # Custom Auth argument
    parser.add_argument("--custom-auth", type=str)
    
    args = parser.parse_args()

    # Go to Functions according to command selected
    if args.command == "discover":
        discover(args)
    elif args.command == "test":
        test(args)
    else:
        parser.print_help()
