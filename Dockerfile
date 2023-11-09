FROM python:3.8.5

ENV HOME=/opt/app/backend

WORKDIR $HOME

COPY requirements.txt $HOME
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
RUN pip install baidu-aip -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
RUN pip install chardet
RUN pip install -i https://pypi.douban.com/simple pillow
RUN pip install django-cors-headers
RUN pip install pymysql

COPY image_restoration/ $HOME
COPY config/ $HOME

EXPOSE 80

ENV PYTHONUNBUFFERED=true
CMD ["/bin/sh", "run.sh"]
