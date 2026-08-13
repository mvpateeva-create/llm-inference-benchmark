import time
import json
import csv
import requests
import statistics
from datetime import datetime

url = "http://127.0.0.1:8000/v1/chat/completions"

REQUESTS_PER_TEST = 20
MAX_TOKENS = 50

prompt_tests = {
    "short": "Explain artificial intelligence.",
    "medium": "Explain artificial intelligence in simple terms, including what models do, how they learn from data, and where they are used.",
    "long": "Artificial intelligence is used in many systems. " * 50,
    "very_long": "Artificial intelligence is used in many systems. " * 150
}

all_results = []

for prompt_name, prompt_text in prompt_tests.items():

    print()
    print("=" * 50)
    print("Testing prompt =", prompt_name)
    print("Characters =", len(prompt_text))
    print("=" * 50)

    for i in range(REQUESTS_PER_TEST):

        data = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt_text
                }
            ],
            "max_tokens": MAX_TOKENS,
            "stream": True
        }

        start_time = time.perf_counter()
        first_token_time = None

        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()

        for line in response.iter_lines():

            if not line:
                continue

            line = line.decode("utf-8")

            if not line.startswith("data: "):
                continue

            payload = line[6:]

            if payload == "[DONE]":
                break

            chunk = json.loads(payload)

            content = chunk["choices"][0]["delta"].get("content", "")

            if content and first_token_time is None:
                first_token_time = time.perf_counter()

        end_time = time.perf_counter()

        ttft = first_token_time - start_time
        total_latency = end_time - start_time

        result = {
            "prompt_type": prompt_name,
            "prompt_characters": len(prompt_text),
            "request": i + 1,
            "ttft_seconds": round(ttft, 4),
            "total_latency_seconds": round(total_latency, 4)
        }

        all_results.append(result)

        print(
            f"Request {i + 1:02d} | "
            f"TTFT: {ttft:.3f}s | "
            f"Total: {total_latency:.3f}s"
        )


timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"prompt_benchmark_{timestamp}.csv"

with open(filename, "w", newline="") as csvfile:

    writer = csv.DictWriter(
        csvfile,
        fieldnames=all_results[0].keys()
    )

    writer.writeheader()
    writer.writerows(all_results)


print()
print()
print("SUMMARY")
print("=======")

for prompt_name in prompt_tests:

    subset = [
        r for r in all_results
        if r["prompt_type"] == prompt_name
    ]

    ttfts = [r["ttft_seconds"] for r in subset]
    latencies = [r["total_latency_seconds"] for r in subset]

    print()
    print("Prompt:", prompt_name)
    print("Average TTFT:   ", round(statistics.mean(ttfts), 3), "seconds")
    print("Average latency:", round(statistics.mean(latencies), 3), "seconds")

print()
print("Saved to:", filename)
