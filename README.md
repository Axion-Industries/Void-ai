# Void Z1
***NOTE:*** VERY IMPORTANT: THIS REPO IS ABANDONED, BUT WE JUST DECIDED TO MAKE IT PUBLIC SINCE IT SERVES NO PURPOSE TO USE ANYMORE, SINCE THE NEWEST VOID VERSON IS COMING OUT VERY SOON!!!

**NOTE:** For free-tier deployment (512MB RAM), all memory-intensive features (embedding memory, large models) are disabled. Only minimal GPT chat is available. If you need advanced features, upgrade your deployment resources.

Void Z1 is the first generative language model from Void AI. This project includes all scripts, model code, and deployment instructions for training, serving, and using the Z1 model.

The simplest, fastest repository for training/finetuning medium-sized GPTs. It is a rewrite of [minGPT](https://github.com/karpathy/minGPT) that prioritizes teeth over education. Still under active development, but currently the file `train.py` reproduces GPT-2 (124M) on OpenWebText, running on a single 8XA100 40GB node in about 4 days of training. The code itself is plain and readable: `train.py` is a ~300-line boilerplate training loop and `model.py` a ~300-line GPT model definition, which can optionally load the GPT-2 weights from OpenAI. That's it.

![repro124m](assets/gpt2_124M_loss.png)

Because the code is so simple, it is very easy to hack to your needs, train new models from scratch, or finetune pretrained checkpoints (e.g. biggest one currently available as a starting point would be the GPT-2 1.3B model from OpenAI).

## install

```
pip install torch numpy transformers datasets tiktoken wandb tqdm
```

Dependencies:

- [pytorch](https://pytorch.org) <3
- [numpy](https://numpy.org/install/) <3
- `transformers` for huggingface transformers <3 (to load GPT-2 checkpoints)
- `datasets` for huggingface datasets <3 (if you want to download + preprocess OpenWebText)
- `tiktoken` for OpenAI's fast BPE code <3
- `wandb` for optional logging <3
- `tqdm` for progress bars <3

