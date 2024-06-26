FROM python:3.10-slim
WORKDIR /app
COPY ./ /app
RUN pip install --no-cache-dir -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

