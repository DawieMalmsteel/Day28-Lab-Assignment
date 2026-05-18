# Colab Quickstart (Hybrid)

## Kết luận nhanh
- ✅ Dùng Colab để chạy **vLLM + embedding**
- ❌ Không chạy full `docker compose` ổn định trên Colab

## Kiến trúc đúng
- **Colab/Kaggle GPU:** model serving + embedding
- **Local machine:** Kafka, Prefect, Delta, Redis/Feast, Qdrant, API Gateway, Prometheus, Grafana

## Quy trình
1. Chạy cell vLLM trên Colab/Kaggle, lấy URL tunnel.
2. Chạy cell embedding service, lấy URL tunnel.
3. Local: `cp .env.example .env` và điền:
   - `VLLM_NGROK_URL=...`
   - `EMBED_NGROK_URL=...`
4. Local: `docker compose up -d`
5. Chạy scripts và smoke test:
   - `python scripts/01_ingest_to_kafka.py`
   - `python scripts/03_delta_to_feast.py`
   - `python scripts/05_embed_to_qdrant.py`
   - `pytest smoke-tests/ -v`
