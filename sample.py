"""
Sample from a trained model
"""
import os
import pickle
from contextlib import nullcontext
import torch
import tiktoken
from model import GPTConfig, GPT

# -----------------------------------------------------------------------------
init_from = 'resume'  # either 'resume' (from an out_dir) or a gpt2 variant
out_dir = 'out'  # ignored if init_from is not 'resume'
start = "\n"  # or "<|endoftext|>" or etc. Can also specify a file
num_samples = 10  # number of samples to draw
max_new_tokens = 500  # number of tokens generated in each sample
# 1.0 = no change, < 1.0 = less random, > 1.0 = more random in predictions
temperature = 0.8
# retain only the top_k most likely tokens, clamp others to 0 prob
top_k = 200
seed = 1337
device = 'cuda'  # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.
dtype = (
    'bfloat16' if torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    else 'float16'
)  # 'float32' or 'bfloat16' or 'float16'
compile = False  # use PyTorch 2.0 to compile the model to be faster
exec(open('configurator.py').read())  # overrides from command line or config file
# -----------------------------------------------------------------------------

torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
torch.backends.cuda.matmul.allow_tf32 = True  # allow tf32 on matmul
torch.backends.cudnn.allow_tf32 = True  # allow tf32 on cudnn
device_type = 'cuda' if 'cuda' in device else 'cpu'  # for torch.autocast
ptdtype = {
    'float32': torch.float32,
    'bfloat16': torch.bfloat16,
    'float16': torch.float16,
}[dtype]
try:
    from torch.amp.autocast_mode import autocast
    ctx = (
        nullcontext() if device_type == 'cpu'
        else autocast(device_type=device_type, dtype=ptdtype)
    )
except ImportError:
    ctx = (
        nullcontext() if device_type == 'cpu'
        else torch.cuda.amp.autocast(dtype=ptdtype)
    )

# model
if init_from == 'resume':
    # init from a model saved in a specific directory
    ckpt_path = os.path.join(out_dir, 'ckpt.pt')
    checkpoint = torch.load(ckpt_path, map_location=device)
    gptconf = GPTConfig(**checkpoint['model_args'])
    model = GPT(gptconf)
    state_dict = checkpoint['model']
    unwanted_prefix = '_orig_mod.'
    for k, v in list(state_dict.items()):
        if k.startswith(unwanted_prefix):
            state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
    model.load_state_dict(state_dict)
elif init_from.startswith('gpt2'):
    # init from a given GPT-2 model
    model = GPT.from_pretrained(init_from, dict(dropout=0.0))

model.eval()
model.to(device)
if compile:
    model = torch.compile(model)  # requires PyTorch 2.0 (optional)

# look for the meta pickle in case it is available in the dataset folder
load_meta = False
meta_path = None
if (
    init_from == 'resume' and 'config' in checkpoint and 'dataset' in checkpoint['config']
):
    meta_path = os.path.join('data', checkpoint['config']['dataset'], 'meta.pkl')
    load_meta = meta_path is not None and os.path.exists(meta_path)

# Define encode/decode functions globally
if load_meta and meta_path is not None:
    print(f"Loading meta from {meta_path}...")
    with open(meta_path, 'rb') as f:
        meta = pickle.load(f)
    stoi, itos = meta['stoi'], meta['itos']

    def _encode_fn(s):
        return [stoi[c] for c in s]

    def _decode_fn(indices):
        return "".join([itos[i] for i in indices])
else:
    print("No meta.pkl found, assuming GPT-2 encodings...")
    enc = tiktoken.get_encoding("gpt2")

    def _encode_fn(s):
        return enc.encode(s, allowed_special={"<|endoftext|>"})

    def _decode_fn(indices):
        return enc.decode(indices)

encode_fn = _encode_fn
decode_fn = _decode_fn

# encode the beginning of the prompt
if start.startswith('FILE:'):
    with open(start[5:], 'r', encoding='utf-8') as f:
        start = f.read()
start_ids = encode_fn(start)
x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])

# run generation
with torch.no_grad():
    with ctx:
        for k in range(num_samples):
            y = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
            print(decode_fn(y[0].tolist()))
            print('---------------')
