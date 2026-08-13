import time
import json
import csv
import requests
import statistics
from datetime import datetime

url = "http://127.0.0.1:8000/v1/chat/completions"
tokenize_url = "http://127.0.0.1:8000/extras/tokenize/count"

NUMBER_OF_REQUESTS = 30
MAX_TOKENS = 100

data = {
    "messages": [
        {
            "role": "user",
            "content": "Explain what artificial intelligence is in simple terms."
        }
    ],
    "max_tokens": MAX_TOKENS,
    "stream": True
}

results = []

for i in range(NUMBER_OF_REQUESTS):

    start_time = time.perf_counter()
    first_token_time = None
    generated_text = ""

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

        if content:

            if first_token_time is None:
                first_token_time = time.perf_counter()

            generated_text += content

    end_time = time.perf_counter()

    token_response = requests.post(
        tokenize_url,
        json={"input": generated_text}
    )
    token_response.raise_for_status()

    completion_tokens = token_response.json()["count"]

    ttft = first_token_time - start_time
    total_latency = end_time - start_time
    generation_time = end_time - first_token_time
    generation_speed = completion_tokens / generation_time

    result = {
        "request": i + 1,
        "ttft_seconds": round(ttft, 4),
        "total_latency_seconds": round(total_latency, 4),
        "generation_time_seconds": round(generation_time, 4),
        "completion_tokens": completion_tokens,
        "tokens_per_second": round(generation_speed, 2)
    }

    results.append(result)

    print(
        f"Request {i + 1:02d} | "
        f"TTFT: {ttft:.3f}s | "
        f"Total: {total_latency:.3f}s | "
        f"Tokens: {completion_tokens} | "
        f"Speed: {generation_speed:.2f} tok/s"
    )


timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"benchmark_{timestamp}.csv"

with open(filename, "w", newline="") as csvfile:

    writer = csv.DictWriter(
        csvfile,
        fieldnames=results[0].keys()
    )

    writer.writeheader()
    writer.writerows(results)


ttfts = [r["ttft_seconds"] for r in results]
latencies = [r["total_latency_seconds"] for r in results]
speeds = [r["tokens_per_second"] for r in results]

print()
print("BENCHMARK COMPLETE")
print("==================")
print("Requests:", NUMBER_OF_REQUESTS)
print("Max tokens:", MAX_TOKENS)
print()
print("Average TTFT:", round(statistics.mean(ttfts), 3), "seconds")
print("Average latency:", round(statistics.mean(latencies), 3), "seconds")
print("Average speed:", round(statistics.mean(speeds), 2), "tokens/sec")
print()
print("Saved to:", filename)
