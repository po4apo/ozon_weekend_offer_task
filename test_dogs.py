import random

import pytest
import requests


class YaUploader:
    def __init__(self):
        pass

    def create_folder(self, path, token): # token лучше получать из окружения или вообще из 
        # url и headers лучше вынести в конструктор
        # ендпоинты лучше вынести в отдельный enum
        url_create = 'https://cloud-api.yandex.net/v1/disk/resources' 
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {token}'}
        response = requests.put(f'{url_create}?path={path}', headers = headers) # response лучше вернуть, либо вообще убрать

    def upload_photos_to_yd(self, token, path, url_file, name):
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {token}'}
        params = {"path": f'/{path}/{name}', 'url': url_file, "overwrite": "true"}
        resp = requests.post(url, headers=headers, params=params) # response лучше вернуть, либо вообще убрать


def get_sub_breeds(breed):
    res = requests.get(f'https://dog.ceo/api/breed/{breed}/list')
    return res.json().get('message', [])


def get_urls(breed, sub_breeds):
    url_images = []
    if sub_breeds:
        for sub_breed in sub_breeds:
            res = requests.get(f"https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random")
            sub_breed_urls = res.json().get('message')
            url_images.append(sub_breed_urls)
    else:
        url_images.append(requests.get(f"https://dog.ceo/api/breed/{breed}/images/random").json().get('message'))
    return url_images


def u(breed): # кошмар, а не название. Название должно отражать суть того что делает функция, можно назвать upload_breed_images
    sub_breeds = get_sub_breeds(breed)
    urls = get_urls(breed, sub_breeds)
    yandex_client = YaUploader()
    # test_folder не стоит хардкодить в таком виде
    # думаю лучше было бы вынести это в какую-то конфигурацию
    yandex_client.create_folder('test_folder', "AgAAAAAJtest_tokenxkUEdew") 
    for url in urls:
        part_name = url.split('/') # чтобы такое не делать нужно использовать pathlib
        name = '_'.join([part_name[-2], part_name[-1]])
        yandex_client.upload_photos_to_yd("AgAAAAAJtest_tokenxkUEdew", "test_folder", url, name)

# в данном случае случайный выбор породы не допустим, так как он влияет на результат теста
# случайные данные не должные влиять на результат, иначе тест нельзя воспроизвести
@pytest.mark.parametrize('breed', ['doberman', random.choice(['bulldog', 'collie'])]) 
# proverka? названия нужно писать на английском
def test_proverka_upload_dog(breed: str):
    u(breed)
    # проверка
    url_create = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth AgAAAAAJtest_tokenxkUEdew'}
    response = requests.get(f'{url_create}?path=/test_folder', headers=headers)
    assert response.json()['type'] == "dir"
    assert response.json()['name'] == "test_folder" # тут проверяется api yandex
    assert True # лучшая проверка :), но так лучше не делать
    # даже если тут нужен if, то только для assert len(response.json()['_embedded']['items'])
    # цикл for без проблем можно вынести
    if get_sub_breeds(breed) == []: 
        assert len(response.json()['_embedded']['items']) == 1
        for item in response.json()['_embedded']['items']:
            assert item['type'] == 'file'
            assert item['name'].startswith(breed)

    else:
        assert len(response.json()['_embedded']['items']) == len(get_sub_breeds(breed))
        for item in response.json()['_embedded']['items']:
            assert item['type'] == 'file'
            assert item['name'].startswith(breed)


# слишком много отступов в конце файла, достаточно одного