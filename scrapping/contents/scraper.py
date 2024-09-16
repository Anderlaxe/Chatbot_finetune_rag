from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from time import sleep
import re
from bs4 import BeautifulSoup, Comment, UnicodeDammit
from markdownify import markdownify as md

chromedriver_autoinstaller.install()

STORAGE_FOLDER = "./raw/"

with open(STORAGE_FOLDER + "@sources.txt", "w") as f:
    pass

class CSrapper:
    def __init__(self, subdomain, pause_to_enter_creds=False):
        self.domain = "https://{}.university.fr/".format(subdomain)
        self.pause_to_enter_creds = pause_to_enter_creds

        self.to_visit = set()
        self.visited = []

        self.driver = webdriver.Chrome()

    def get_all_links(self):
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and (href[0] != "/" and (self.domain in href)):
                    href = re.sub(r"#.*$", "", href)
                    href = re.sub(r"\?.*$", "", href)
                    if (not re.findall(r"\.[a-zA-Z0-9]{2,4}$", href)):
                        if not any([x in href for x in ["/agenda", "/actualites", "/user", "index.php"]]):
                            if (href not in self.visited):
                                self.to_visit.add(href)
        except:
            pass
    
    def get_content(self):
        # get element by role = main
        content = self.driver.find_element(By.CLASS_NAME, "main-container")
        html = content.get_attribute("innerHTML")

        soup = BeautifulSoup(html, "html.parser")
        comments = soup.findAll(string=lambda text:isinstance(text, Comment))
        for comment in comments:
            comment.extract()
        [s.extract() for s in soup('script')]
        [s.extract() for s in soup('style')]
        for tag in soup.find_all(True):
            if hasattr(tag, "href"):
                if tag.href and tag.href[0] == "/":
                    tag.href = self.domain + tag.href
            if len(tag.get_text(strip=True)) == 0:
                tag.extract()
        
        markdown = md(UnicodeDammit(str(soup)).unicode_markup, heading_style="atx")
        markdown = re.sub(r"^\s*", "", markdown)
        markdown = re.sub(r"^\s*$", "", markdown, flags=re.MULTILINE)
        markdown = re.sub(r"\]\((?!http)(/.*?)\)", r"]({}/\1)".format(self.domain), markdown)
        markdown = re.sub(r"#+\s*$", "", markdown, flags=re.MULTILINE)
        return markdown

    def run(self):
        self.to_visit.add(self.domain)
        self.driver.get(self.domain)
        if self.pause_to_enter_creds:
            input("Press enter to continue after entering credentials")

        while bool(self.to_visit):
            link = self.to_visit.pop()
            if link not in self.visited:
                self.visited.append(link)
                self.driver.get(link)
                sleep(1)
                self.get_all_links()

                content = self.get_content()
                if content != "error":
                    new_filename = "{}.md".format(link.replace("/", "_"))
                    new_filename = re.sub(r"https?:__", "", new_filename)
                    new_filename = re.sub(r"-", "_", new_filename)
                    new_filename = re.sub(r".university.fr", "", new_filename)
                    new_filename = re.sub(r"_fr_", "_", new_filename)
                    new_filename = re.sub(r"_en_", "_", new_filename)
                    
                    with open(STORAGE_FOLDER + new_filename, "w", encoding='utf-8') as f:
                        f.write(content)
                    
                    with open(STORAGE_FOLDER + "@sources.txt", "a") as f:
                        f.write("{},{}\n".format(new_filename, link))
                        
                else:
                    print("Error on {}".format(link))

        self.driver.close()
            

CSrapper("linked_pages", pause_to_enter_creds=True).run()