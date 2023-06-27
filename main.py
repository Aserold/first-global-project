import requests
import datetime
import json


class VK:
    def __init__(self, vktoken):
        self.vktoken = vktoken
        
        
    def get_photo_data(self, userid, amount):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'owner_id': str(userid),
            'album_id': 'profile',
            'extended': '1',
            'access_token': vktoken,
            'v':'5.131'
        }
        res = requests.get(url, params=params).json()
        res = res['response']['items']
        # print(res)
        all_data_list = []
        cut_data_list = []
        like_check = []
        
        for item in res:
            temporary_dict = {}
            if item['likes']['count'] in like_check:
                temporary_dict['name'] = f"{datetime.datetime.fromtimestamp(item['date']).strftime('%Y-%m-%d')}.jpg"
            else:
                temporary_dict['name'] = str(f"{item['likes']['count']}.jpg")
            like_check.append(item['likes']['count'])
            for size in item['sizes']:
                if size['type'] == 'z':
                    temporary_dict['photo_url'] = size['url']
                    temporary_dict['size'] = 'z'
                elif size['type'] == 'y':
                    temporary_dict['photo_url'] = size['url']
                    temporary_dict['size'] = 'y'
                elif size['type'] == 'x':
                    temporary_dict['photo_url'] = size['url']
                    temporary_dict['size'] = 'x'
                elif size['type'] == 'm':
                    temporary_dict['photo_url'] = size['url']
                    temporary_dict['size'] = 'm'
                elif size['type'] == 's':
                    temporary_dict['photo_url'] = size['url']
                    temporary_dict['size'] = 's'
                
                    
            all_data_list.append(temporary_dict)
        global item_count
        item_count = sum('name' in item for item in all_data_list)

        if amount == 'all':
            return all_data_list
        elif amount >= item_count:
            return all_data_list
        else:
            item_count = amount
            cut_data_list = all_data_list[:amount]
            return cut_data_list
        
    


class Yandex:
    def __init__(self, token):
        self.token = token

        
    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }
    
    def create_folder(self, folder_name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': folder_name}
        response = requests.put(url, headers=self.get_headers(), params=params)
        
    def upload_photo(self, url, folder_name, file_name):
        response = requests.get(url)
    
        if response.status_code == 200:
            upload_url = f"https://cloud-api.yandex.net/v1/disk/resources/upload?path={folder_name}/{file_name}&overwrite=true"
            headers = {
                "Authorization": f"OAuth {self.token}",
            }
            
            upload_response = requests.get(upload_url, headers=headers)
            
            if upload_response.status_code == 200:
                upload_data = upload_response.json()
                href = upload_data["href"]
                
                upload_file_response = requests.put(href, data=response.content)
                
                if upload_file_response.status_code == 201:
                    pass
                else:
                    print("Ошибка загрузки файла на Яндекс.Диск.")
            else:
                print("Ошибка получения ссылки для загрузки файла на Яндекс.Диск.")
        else:
            print("Ошибка загрузки фотографии.")



       
if __name__ == '__main__':
    # token = input('Введите токен Яндекс>>>> ')
    # vktoken = input('Введите токен ВК>>>> ')
    token = '' #введите ваш токен с Полигона Яндекс.Диска
    vktoken = '' #введите ваш токен vk api
    vk_test = VK(vktoken)
    ya_disk = Yandex(token)
    
    
    def ask_amount():
        amount = input('Введите количество фотографий(по учолчанию 5), которые вы хотите скачать(! - Скачать все)>>>> ')
        if amount == '!':
            amount = 'all'
            return amount
        try:
            amount = int(amount)
        except ValueError:
            amount = 5
        return amount
        
    def progress_bar(progress, total, message):
        percent = 100 * (progress / float(total))
        bar = '█' * int(percent) + '-' * (100 - int(percent))
        print(f'\r|{bar}| {percent:.2f}% {message}', end='\r')
    
    
    id_ = input('Введите vk id>>>>')
    amount = ask_amount()
    data = vk_test.get_photo_data(id_, amount)
    # print(data)
    ya_disk.create_folder('vk_pfp')
    
    json_data = []
    
    for index, item in enumerate(data):
        temp_dict = {}
        name = item['name']
        photo_url = item['photo_url']
        ya_disk.upload_photo(photo_url, 'vk_pfp', name)
        temp_dict['file_name'] = item['name']
        temp_dict['size'] = item['size']
        json_data.append(temp_dict)
        progress_bar(index + 1, item_count, 'Загрузка фотографий...')

    with open('info.json', 'w', encoding='utf8') as file:
        json.dump(json_data, file, indent=1)

    print(f'\nПрограмма выполнена!')