#
#
# 【スクレイピングテンプレート】
#    01. ログイン            (requests)
#    02. スクレイピング実行    (BeautifulSoup ➔ Just One List ➔ CSV)
#    03. CSV出力 & スプシ記入 (CSV ➔ Google Sheets)
#
import requests
from bs4 import BeautifulSoup
import os
from glob import glob
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -------------------------------------------------------------
#
# ログイン画面のURL
#
url = 'https://education.showbooth.dmm.com/booth/login.php'
#
# セッション開始
#
session = requests.session()
#
# サーバーにポストする情報を、{ name属性: value属性 } の形で記入。
#
login_info = {
	'u_id': 'morifuji@trois-re.co.jp',
	'pass': 'troisre2012',
}
#
# ログイン処理
#
session.post(url, data=login_info)


# --------------------------------------------------------------
#
# スクレイピング実行
#
def search(url):
	#
	# セッションを保ったまま、ログインが必要なサイトのURLへアクセス
	#
	html = session.get(url)
	#
	# html.text もしくは、html.content
	#
	soup = BeautifulSoup(html.text, 'html.parser')
	#
	# スクレイピング処理
	#
	units = soup.find_all('div', {'class': 'offer_data_area'})
	_url = 'https://education.showbooth.dmm.com/sb-admin/booth/offer.php'
	for unit in units[:200]:
		html = session.get(_url + unit.find('a').attrs['href'])
		soup = BeautifulSoup(html.text, 'html.parser')
		elements = soup.find_all('div', {'class': 'tr_content'})

		profile = []
		for i,element in enumerate(elements):
			if i in (5,6):
				try:
					tags = element.select('.td_cnt')
					profile.append([tag.text.strip() for tag in tags])
				except:
					continue
			elif i in (0,1,2,3,4,7,8):
				try:
					profile.append(element.select_one('.td_cnt p').text)
				except:
					continue
		datasets.append(profile)
	#
	# ページネーションがあれば次ページへ遷移し、再帰的にスクレイピングする。
	#
	next_pagenation = soup.select('.new_pagenation .next .num')
	if len(next_pagenation) > 0:
		next_url = _url + next_pagenation[0].attrs['href']
		search(next_url)

# --------------------------------------------------------------
#
# CSV出力 & スプシ記入
#
def output(datasets):
	#
	# ---------------------------------------------------
	# 	csv 出力
	# ---------------------------------------------------
	#
	name = os.path.basename(__file__).split('.')[0]
	with open(name+'.csv', 'w') as f:
		w = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
		w.writerows(datasets)
		f.close()
	#
	# csv_pth = ./dmm_test.csv
	#
	csv_path = './' + glob('*.csv')[0]
	#
	# ---------------------------------------------------
	# 	csv → Google Sheets
	# ---------------------------------------------------
	#
	# 2つのAPIを記述しないと、
	# リフレッシュトークンを3600秒毎に発行し続けなければならない
	#
	scope = ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']
	#
	# Google Developer Console で登録した認証情報(json)を使用する。
	#
	credentials = ServiceAccountCredentials.from_json_keyfile_name(
            'trois-re-sales-list-9bb1f3c5fc52.json', scope)
	gc = gspread.authorize(credentials)
	#
	# スプシの一意キー
	#
	SPREADSHEET_KEY = '1BQ43UlivXqZAAE6hpl3NycGOhq978VcAkdlfNG8e8x0'
	#
	# ワークシート情報を取得
	#
	worksheet = gc.open_by_key(SPREADSHEET_KEY)
	#
	# ワークシートへ、CSV情報を書き込む
	#
	worksheet.values_update(
		'シート1',
		params={'valueInputOption': 'USER_ENTERED'},
		body={'values': list(csv.reader(open(csv_path, encoding='utf_8_sig')))}
	)

# --------------------------------------------------------------
#
# スクレイピングしたいURL
#
url = 'https://education.showbooth.dmm.com/sb-admin/booth/offer.php?parpage=200&cat=%E6%95%99%E8%82%B2%E3%83%BB%E6%95%99%E6%9D%90%E3%82%B3%E3%83%B3%E3%83%86%E3%83%B3%E3%83%84&genre=&tab=&search='
#
# csv化するリスト
#
datasets = [
	['法人名','職種','従業員数','役職名','興味のあるカテゴリ・ジャンル','来場の目的','プロフィール・課題感','参加にあたって期待すること']
]

# --------------------------------------------------------------
#
# メソッド実行
#
search(url)
output(datasets)
