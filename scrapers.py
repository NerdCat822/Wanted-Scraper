import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import time
import csv

class Job:

    def __init__(self, title, company, empolyment_type, location, link):
        self.title = title
        self.company = company
        self.employment_type = empolyment_type
        self.location = location
        self.link = link

class JobList:

    def __init__(self, list_name):
        self.list_name = list_name
        self.jobs = []

    def add_job(self, title, company, empolyment_type, location, link):
        new_job = Job(title, company, empolyment_type, location, link)
        self.jobs.append(new_job)

    def run_scraper_wwr(self, url):
        print("scraping We Work Remotely...")
        sum_wwr = 0

        def get_pages(url):
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser",)
            return len(soup.find("div", class_="pagination").find_all("span", class_="page"))

        def scrape_page_wwr(page_url):
            print(f"Scrapping {page_url}...")
            response = requests.get(page_url)
            soup = BeautifulSoup(response.content, "html.parser")
            jobs = soup.find("section", class_="jobs").find_all("li")[:-1]
            print(len(jobs), "jobs found")
            nonlocal sum_wwr
            sum_wwr += len(jobs)

            for job in jobs:

                title = job.find("span", class_="title").text
                
                try:
                    company, employment_type, region = job.find_all("span", class_="company")
                except:
                    company = job.find_all("span", class_="company")[0]
                    employment_type = job.find_all("span", class_="company")[1]
                    region = job.find("span", class_="region")

                try:
                    job_url = f"https://weworkremotely.com{job.find('div', class_='tooltip--flag-logo').next_sibling['href']}"
                except:
                    job_url = None

                self.add_job(title, company.text, employment_type.text, region.text, job_url)

        number_of_total_pages = get_pages(url)
        for x in range(number_of_total_pages):
            page_url = f"https://weworkremotely.com/remote-full-time-jobs?page={x+1}"
            scrape_page_wwr(page_url)
        print(sum_wwr, "jobs found in total\n")

    def run_scraper_remoteok(self, *, keyword:str=None, keywords:list[str]=[]):
        print("scraping Remote OK...")
        sum_remoteok = 0

        def scrape_page_remoteok(keyword):
            url = f"https://remoteok.com/remote-{keyword}-jobs"
            response = requests.get(url, headers={
                "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            })
            soup = BeautifulSoup(response.content, "html.parser")
            jobs = soup.find("table", id="jobsboard").find_all("td", class_="company_and_position")[1:]
            print(f"{len(jobs)} jobs found for keyword {keyword}")
            nonlocal sum_remoteok
            sum_remoteok += len(jobs)

            for job in jobs:
                title = job.find("h2", itemprop="title").text
                company = job.find("span", itemprop="hiringOrganization")
                region = job.find("div", class_="location")
                job_url = f"https://remoteok.com{job.find('a', itemprop='url')['href']}"
                self.add_job(title[1:-1], company.text[2:-3], None, region.text, job_url)

        self.run_func_for_keywords(keyword, keywords, scrape_page_remoteok)
        print(sum_remoteok, "jobs found in total\n")

    def run_scraper_wanted(self, *, keyword:str=None, keywords:list[str]=[]):
        print("scraping Wanted...")
        sum_wanted = 0

        def scrape_page_wanted(keyword):
            p = sync_playwright().start()
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(f"https://www.wanted.co.kr/search?query={keyword}&tab=position")
            time.sleep(1)

            for i in range(5):
                page.keyboard.down("End")
                time.sleep(1)
            time.sleep(1.5)
            content = page.content()
            p.stop()

            soup = BeautifulSoup(content, "html.parser")
            jobs = soup.find_all("div", class_="JobCard_container__FqChn")
            print(f"{len(jobs)} jobs found for keyword {keyword}")
            nonlocal sum_wanted
            sum_wanted += len(jobs)

            for job in jobs:
                title = job.find("strong", class_="JobCard_title__ddkwM").text
                company = job.find("span", class_="JobCard_companyName__vZMqJ").text
                job_url = f"https://www.wanted.co.kr{job.find('a')['href']}"
                self.add_job(title, company, None, None, job_url)        
        
        self.run_func_for_keywords(keyword, keywords, scrape_page_wanted)
        print(sum_wanted, "jobs found in total\n")

    def run_func_for_keywords(self, keyword, keywords, function):
        if keyword==None and keywords==[]:
            print("Please enter a keyword or a list of keywords.")
        else:
            if keyword!=None:
                keywords.append(keyword)
            keywords = set(keywords)
            for keyword in keywords:
                function(keyword)

    def save_to_file(self, file_name):

        file = open(f"{file_name}.csv", "w", encoding="utf-8", newline="")
        writter = csv.writer(file, lineterminator='\n')

        writter.writerow(["Title", "Company", "Employment Type", "Location", "Link"])
        for job in self.jobs:
            writter.writerow([job.title, job.company, job.employment_type, job.location, job.link])
        file.close()
        print(f"created file as '{file_name}.csv'")