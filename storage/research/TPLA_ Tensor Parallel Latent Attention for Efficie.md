# TPLA: Tensor Parallel Latent Attention for Efficient Disaggregated Prefill and Decode Inference

## Resumen

Multi-Head Latent Attention (MLA), introduced in DeepSeek-V2, compresses key-value states into a low-rank latent vector, caching only this vector to reduce memory. In tensor parallelism (TP), however, attention heads are computed across multiple devices, and each device must load the full cache, ero...

## Enlaces

- **Ver en arXiv**: http://arxiv.org/abs/2508.15881v2
- **PDF descargado localmente**: TPLA_ Tensor Parallel Latent Attention for Efficie.pdf

---
*Guardado automáticamente desde arXiv*
