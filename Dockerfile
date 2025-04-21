FROM python:3.13 AS builder
RUN pip install --upgrade pip poetry poetry-plugin-export

COPY pyproject.toml .

RUN poetry export -f requirements.txt --output requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r ./requirements.txt

RUN pip install -r requirements.txt


#########
# FINAL #
#########

FROM python:3.13

COPY --from=builder /usr/src/app/wheels /wheels
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

COPY ./src .

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0", "entur:app"]
EXPOSE 8000