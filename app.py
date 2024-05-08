from scrapers import JobList

my_job_list = JobList("my job list")

print(f"my job list : {my_job_list.jobs}\n")

my_job_list.run_scraper_wwr("https://weworkremotely.com/remote-contract-jobs#job-listings")
search_words = ["flutter", "python", "javascript"]
my_job_list.run_scraper_remoteok(keywords=search_words)
my_job_list.run_scraper_wanted(keyword="rust", keywords=search_words)

print("total jobs found :", len(my_job_list.jobs))

my_job_list.save_to_file(my_job_list.list_name)