from JSONFileServer import JSONFileServer
from LeaderboardScraper import LeaderboardScraper
from settings import login_journal, password_journal
import datetime

current_date = datetime.date.today()
scrapper = LeaderboardScraper(password=password_journal, login=login_journal)
server = JSONFileServer(json_file_path=f"json/leader_data_{current_date.strftime('%d')}_{current_date.strftime('%B')}_{current_date.strftime('%Y')}.json", port=8080)

# scrapper.run()
server.run()