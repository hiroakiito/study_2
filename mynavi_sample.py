import os
import pandas as pd
import numpy as np
from selenium.webdriver import Chrome, ChromeOptions
import time
import logging

# debug.logフォルダを出力
logging.basicConfig(filename='debug.log', level=logging.DEBUG)

### Chromeを起動する関数
def set_driver(driver_path,headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）の設定
    if headless_flg==True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return Chrome(executable_path=os.getcwd() + "/" + driver_path,options=options)

def get_site_info(driver, list_info):
    # 検索結果を取得
    name_list=driver.find_elements_by_class_name("cassetteRecruit__name")
    copy_list=driver.find_elements_by_class_name("cassetteRecruit__copy")
    status_list=driver.find_elements_by_class_name("labelEmploymentStatus")
    table_list=driver.find_elements_by_class_name("tableCondition")
    update_date_list=driver.find_elements_by_class_name("cassetteRecruit__updateDate")
    end_date_list=driver.find_elements_by_class_name("cassetteRecruit__endDate")

    # 1ページ分繰り返し
    print("{},{},{},{},{},{}".format(len(copy_list),len(status_list),len(name_list),len(table_list),len(update_date_list),len(end_date_list)))
    for name,copy,status,table,updatedate,enddate in zip(name_list,copy_list,status_list,table_list,update_date_list,end_date_list):
        print(name.text)
        print(copy.text)
        print(status.text)
        table_td_list = table.find_elements_by_class_name("tableCondition__body")
        for table_td in table_td_list:
           print(table_td.text)
        print(updatedate.text)
        print(enddate.text)

        list_info += [[name.text, copy.text, status.text, table_td_list[0].text, table_td_list[1].text, table_td_list[2].text, table_td_list[3].text]]
        logging.debug(f'現在 {len(list_info)}件目取得')
    return list_info

### main処理
def main():
    search_keyword=input("求人情報検索ワードを入力してください >>> ")
    # driverを起動
    driver=set_driver("chromedriver.exe",False)
    # Webサイトを開く
    driver.get("https://tenshoku.mynavi.jp/")
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    time.sleep(5)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    
    # 検索窓に入力
    driver.find_element_by_class_name("topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()

    # dataframe用のリスト作成
    list_info = []

    # 画面に次ページボタンがあればクリックして処理を継続
    roop_flg = True
    while(roop_flg):
        try:
            list_info = get_site_info(driver, list_info)
            # 次ページへのリンクがある位置までスクロール
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            next_link = driver.find_elements_by_class_name("iconFont--arrowLeft")
            if len(next_link) == 0:
                # 最後のページまで読込が完了したらCSVに出力する。
                roop_flg = False
                df = pd.DataFrame(data=list_info,columns=["会社情報", "採用情報概要", "雇用形態", "仕事内容", "対象となる方", "勤務地", "給与"])
                df.to_csv('sample.csv', encoding='utf_8_sig')
            else:
                next_link[0].click()
                driver.wait(10)
        except IndexError:
            logging.debug('ページのデータがありません')
            continue
    
    print("処理が終了しました。")

### 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
