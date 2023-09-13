FROM ubi9/python-311

USER 0:0
COPY .
RUN chown -R 1001:0 . && chmod -R g=u .
USER 1001

RUN pip install -U "pip>=19.3.1" && \
    pip install '.[cli]'

EXPOSE 8080
ENV RESPONSE="hello world!"

CMD python kmg/kitchen/http --response "$RESPONSE" --listen-address 8080