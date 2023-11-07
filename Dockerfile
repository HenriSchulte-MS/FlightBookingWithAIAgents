FROM python:3.11-slim
ENV PORT 5000
EXPOSE 5000
WORKDIR /usr/src/app

COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r app/requirements.txt

COPY . .

ENTRYPOINT ["python"]
CMD ["app/app.py"]
