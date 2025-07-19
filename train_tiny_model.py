import os
import pickle
import torch
import torch.nn as nn
import torch.optim as optim

# Parameters for tiny model
vocab_size = None  # to be set after reading data
block_size = 32
n_layer = 1
n_embd = 16
n_head = 1
num_epochs = 10

# Read dataset
with open('data/void/facts.txt', 'r', encoding='utf-8') as f:
    data = f.read()

# Build vocabulary
chars = sorted(list(set(data)))
vocab_size = len(chars)
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for i, ch in enumerate(chars)}

# Encode data
def encode(s):
    return [stoi[c] for c in s]

data_ix = torch.tensor(encode(data), dtype=torch.long)

# Simple dataset for next-char prediction
def get_batch(batch_size=16):
    ix = torch.randint(len(data_ix) - block_size, (batch_size,))
    x = torch.stack([data_ix[i:i+block_size] for i in ix])
    y = torch.stack([data_ix[i+1:i+block_size+1] for i in ix])
    return x, y

# Tiny model: single-layer GRU
class TinyRNN(nn.Module):
    def __init__(self, vocab_size, n_embd, block_size):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, n_embd)
        self.rnn = nn.GRU(n_embd, n_embd, batch_first=True)
        self.fc = nn.Linear(n_embd, vocab_size)
    def forward(self, x):
        x = self.embed(x)
        out, _ = self.rnn(x)
        logits = self.fc(out)
        return logits

model = TinyRNN(vocab_size, n_embd, block_size)
optimizer = optim.Adam(model.parameters(), lr=0.01)
loss_fn = nn.CrossEntropyLoss()

# Training loop
for epoch in range(num_epochs):
    x, y = get_batch()
    logits = model(x)
    loss = loss_fn(logits.view(-1, vocab_size), y.view(-1))
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    if (epoch+1) % 2 == 0:
        print(f"Epoch {epoch+1}/{num_epochs}, Loss: {loss.item():.4f}")

# Save model
os.makedirs('out', exist_ok=True)
torch.save(model.state_dict(), 'out/model.pt')

# Save vocab
os.makedirs('data/void', exist_ok=True)
with open('data/void/vocab.pkl', 'wb') as f:
    pickle.dump((chars, stoi), f)

# Save meta
meta = {
    'block_size': block_size,
    'n_layer': n_layer,
    'n_head': n_head,
    'n_embd': n_embd,
    'bias': True,
    'vocab_size': vocab_size,
    'model_type': 'TinyRNN'
}
with open('data/void/meta.pkl', 'wb') as f:
    pickle.dump(meta, f)

print("✓ Tiny model, vocab, and meta saved!")
