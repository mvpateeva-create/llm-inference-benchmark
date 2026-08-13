import matplotlib.pyplot as plt


# 1. OUTPUT TOKENS vs TOTAL LATENCY

tokens = [10, 50, 100]
token_latency = [0.243, 1.168, 2.251]

plt.figure(figsize=(7, 5))
plt.plot(tokens, token_latency, marker="o")
plt.xlabel("Max output tokens")
plt.ylabel("Average latency (seconds)")
plt.title("Output Length vs Total Latency")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("output_tokens_vs_latency.png", dpi=200)
plt.close()


# 2. PROMPT SIZE vs TTFT

prompt_labels = ["Short", "Medium", "Long", "Very long"]
prompt_ttft = [0.031, 0.039, 0.181, 0.271]

plt.figure(figsize=(7, 5))
plt.plot(prompt_labels, prompt_ttft, marker="o")
plt.xlabel("Prompt size")
plt.ylabel("Average TTFT (seconds)")
plt.title("Prompt Size vs Time to First Token")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("prompt_size_vs_ttft.png", dpi=200)
plt.close()


# 3. CONCURRENCY vs LATENCY

concurrency = [1, 2, 4]
concurrency_latency = [1.112, 1.670, 3.052]

plt.figure(figsize=(7, 5))
plt.plot(concurrency, concurrency_latency, marker="o")
plt.xlabel("Concurrent requests")
plt.ylabel("Average latency (seconds)")
plt.title("Concurrency vs Latency")
plt.xticks(concurrency)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("concurrency_vs_latency.png", dpi=200)
plt.close()


# 4. CONCURRENCY vs THROUGHPUT

throughput = [0.90, 0.90, 0.85]

plt.figure(figsize=(7, 5))
plt.plot(concurrency, throughput, marker="o")
plt.xlabel("Concurrent requests")
plt.ylabel("Throughput (requests/sec)")
plt.title("Concurrency vs Throughput")
plt.xticks(concurrency)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("concurrency_vs_throughput.png", dpi=200)
plt.close()


print("Charts created successfully!")
print("1. output_tokens_vs_latency.png")
print("2. prompt_size_vs_ttft.png")
print("3. concurrency_vs_latency.png")
print("4. concurrency_vs_throughput.png")
