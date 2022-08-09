#!/usr/bin/env python
import os
from dataclasses import dataclass

import click
import requests
from opentelemetry import trace


tracer = trace.get_tracer(__name__)


@dataclass(frozen=True)
class CounterClient:
    host: str = os.environ.get("COUNTER_HOST", "localhost")
    port: str = os.environ.get("COUNTER_PORT", "8000")

    def get_counts(self):
        resp = requests.get(f"http://{self.host}:{self.port}/")
        resp.raise_for_status()
        return resp.json()


@dataclass(frozen=True)
class WordsCounter:
    host: str = os.environ.get("WORD_COUNTER_HOST", "localhost")
    port: str = os.environ.get("WORD_COUNTER_PORT", "8001")

    def get_words_in_sentence(self, sentence: str):
        resp = requests.get(f"http://{self.host}:{self.port}/words_counter/{sentence}")
        resp.raise_for_status()
        return resp.json()


counter_service = CounterClient()
word_counter_service = WordsCounter()


@click.group()
def cli():
    pass


@cli.command()
@tracer.start_as_current_span("global_counts")
def global_counts():
    """Prints the global counters"""
    counts = counter_service.get_counts()
    for key, count in sorted(counts.items()):
        print(f"{key:20}: {count}")


@cli.command()
@click.argument("sentence", envvar="SENTENCE", type=str)
@tracer.start_as_current_span("count_words")
def word_counter(sentence: str):
    """Prints the word counters"""
    counts = word_counter_service.get_words_in_sentence(sentence)
    print(counts)


if __name__ == "__main__":
    cli()
