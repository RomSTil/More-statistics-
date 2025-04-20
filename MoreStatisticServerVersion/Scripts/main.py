from JSONFileServer import JSONFileServer
from LeaderboardScraper import LeaderboardScraper
from settings import login_journal, password_journal


scrapper = LeaderboardScraper(password=password_journal, login=login_journal)
server = JSONFileServer(json_file_path="json")

scrapper.run()
server.run()