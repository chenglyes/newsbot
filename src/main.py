import os
import time
import json
import logging
import schedule
from concurrent.futures import ThreadPoolExecutor
from configs import Subscription, load_yaml_config
from paper import Paper
from llm import LLMClient
from fetcher import Fetcher
from senders import create_sender

class NewsBot:
    def __init__(self) -> None:
        self.config = load_yaml_config("configs/config.yaml")
        if self.config.thread_num and self.config.thread_num > 1:
            self.thread_pool = ThreadPoolExecutor(self.config.thread_num)
        else:
            self.thread_pool = None
        self.llm = LLMClient(
            model=self.config.llm.model,
            api_base=self.config.llm.api_base,
            api_key=self.config.llm.api_key,
        )
        self.fetcher = Fetcher()
        self.senders = [create_sender(**data) for data in self.config.senders]

    def translate_paper(self, paper: Paper) -> Paper:
        logging.info(f"translate paper '{paper.id}'")
        from prompts import translate_system_prompt
        user_prompt = f'{{"title": "{paper.title}", "summary": "{paper.summary}"}}'
        messages = [
            {"role": "system", "content": translate_system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = self.llm.chat(messages)
        if not response:
            logging.warning(f"no llm response from translate paper '{paper.id}'")
            return paper
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end]
            data = json.loads(json_str)
        except Exception as e:
            logging.exception(f"fail to parse llm response from translate paper '{paper.id}', exception '{e}'")
            return paper
        else:
            paper.title_translation = data.get("title", None)
            paper.summary_translation = data.get("summary", None)
            logging.info(f"success to translate paper '{paper.id}'")
            return paper

    def process_paper(self, paper: Paper):
        paper = self.translate_paper(paper)
        for sender in self.senders:
            self._run_job(lambda: sender.send(paper))

    def process_subscription(self, subscription: Subscription):
        logging.info(f"process subscription '{subscription.name}'")
        path = f"output/{subscription.name}/"
        os.makedirs(path, exist_ok=True)
        papers = self.fetcher.fectch(
            subscription.name,
            subscription.url,
            max_results=subscription.max_results
        )
        logging.info(f"fetched {len(papers)} papers")
        for paper in papers:
            self._run_job(lambda: self.process_paper(paper))
    
    def run(self):
        logging.info(f"running...")
        for subscription in self.config.subscriptions:
            schedule.every(subscription.interval).minutes.do(
                lambda: self._run_job(
                    lambda: self.process_subscription(subscription)
                )
            )
        schedule.run_all()
        while True:
            schedule.run_pending()
            time.sleep(5)

    def shutdown(self):
        schedule.clear()
        if self.thread_pool:
            self.thread_pool.shutdown(cancel_futures=True)

    def _run_job(self, job, *args, **kwargs):
        if self.thread_pool:
            self.thread_pool.submit(job, *args, **kwargs)
        else:
            job(*args, **kwargs)

if __name__ == "__main__":
    from datetime import datetime
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s]%(asctime)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                f"logs/{datetime.now().strftime("%Y%m%d-%H.%M.%S")}.log",
                encoding="utf-8",
            ),
        ],
    )
    from dotenv import load_dotenv
    if load_dotenv():
        logging.info("use dotenv")
    try:
        bot = NewsBot()
        bot.run()
    except KeyboardInterrupt:
        logging.info("stop because user interrupt")
    except Exception as e:
        logging.exception(e)
    else:
        bot.shutdown()
