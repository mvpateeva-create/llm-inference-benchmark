# LLM Inference Performance Benchmark

## Objective

Evaluate the performance characteristics of local LLM inference
and analyze how output length, prompt size, concurrency and CPU
configuration affect latency and throughput.

## Test environment

Model: Qwen2.5-0.5B-Instruct  
Format: GGUF  
Quantization: Q4_K_M  
Runtime: llama.cpp / llama-cpp-python  

Hardware:
- MacBook Pro
- Quad-Core Intel Core i5, 2.3 GHz
- 4 CPU cores
- Hyper-Threading enabled
- 8 GB RAM

Execution:
- Local inference
- HTTP API on 127.0.0.1:8000

## Metrics

The following metrics were used:

- TTFT (Time to First Token) — time between sending the request
  and receiving the first generated token.
- Total latency — time between sending the request and receiving
  the complete response.
- Generation speed — number of generated tokens per second.
- Throughput — number of completed requests per second.

These metrics were selected because they describe different
parts of the user experience and system performance.

TTFT reflects how quickly the user starts seeing a response.

Generation speed reflects how quickly the model continues
generating after the response starts.

Total latency reflects complete response time.

Throughput reflects the capacity of the system under load.

## Methodology

A local LLM server was started using llama.cpp.

A Python client was created to send test prompts to the local API,
measure performance metrics and save raw observations to CSV files.

Streaming responses were used to measure TTFT.

The llama.cpp tokenizer endpoint was used to calculate the real
number of generated tokens instead of approximating tokens by words.

Each main benchmark was executed repeatedly to reduce the impact
of a single measurement.

## Experiment 1 — Baseline

30 sequential requests were executed with:

max_tokens = 100

For each request the benchmark measured:

- TTFT
- total latency
- generation time
- completion tokens
- generation speed

Example stable result:

Average TTFT: 0.028 s  
Average latency: 2.344 s  
Average generation speed: 43.01 tokens/s

## Experiment 2 — Output length

The output limit was changed while keeping the prompt constant.

Results:

| Max output tokens | Average TTFT | Average latency | Average speed |
|---|---:|---:|---:|
| 10 | 0.030 s | 0.243 s | 47.06 tokens/s |
| 50 | 0.027 s | 1.168 s | 43.84 tokens/s |
| 100 | 0.027 s | 2.251 s | 43.33 tokens/s |

### Finding

Total latency increased approximately linearly with output length.

TTFT remained almost unchanged.

Generation speed remained relatively stable for longer outputs.

This indicates that output length is primarily a driver of
decode time and therefore total response latency.

## Experiment 3 — Prompt size

Prompt size was increased while max_tokens remained fixed.

Results:

| Prompt size | Average TTFT | Average latency |
|---|---:|---:|
| Short | 0.031 s | 1.160 s |
| Medium | 0.039 s | 1.172 s |
| Long | 0.181 s | 1.318 s |
| Very long | 0.271 s | 1.508 s |

### Finding

Larger prompts significantly increased TTFT.

This is consistent with the model having to process more input
tokens before generation begins.

The experiment shows the difference between input processing
(prefill) and output generation (decode).

## Experiment 4 — Concurrency

The number of concurrent requests was increased.

Results:

| Concurrent requests | Average latency | Throughput |
|---|---:|---:|
| 1 | 1.112 s | 0.90 req/s |
| 2 | 1.670 s | 0.90 req/s |
| 4 | 3.052 s | 0.85 req/s |

### Finding

Higher concurrency increased latency without improving throughput
in the tested local configuration.

This indicates that the system reached a compute-capacity
bottleneck: additional concurrent requests mostly increased
waiting time instead of increasing completed requests per second.

## Experiment 5 — CPU threads

The same benchmark was repeated with different CPU thread settings.

Observed results:

| CPU threads | Average TTFT | Average latency | Generation speed |
|---|---:|---:|---:|
| 1 | 0.075 s | 5.130 s | 19.39 tokens/s |
| 2 | 0.052 s | 3.037 s | 32.83 tokens/s |
| 4 | 0.045 s | 2.374 s | 42.16 tokens/s |

### Finding

Increasing CPU threads improved generation speed and reduced
end-to-end latency.

The largest gain was observed when moving from one to two threads.

Performance continued improving at four threads, which matches
the four CPU cores reported by the test machine.

## Key findings

1. Output length is a major driver of total latency.

2. Prompt length primarily affects TTFT because the model must
   process the input before generation starts.

3. Generation throughput stabilizes around 43 tokens/s for longer
   outputs on the tested configuration.

4. Higher concurrency increases latency without improving request
   throughput once the available compute capacity is saturated.

5. CPU configuration has a significant impact on inference speed.

6. A single latency number is not sufficient to describe LLM
   performance. TTFT, generation speed, total latency and throughput
   describe different parts of system behavior.

## Limitations

This benchmark was executed on a local Intel-based MacBook Pro
using a small quantized model.

The results should therefore be interpreted as an analysis of
performance behavior rather than an estimate of production capacity.

The prompt-size experiment used qualitative prompt categories
rather than fixed token counts.

The concurrency experiment was executed on a single local
inference server without production batching or autoscaling.

## Possible next steps

For a production-oriented benchmark I would additionally evaluate:

- larger models and different quantization levels;
- GPU-based inference;
- fixed input-token buckets;
- P50 / P95 / P99 latency under load;
- batching behavior;
- memory usage;
- error rate and timeout rate;
- sustained load over longer periods;
- comparison of different serving configurations.
