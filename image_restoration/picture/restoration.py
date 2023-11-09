from aip import AipImageProcess
from picture import utils

""" 你的 APPID AK SK """
APP_ID = '25832391'
API_KEY = '6NAMnu7BEUddoAfZSQbuHTyi'
SECRET_KEY = '9oy9kYyEvMf8KKrqeornWuBGTthmVCVv'

client = AipImageProcess(APP_ID, API_KEY, SECRET_KEY)

""" 读取图片 """


def get_file_content(file_path):
    with open(utils.change_http_url_to_local(file_path), 'rb') as fp:
        return fp.read()


repair_options = {
    '图像无损放大': '1',
    '图像去雾': '2',
    '图像对比度增强': '3',
    '拉伸图像恢复': '4',
    '图像修复': '5',
    '图像清晰度增强': '6',
    '黑白图像上色': '7',
    '图像风格转换': '8',
    '人像动漫化': '9'
}


# TODO 调用接口的同步异步问题待解决
def restoration(name, path):
    if len(name) == 1:
        repair_id = name
    else:
        repair_id = repair_options[name]
    image = get_file_content(path)
    if repair_id == '1':
        result = client.imageQualityEnhance(image)
        return result
    elif repair_id == '2':
        return client.dehaze(image)
    elif repair_id == '3':
        print('in 3')
        return client.contrastEnhance(image)
    elif repair_id == '4':
        return client.stretchRestore(image)
    # 似乎暂时不能使用
    elif repair_id == '5':
        return client.inpaintingByMask(image, rectangle=[{'width': 92, 'top': 25, 'height': 36, 'left': 10}])
    elif repair_id == '6':
        return client.imageDefinitionEnhance(image)
    elif repair_id == '7':
        print('in 7')
        return client.colourize(image)
    # 暂定风格转换为卡通
    elif repair_id == '8':
        options = {'option': "cartoon"}
        return client.styleTrans(image, options)
    elif repair_id == '9':
        return client.selfieAnime(image)
    else:
        return None
